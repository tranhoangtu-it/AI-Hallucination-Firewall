# Phase 2: LLM Output Parser

## Context Links

- Research: [researcher-02-vscode-llm-parser.md](./research/researcher-02-vscode-llm-parser.md)
- CLI: `src/hallucination_firewall/cli.py`
- Runner: `src/hallucination_firewall/pipeline/runner.py`
- Models: `src/hallucination_firewall/models.py`

## Overview

**Priority:** P1
**Status:** Complete
**Effort:** 3h
**Goal:** Parse markdown code fences from LLM responses, extract multiple code blocks, validate each

LLM outputs often contain multiple code blocks in markdown format. This parser extracts all blocks, detects language, routes to validation pipeline, aggregates results.

## Key Insights

From research report:
- **Regex-based extraction:** Simple `r'```([^\n]*)\n(.*?)\n```'` pattern (zero dependencies)
- **Language detection:** Explicit fence tags (`python`, `javascript`) + heuristics (JSON parsing, SQL keywords)
- **Multi-block support:** Use `re.findall()` to capture all blocks in single response
- **Edge cases:** Nested backticks, code-in-comments, multi-file formats
- **No external libs:** Avoid `mistune`, use stdlib `re` module

## Requirements

### Functional Requirements

1. Extract code blocks from markdown fenced code (triple backticks)
2. Detect language from fence tag (e.g., `​```python`)
3. Support fallback heuristics for untagged blocks (JSON, SQL, shell)
4. Handle multiple code blocks in single response
5. Validate each block independently via existing pipeline
6. Aggregate results into single report

### Non-Functional Requirements

- **Performance:** <50ms to parse 100KB markdown (regex is fast)
- **Zero dependencies:** Use stdlib `re` module only
- **Robustness:** Handle malformed markdown gracefully
- **Compatibility:** Support ChatGPT, Claude, Copilot output formats

## Architecture

### Component Design

```
CLI (parse command)
    ↓
LLMOutputParser
    ├── extract_code_blocks(markdown) → list[CodeBlock]
    ├── detect_language(code, tag) → Language
    └── validate_blocks(blocks) → ValidationReport

CodeBlock
    ├── language: str
    ├── code: str
    ├── line_number: int
    └── block_index: int
```

### Data Flow

```
Markdown Input
    "Here's the code:\n```python\nimport os\n```"
        ↓
extract_code_blocks()
    [CodeBlock(language="python", code="import os", line=2, index=0)]
        ↓
ValidationPipeline.validate_code() (per block)
    [ValidationResult(file="<block-0>", issues=[], passed=True)]
        ↓
Aggregate Results
    LLMValidationReport(blocks=1, passed=1, failed=0, issues=[])
```

### Integration Point

New CLI command in `cli.py`:

```python
@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", "output_format", type=click.Choice(["terminal", "json"]), default="terminal")
def parse(file: str, output_format: str) -> None:
    """Parse and validate code blocks from LLM markdown output."""
    # Read markdown file, extract blocks, validate each
```

## Related Code Files

### Files to Create

- `src/hallucination_firewall/parsers/__init__.py` (empty)
- `src/hallucination_firewall/parsers/llm_output_parser.py` (120 lines)
  - `CodeBlock` dataclass
  - `LLMValidationReport` dataclass
  - `extract_code_blocks()` function
  - `detect_language_heuristic()` function
  - `validate_llm_output()` async function (entry point)

### Files to Modify

- `src/hallucination_firewall/cli.py` (add `parse` command)
- `src/hallucination_firewall/models.py` (add `LLMValidationReport` model)

### Files to Read

- `src/hallucination_firewall/utils/language_detector.py` (language detection patterns reference)
- `src/hallucination_firewall/reporters/terminal_reporter.py` (output formatting reference)

## Implementation Steps

### Step 1: Create Parser Module Structure (5min)

```bash
mkdir -p src/hallucination_firewall/parsers
touch src/hallucination_firewall/parsers/__init__.py
```

### Step 2: Define Data Models (15min)

In `models.py`, add:

```python
from dataclasses import dataclass

@dataclass
class CodeBlock:
    """A single code block extracted from LLM output."""
    language: str
    code: str
    line_number: int  # Line in original markdown
    block_index: int  # 0-indexed block number
    raw_tag: str = ""  # Original fence tag

class LLMValidationReport(BaseModel):
    """Aggregated validation results from LLM output."""
    total_blocks: int
    blocks_passed: int
    blocks_failed: int
    results: list[ValidationResult]

    @property
    def passed(self) -> bool:
        return self.blocks_failed == 0
```

### Step 3: Implement Block Extraction (45min)

File: `src/hallucination_firewall/parsers/llm_output_parser.py`

```python
from __future__ import annotations

import re
from dataclasses import dataclass

from ..models import CodeBlock, Language

# Regex pattern for fenced code blocks
CODE_FENCE_PATTERN = r'```([^\n]*)\n(.*?)```'

def extract_code_blocks(markdown: str) -> list[CodeBlock]:
    """Extract all code blocks from markdown text."""
    pattern = re.compile(CODE_FENCE_PATTERN, re.DOTALL)
    blocks = []

    for index, match in enumerate(pattern.finditer(markdown)):
        tag = match.group(1).strip()
        code = match.group(2).strip()
        line_number = markdown[:match.start()].count('\n') + 1

        language = tag if tag else detect_language_heuristic(code)

        blocks.append(CodeBlock(
            language=language,
            code=code,
            line_number=line_number,
            block_index=index,
            raw_tag=tag,
        ))

    return blocks
```

**Structure:**
- Compile regex once at module level
- Use `finditer()` to get match positions for line numbers
- Support empty tags (untagged blocks)

### Step 4: Implement Language Detection Heuristics (30min)

```python
import json

def detect_language_heuristic(code: str) -> str:
    """Detect language from code content using heuristics."""
    # Try JSON parse
    try:
        json.loads(code)
        return "json"
    except (json.JSONDecodeError, ValueError):
        pass

    # Check for SQL keywords
    sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP"]
    if any(kw in code.upper()[:100] for kw in sql_keywords):
        return "sql"

    # Check for shell patterns
    if code.startswith("#!") or code.lstrip().startswith("$ "):
        return "bash"

    # Check for XML/HTML
    if code.lstrip().startswith("<") and ">" in code:
        return "xml"

    # Check for Python imports
    if "import " in code[:200] or "from " in code[:200]:
        return "python"

    # Check for JS/TS patterns
    if any(kw in code[:200] for kw in ["function", "const ", "let ", "var "]):
        return "javascript"

    return "text"  # Default fallback
```

**Heuristics priority:**
1. JSON parsing (most reliable)
2. SQL keywords (high signal)
3. Shebang or shell prompt
4. XML/HTML tags
5. Python imports
6. JavaScript keywords
7. Fallback to "text"

### Step 5: Implement Validation Entry Point (45min)

```python
from ..pipeline.runner import ValidationPipeline
from ..models import LLMValidationReport, ValidationResult

async def validate_llm_output(
    markdown: str,
    config=None,
) -> LLMValidationReport:
    """Parse LLM markdown output and validate all code blocks."""
    blocks = extract_code_blocks(markdown)

    if not blocks:
        return LLMValidationReport(
            total_blocks=0,
            blocks_passed=0,
            blocks_failed=0,
            results=[],
        )

    pipeline = ValidationPipeline(config)
    results = []

    try:
        for block in blocks:
            # Validate each block with synthetic filename
            file_name = f"<llm-block-{block.block_index}>.{block.language}"
            result = await pipeline.validate_code(block.code, file_name)
            results.append(result)
    finally:
        await pipeline.close()

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    return LLMValidationReport(
        total_blocks=len(blocks),
        blocks_passed=passed,
        blocks_failed=failed,
        results=results,
    )
```

### Step 6: Add CLI Command (30min)

In `cli.py`, add new command:

```python
@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--format", "output_format",
    type=click.Choice(["terminal", "json"]), default="terminal",
)
def parse(file: str, output_format: str) -> None:
    """Parse and validate code blocks from LLM markdown output.

    Example:
        firewall parse llm_response.md
        firewall parse --format json output.md
    """
    from pathlib import Path
    from .parsers.llm_output_parser import validate_llm_output

    markdown = Path(file).read_text(encoding="utf-8")
    report = asyncio.run(validate_llm_output(markdown))

    if output_format == "json":
        print_json([report])
    else:
        console.print(f"\n[bold]LLM Output Validation Report[/]")
        console.print(f"Total blocks: {report.total_blocks}")
        console.print(f"Passed: [green]{report.blocks_passed}[/]")
        console.print(f"Failed: [red]{report.blocks_failed}[/]\n")

        for result in report.results:
            print_result(result, console)

    if not report.passed:
        sys.exit(1)
```

### Step 7: Write Tests (60min)

File: `tests/parsers/test_llm_output_parser.py`

Test cases:
- [ ] Extract single code block with language tag
- [ ] Extract multiple blocks from one response
- [ ] Handle untagged blocks with heuristics
- [ ] Detect Python from imports
- [ ] Detect JavaScript from keywords
- [ ] Detect JSON from valid JSON
- [ ] Detect SQL from keywords
- [ ] Handle nested backticks (edge case)
- [ ] Handle empty code blocks
- [ ] Handle markdown without code blocks
- [ ] Integration: validate real ChatGPT response
- [ ] Integration: validate real Claude response

Sample test data:

```python
SAMPLE_LLM_OUTPUT = """
Here's the implementation:

```python
import requests

def fetch_data():
    response = requests.get("https://api.example.com")
    return response.json()
```

And the test:

```python
def test_fetch():
    assert fetch_data() is not None
```
"""
```

### Step 8: Manual Testing (15min)

Create test markdown file `test_llm_response.md`:

```markdown
# ChatGPT Response

Here's the code:

​```python
import fakelib  # Should error
import requests  # Should pass

def hello():
    requests.get()  # Should error (missing url)
​```

And some JavaScript:

​```javascript
const axios = require('axios');
axios.get('https://api.example.com');
​```
```

Run: `firewall parse test_llm_response.md`

Expected output:
- 2 blocks found
- Block 0 (Python): 2 errors (fakelib, requests.get missing url)
- Block 1 (JavaScript): 0 errors
- Overall: Failed

## Todo List

- [ ] Create `parsers/` package directory
- [ ] Add `CodeBlock` and `LLMValidationReport` to `models.py`
- [ ] Create `llm_output_parser.py` module
- [ ] Implement `extract_code_blocks()` with regex
- [ ] Implement `detect_language_heuristic()` function
- [ ] Implement `validate_llm_output()` entry point
- [ ] Add `parse` command to CLI
- [ ] Write unit tests for extraction logic
- [ ] Write unit tests for heuristic detection
- [ ] Write integration tests with real LLM outputs
- [ ] Collect 20 real ChatGPT/Claude responses for testing
- [ ] Manual testing with multi-block markdown
- [ ] Update README with `parse` command examples
- [ ] Add example LLM responses to docs

## Success Criteria

### Functional

- [ ] Extracts 100% of code blocks from well-formed markdown
- [ ] Correctly detects language from fence tags
- [ ] Heuristics detect Python/JavaScript/JSON with 90% accuracy
- [ ] Validates each block independently
- [ ] Aggregates results correctly (passed/failed counts)

### Performance

- [ ] <50ms to parse 100KB markdown (typical LLM response)
- [ ] Zero memory leaks on large files (10MB markdown)

### Code Quality

- [ ] 95% test coverage on llm_output_parser.py
- [ ] Type hints on all functions
- [ ] Ruff linting passes
- [ ] MyPy type checking passes

## Risk Assessment

### Potential Issues

1. **Regex fails on nested/escaped backticks**
   - **Mitigation:** Test with 100 real LLM outputs; document known limitations
   - **Fallback:** Users can manually extract problematic blocks

2. **False language detection for untagged blocks**
   - **Mitigation:** Fail-open; default to "text" if unsure
   - **User workaround:** Add explicit language tags when using `parse`

3. **LLM outputs non-standard markdown**
   - **Mitigation:** Collect edge cases; add special handling
   - **Example:** Copilot uses `// filename: app.js` headers

4. **Large responses timeout**
   - **Mitigation:** Stream validation results; don't wait for all blocks
   - **Future:** Add `--max-blocks` flag

## Security Considerations

### Input Validation

- **File size limit:** 10MB max for markdown input (prevent DoS)
- **Block count limit:** 100 blocks max per file (prevent regex DoS)
- **Code size limit:** Reuse existing 5MB limit per code block

### Code Execution

- **No eval/exec:** Regex-only parsing, no code execution
- **Validation safety:** Delegate to existing pipeline (same security model)

## Next Steps

After Phase 2 completion:

1. **Phase 3:** Create pre-commit hook using `parse` command
2. **Documentation:** Add examples of piping LLM API responses to `firewall parse`
3. **CI/CD integration:** Document using `parse` in GitHub Actions
4. **Real-world testing:** Collect 100 production LLM outputs for edge case testing

## Stdin and URL Input Support (Added from Validation Session 1)
<!-- Updated: Validation Session 1 - Add stdin + URL input -->

**CLI command updates:**
```bash
# File input (existing)
firewall parse response.md

# Stdin pipe (NEW)
curl -s https://api.openai.com/... | firewall parse --stdin

# URL fetch (NEW)
firewall parse --url https://gist.githubusercontent.com/.../response.md
```

**Implementation:**
- Add `--stdin` flag: read from `sys.stdin` (same pattern as `firewall check --stdin`)
- Add `--url` flag: fetch content with `httpx` (async, reuse existing client pattern)
- URL fetch: 10s timeout, 10MB max, HTTPS only
- Add to `cli.py` parse command options

**Effort increase:** +1h (total phase: ~4h)

## Unresolved Questions

1. **Multi-file format support:** Should we parse `## filename.py` headers? → Yes, add in v2 if users request
2. **Streaming validation:** Validate blocks as parsed or batch? → Batch for v1 (simpler)
3. **Interactive mode:** Ask user to fix blocks one-by-one? → No, batch report only
4. **Output format:** Should JSON include original markdown blocks? → Yes, include `code` field in results
