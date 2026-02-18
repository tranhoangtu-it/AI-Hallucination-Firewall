# Phase 3: Validation Pipeline

## Context
- [Plan Overview](./plan.md)
- [Phase 2: Models & Config](./phase-02-core-models-and-config.md)
- [Research: Code Validation](../reports/researcher-260218-0207-code-validation-approaches.md)
- [Research: Hallucination Patterns](../reports/researcher-260218-0207-hallucination-detection-patterns.md)

## Overview
- **Priority:** P1 (core feature)
- **Status:** pending
- **Effort:** 8h
- **Depends on:** Phase 2 (models must exist)
- **Description:** Implement 4-layer validation pipeline: AST → imports → signatures → deprecation.

## Key Insights
- Layered approach: AST catches 30%, imports 40%, signatures 20%, deprecation 10%
- Fail-open philosophy: unknown → warning, confirmed bad → error
- Async pipeline: registry lookups run concurrently
- tree-sitter gives concrete syntax trees, not abstract — node types vary per grammar

## Requirements
- **Functional:** Parse code, detect hallucinated imports/methods/params, return Issue list
- **Non-functional:** <1s for typical file (excluding network), cache registry responses

## Architecture

```
runner.py (orchestrator)
    ├── ast_validator.py        Layer 1: syntax + undefined refs
    ├── import_checker.py       Layer 2: package existence (PyPI/npm)
    ├── signature_validator.py  Layer 3: method signature matching
    └── deprecation_checker.py  Layer 4: deprecated API database

registries/
    ├── pypi_registry.py        async PyPI JSON API client
    ├── npm_registry.py         async npm registry client
    └── cache.py                SQLite cache with TTL
```

## Related Code Files
- **Create:** `pipeline/runner.py`, `pipeline/ast_validator.py`, `pipeline/import_checker.py`, `pipeline/signature_validator.py`, `pipeline/deprecation_checker.py`
- **Create:** `registries/pypi_registry.py`, `registries/npm_registry.py`, `registries/cache.py`
- **Create:** `data/deprecations/python.json`

## Implementation Steps

### 3.1 Pipeline Runner (`pipeline/runner.py`)

```python
class PipelineRunner:
    def __init__(self, config: FirewallConfig):
        self.config = config
        self.validators: list[Validator] = []

    def register(self, validator: Validator) -> None:
        self.validators.append(validator)

    async def run(self, code: str, language: str, file_path: str) -> ValidationResult:
        """Run all validators sequentially, collect issues."""
        issues: list[Issue] = []
        start = time.perf_counter()
        for validator in self.validators:
            result = await validator.validate(code, language, file_path)
            issues.extend(result)
        duration = (time.perf_counter() - start) * 1000
        return ValidationResult(file_path=file_path, language=language,
                                issues=issues, duration_ms=duration)
```

Factory function `create_pipeline(config)` builds runner with all validators registered.

### 3.2 AST Validator (`pipeline/ast_validator.py`)

1. Initialize tree-sitter parser for target language
2. Parse code into syntax tree
3. Walk tree for ERROR nodes → report as syntax errors
4. Extract all function/method call nodes → collect names for downstream validation
5. Return `list[Issue]` for syntax errors

Key: Use `tree_sitter.Language` and `tree_sitter.Parser`. Load grammars dynamically based on language config.

### 3.3 Import Checker (`pipeline/import_checker.py`)

1. Extract import statements from AST (or regex fallback for speed)
2. For Python: parse `import X` and `from X import Y`
3. Check against stdlib list first (use `sys.stdlib_module_names` on 3.10+)
4. Query PyPI registry for non-stdlib packages
5. For JS: parse `import ... from 'X'` and `require('X')`
6. Query npm registry for packages
7. Return issues for packages not found on any registry

### 3.4 Signature Validator (`pipeline/signature_validator.py`)

1. For Python: attempt `importlib.import_module()` on installed packages
2. Use `inspect.signature()` to get real signatures
3. Compare call-site arguments (from AST) against real signature
4. Flag: wrong param names, too many args, nonexistent methods on objects
5. Return issues with suggestions (closest matching method via difflib)

### 3.5 Deprecation Checker (`pipeline/deprecation_checker.py`)

1. Load deprecation database from `data/deprecations/python.json`
2. Structure: `{"module.function": {"deprecated_in": "3.10", "removed_in": "3.12", "replacement": "new.function"}}`
3. Match imports and function calls against database
4. Return warning-level issues with replacement suggestions

### 3.6 Registry Clients (`registries/`)

**PyPI (`pypi_registry.py`):**
```python
class PyPIRegistry:
    BASE_URL = "https://pypi.org/pypi"

    async def package_exists(self, name: str) -> bool:
        """Check if package exists on PyPI."""
        # GET https://pypi.org/pypi/{name}/json → 200 or 404

    async def get_package_info(self, name: str) -> PackageInfo | None:
        """Fetch package metadata (version, description)."""
```

**npm (`npm_registry.py`):** Same pattern, `https://registry.npmjs.org/{name}`

**Cache (`cache.py`):**
- SQLite via `aiosqlite`
- Table: `cache(key TEXT PRIMARY KEY, value TEXT, expires_at REAL)`
- `async get(key) -> str | None` — returns None if expired
- `async set(key, value, ttl)` — insert/replace with expiry

### 3.7 Deprecation Data (`data/deprecations/python.json`)

Seed with ~20 common deprecated Python APIs:
- `imp` module (use `importlib`)
- `asyncio.get_event_loop()` pattern
- `collections.MutableMapping` (use `collections.abc`)
- `typing.Optional` patterns that changed
- `distutils` (removed in 3.12)
- `unittest.makeSuite` (deprecated 3.8)

## Todo List
- [ ] Implement PipelineRunner with create_pipeline() factory
- [ ] Implement ASTValidator with tree-sitter integration
- [ ] Implement ImportChecker with stdlib detection + registry lookup
- [ ] Implement SignatureValidator with inspect-based checking
- [ ] Implement DeprecationChecker with JSON database
- [ ] Implement PyPIRegistry async client
- [ ] Implement NpmRegistry async client
- [ ] Implement SQLite cache with TTL
- [ ] Create python.json deprecation database (20+ entries)
- [ ] Wire all validators into create_pipeline()

## Success Criteria
- Pipeline processes a Python file with hallucinated imports and returns correct issues
- AST validator catches syntax errors in malformed code
- Import checker correctly identifies nonexistent PyPI packages
- Signature validator flags wrong parameters on stdlib functions
- Deprecation checker flags `import imp` as deprecated
- Cache stores and retrieves registry responses correctly
- Full pipeline runs in <1s for a 100-line file (excluding first network call)

## Risk Assessment
- tree-sitter API changed in v0.21+ (new binding style) → pin version, test during setup
- PyPI rate limiting → cache aggressively, respect 429 responses with backoff
- `importlib.import_module()` can execute code → only use for stdlib/trusted packages, never for user input
- Signature checking won't work for packages not installed locally → return "unknown" status, not error
