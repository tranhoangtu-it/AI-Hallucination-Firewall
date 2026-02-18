# Phase 1: Signature Validation (Layer 3)

## Context Links

- Research: [researcher-01-signature-precommit.md](./research/researcher-01-signature-precommit.md)
- Current Runner: `src/hallucination_firewall/pipeline/runner.py`
- AST Validator: `src/hallucination_firewall/pipeline/ast_validator.py`
- Models: `src/hallucination_firewall/models.py`

## Overview

**Priority:** P1 (Highest)
**Status:** Complete
**Effort:** 6h
**Goal:** Complete Layer 3 validation by checking function calls against real signatures

Layer 3 validates that function calls use correct parameters, types, and keywords. Catches hallucinated method names, wrong parameter counts, incorrect keyword arguments.

## Key Insights

From research report:
- **tree-sitter extraction:** Use S-expression queries `(call function: (identifier) @fn arguments: (argument_list) @args)` to handle malformed code gracefully
- **Signature lookup priority:** Jedi (fast, 1000+ packages) → typeshed stubs → `inspect.signature()` fallback
- **Validation checks:** Arg count (arity), keyword names, positional vs keyword, basic type hints
- **Performance:** LRU cache signature lookups; target <100ms per file

## Requirements

### Functional Requirements

1. Extract function calls from AST (Python: `requests.get()`, `os.path.join()`)
2. Lookup correct signatures from installed packages + stdlib
3. Validate call-site arguments against signature
4. Report errors: wrong param names, missing required args, extra args, wrong types
5. Support both stdlib and PyPI packages

### Non-Functional Requirements

- **Performance:** <100ms for typical file (10-20 function calls)
- **Accuracy:** 90% on stdlib + top 100 PyPI packages
- **Fail-open:** Unknown packages/signatures → skip with INFO severity
- **Cache:** LRU cache for signature lookups (1000 entries, 1h TTL)

## Architecture

### Component Design

```
ValidationPipeline (runner.py)
    ↓
SignatureChecker (new)
    ├── FunctionCallExtractor (tree-sitter queries)
    ├── SignatureLookup (Jedi + typeshed + inspect)
    └── SignatureValidator (compare args vs params)
```

### Data Flow

```
Code → tree-sitter AST → Extract calls → Lookup signature → Compare → Issue
  "requests.get(url, timeout)"
         ↓
  Call(func="requests.get", args=["url", "timeout"])
         ↓
  Signature(params=["url", timeout=None, ...])
         ↓
  Validation(missing_required=[], wrong_keywords=[])
```

### Integration Point

In `runner.py` after Layer 2 (import check):

```python
# Layer 2: Import/package existence check
imports = extract_imports(code, language)
# ... existing import checking ...

# Layer 3: Signature validation (NEW)
if language == Language.PYTHON:
    signature_issues = await check_signatures(code, language, file_path, self.pypi)
    result.issues.extend(signature_issues)
```

## Related Code Files

### Files to Create

- `src/hallucination_firewall/pipeline/signature_checker.py` (150 lines)
  - `FunctionCallExtractor` class
  - `SignatureLookup` class (Jedi wrapper)
  - `check_signatures()` async function (entry point)
  - LRU cache decorator for lookups

### Files to Modify

- `src/hallucination_firewall/pipeline/runner.py` (add Layer 3 call in `validate_code()`)
- `src/hallucination_firewall/models.py` (add `WRONG_SIGNATURE`, `WRONG_PARAMETER` to `IssueType`)
- `pyproject.toml` (add `jedi>=0.19` dependency)

### Files to Read

- `src/hallucination_firewall/pipeline/ast_validator.py` (tree-sitter patterns reference)
- `src/hallucination_firewall/registries/cache.py` (SQLite cache patterns)

## Implementation Steps

### Step 1: Add Dependencies (5min)

Update `pyproject.toml`:

```toml
dependencies = [
    # ... existing ...
    "jedi>=0.19",
]
```

Run: `pip install -e ".[dev]"`

### Step 2: Update Models (10min)

In `models.py`, add to `IssueType` enum:

```python
class IssueType(str, Enum):
    # ... existing ...
    WRONG_SIGNATURE = "wrong_signature"
    MISSING_REQUIRED_ARG = "missing_required_arg"
    UNKNOWN_PARAMETER = "unknown_parameter"
```

### Step 3: Create FunctionCallExtractor (60min)

File: `src/hallucination_firewall/pipeline/signature_checker.py`

```python
from __future__ import annotations

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query

from ..models import Language as LangEnum

PY_LANGUAGE = Language(tspython.language())

# S-expression query for function calls
CALL_QUERY = """
(call
  function: (attribute) @func_attr
  arguments: (argument_list) @args)

(call
  function: (identifier) @func_id
  arguments: (argument_list) @args)
"""

class FunctionCallExtractor:
    """Extract function calls from tree-sitter AST."""

    def __init__(self):
        self.parser = Parser(PY_LANGUAGE)
        self.query = Query(PY_LANGUAGE, CALL_QUERY)

    def extract_calls(self, code: str) -> list[FunctionCall]:
        """Extract all function calls from code."""
        tree = self.parser.parse(bytes(code, "utf8"))
        captures = self.query.captures(tree.root_node)

        calls = []
        for node, capture_name in captures:
            if capture_name in ("func_attr", "func_id"):
                func_name = self._get_function_name(node)
                args = self._extract_arguments(node.parent)
                calls.append(FunctionCall(name=func_name, args=args, line=node.start_point[0]))
        return calls
```

**Structure:**
- `FunctionCall` dataclass (name, args, kwargs, line)
- `extract_calls()` returns list of calls
- `_get_function_name()` handles both `requests.get` and `get`
- `_extract_arguments()` parses positional + keyword args

### Step 4: Create SignatureLookup (90min)

In same file:

```python
from functools import lru_cache
import inspect
import jedi

class SignatureLookup:
    """Lookup function signatures using Jedi + inspect fallback."""

    @lru_cache(maxsize=1000)
    def get_signature(self, func_name: str, code: str, line: int) -> Signature | None:
        """Get signature for function at given location."""
        # Try Jedi first (handles stdlib + installed packages)
        try:
            script = jedi.Script(code)
            completions = script.goto(line + 1, 0, follow_imports=True)
            if completions:
                sig = completions[0].get_signatures()
                if sig:
                    return self._jedi_to_signature(sig[0])
        except Exception:
            pass

        # Fallback: inspect for installed packages
        try:
            module_name, func = func_name.rsplit(".", 1)
            mod = __import__(module_name, fromlist=[func])
            obj = getattr(mod, func)
            return self._inspect_to_signature(inspect.signature(obj))
        except Exception:
            return None
```

**Structure:**
- `Signature` dataclass (params: list[Parameter])
- `Parameter` dataclass (name, required, kind, type_hint)
- `get_signature()` with LRU cache
- `_jedi_to_signature()` converter
- `_inspect_to_signature()` converter

### Step 5: Create SignatureValidator (60min)

```python
class SignatureValidator:
    """Compare function call args against signature params."""

    def validate(self, call: FunctionCall, signature: Signature) -> list[str]:
        """Return list of validation errors."""
        errors = []

        # Check required params present
        required = [p for p in signature.params if p.required]
        provided = set(call.args + list(call.kwargs.keys()))
        for param in required:
            if param.name not in provided:
                errors.append(f"Missing required parameter: {param.name}")

        # Check unknown keyword args
        known_params = {p.name for p in signature.params}
        for kwarg in call.kwargs:
            if kwarg not in known_params:
                errors.append(f"Unknown parameter: {kwarg}")

        return errors
```

### Step 6: Create Entry Point Function (30min)

```python
async def check_signatures(
    code: str,
    language: LangEnum,
    file_path: str,
    registry,
) -> list[ValidationIssue]:
    """Check all function signatures in code."""
    if language != LangEnum.PYTHON:
        return []  # Only Python supported for now

    extractor = FunctionCallExtractor()
    lookup = SignatureLookup()
    validator = SignatureValidator()

    calls = extractor.extract_calls(code)
    issues = []

    for call in calls:
        signature = lookup.get_signature(call.name, code, call.line)
        if not signature:
            continue  # Fail-open: skip unknown functions

        errors = validator.validate(call, signature)
        for error in errors:
            issues.append(ValidationIssue(
                severity=Severity.ERROR,
                issue_type=IssueType.WRONG_SIGNATURE,
                location=SourceLocation(file=file_path, line=call.line + 1),
                message=f"{call.name}(): {error}",
                source="signature_checker",
            ))

    return issues
```

### Step 7: Integrate into Runner (15min)

In `runner.py`, update `validate_code()`:

```python
from .signature_checker import check_signatures

# ... inside validate_code() ...

# Layer 2: Import/package existence check
imports = extract_imports(code, language)
if language == Language.PYTHON:
    import_issues = await check_python_imports(imports, file_path, self.pypi)

    # Layer 3: Signature validation (NEW)
    signature_issues = await check_signatures(code, language, file_path, self.pypi)
    result.issues.extend(signature_issues)
elif language in (Language.JAVASCRIPT, Language.TYPESCRIPT):
    import_issues = await check_js_imports(imports, file_path, self.npm)
```

### Step 8: Write Tests (120min)

File: `tests/pipeline/test_signature_checker.py`

Test cases:
- [ ] Extract simple function calls (`print()`, `len()`)
- [ ] Extract attribute calls (`requests.get()`)
- [ ] Extract nested calls (`json.dumps(data)`)
- [ ] Validate stdlib signatures (`open(file, mode)`)
- [ ] Detect missing required args (`open()` without filename)
- [ ] Detect unknown kwargs (`requests.get(fake_param=1)`)
- [ ] Cache hits for repeated lookups
- [ ] Fail-open for unknown functions (no error)
- [ ] Handle malformed code gracefully

### Step 9: Manual Testing (30min)

Create test files:

```python
# test_signature_valid.py
import requests
response = requests.get("https://api.example.com", timeout=10)

# test_signature_invalid.py
import requests
response = requests.get(fake_param="value")  # Should error
response = requests.get()  # Should error (missing url)
```

Run: `firewall check test_signature_*.py`

## Todo List

- [ ] Add `jedi>=0.19` to `pyproject.toml` dependencies
- [ ] Update `IssueType` enum in `models.py` with signature-related types
- [ ] Create `signature_checker.py` module
- [ ] Implement `FunctionCallExtractor` class with tree-sitter queries
- [ ] Implement `SignatureLookup` class with Jedi integration
- [ ] Implement `SignatureValidator` class with arg comparison logic
- [ ] Create `check_signatures()` entry point function
- [ ] Add LRU cache decorator to signature lookups
- [ ] Integrate into `runner.py` as Layer 3
- [ ] Write unit tests for extractor, lookup, validator
- [ ] Write integration tests with real stdlib + PyPI packages
- [ ] Manual testing with valid/invalid signatures
- [ ] Performance profiling (target <100ms per file)
- [ ] Update README with Layer 3 documentation

## Success Criteria

### Functional

- [ ] Detects missing required parameters in function calls
- [ ] Detects unknown keyword arguments
- [ ] Works with stdlib functions (`open`, `print`, `json.dumps`)
- [ ] Works with PyPI packages (`requests.get`, `flask.Flask`)
- [ ] Gracefully skips unknown functions (fail-open)

### Performance

- [ ] <100ms validation time for file with 20 function calls
- [ ] LRU cache reduces lookup time by 80% on repeated calls
- [ ] Zero crashes on malformed code

### Code Quality

- [ ] 90% test coverage on signature_checker.py
- [ ] Type hints on all functions
- [ ] Ruff linting passes
- [ ] MyPy type checking passes

## Risk Assessment

### Potential Issues

1. **Jedi performance slow on large files**
   - **Mitigation:** LRU cache + timeout on Jedi calls (500ms max)
   - **Fallback:** Skip signature validation if timeout

2. **False positives on dynamic Python code**
   - **Mitigation:** Fail-open strategy; only report high-confidence issues
   - **Example:** Skip calls with `*args`, `**kwargs` unpacking

3. **Typeshed stubs outdated**
   - **Mitigation:** Pin Jedi version; document stub update process
   - **Fallback:** Use `inspect.signature()` for installed packages

4. **Memory usage for LRU cache**
   - **Mitigation:** 1000-entry limit; clear cache after each file
   - **Monitoring:** Log cache hit rate in debug mode

## Security Considerations

### Code Execution Risk

- **Concern:** Jedi may execute code during introspection
- **Mitigation:** Run Jedi in isolated environment (no change from current AST validation)
- **Note:** `inspect.signature()` requires package installed (same risk as import checker)

### Input Validation

- **Validate code size:** Reuse existing 5MB limit from `runner.py`
- **Sanitize function names:** Use tree-sitter parsed names only (no eval/exec)
- **Timeout protection:** 500ms max per Jedi lookup

## Next Steps

After Phase 1 completion:

1. **Phase 2:** Create LLM output parser to extract code blocks from markdown
2. **Documentation:** Update README with Layer 3 examples
3. **Performance tuning:** Profile cache hit rates, optimize slow lookups
4. **JavaScript support:** Extend signature checking to TypeScript/JavaScript (future)

## JavaScript Signature Validation (Added from Validation Session 1)
<!-- Updated: Validation Session 1 - Add basic JS signature checking -->

**Scope:** Basic JS/TS signature checking using TypeScript Compiler API or `typescript` npm package via subprocess.

**Approach:**
- Use `typescript` package to extract function signatures from `.d.ts` type declaration files
- Focus on popular packages: `express`, `axios`, `lodash`, `react`
- Run as subprocess: `node scripts/ts-signature-lookup.js <func_name>`
- Cache results in SQLite (same as Python signatures)

**Files to create:**
- `scripts/ts-signature-lookup.js` (Node.js script for TS type queries)
- Update `signature_checker.py` to dispatch to JS checker for JS/TS files

**Effort increase:** +2h (total phase: ~8h)

## Unresolved Questions

1. **Jedi cache freshness:** Cache full Jedi Script objects or just signature results? → Cache signature results (smaller memory footprint)
2. **Typeshed version:** Pin or use latest? → Pin to Jedi's bundled version for stability
3. **Partial signatures:** How to handle functions with `*args/**kwargs`? → Skip validation (fail-open)
4. **Performance target:** 100ms acceptable for CLI? → Yes, pre-commit hook caches results
5. **JS type declarations:** Require user to have `@types/*` packages installed? → Yes for v1, auto-fetch in v2
