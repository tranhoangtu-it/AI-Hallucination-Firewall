# Codebase Summary — AI Hallucination Firewall

## Project Overview
AI Hallucination Firewall is a multi-layer code validation system that detects hallucinated APIs, wrong function signatures, nonexistent packages, and invalid code patterns in AI-generated content. It supports Python, JavaScript, and TypeScript with multiple delivery modes: CLI, REST API, pre-commit hooks, and VS Code extension.

## Core Architecture

### Entry Points
1. **CLI** (`cli.py`) — Click-based commands: `check` (files), `parse` (LLM markdown)
2. **API** (`server.py`) — FastAPI server for CI/CD integration
3. **Pre-commit Hooks** (`.pre-commit-hooks.yaml`) — Git integration for Python/JS
4. **VS Code Extension** (`vscode-extension/`) — Real-time diagnostics in IDE

### Validation Pipeline (4 Layers)
```
Input → Layer 1 (Syntax) → Layer 2 (Imports) → Layer 3 (Signatures) → Output
         tree-sitter        PyPI/npm registry   Jedi + inspect      Rich/JSON/Diagnostics
```

**Layer 1: Syntax Validation**
- Module: `pipeline/ast_validator.py`
- Parser: tree-sitter (multi-language AST)
- Detects: Syntax errors, malformed code
- Exit: Early exit on syntax errors (skip deeper checks)

**Layer 2: Import Verification**
- Module: `pipeline/import_checker.py`
- Registries: PyPI (Python), npm (JS/TS)
- Caching: SQLite with configurable TTL
- Detects: Nonexistent packages, invalid imports

**Layer 3: Signature Validation**
- Module: `pipeline/signature_checker.py` (NEW)
- Method: Jedi code intelligence + inspect fallback
- Caching: LRU cache (1024 items)
- Detects: Missing required args, unknown parameters, wrong signatures
- Scope: Python only, dotted names (e.g., `os.path.join()`)

### LLM Output Parsing (NEW)
- Module: `parsers/llm_output_parser.py`
- Input: Markdown text with code fences
- Extraction: Regex for ` ```lang\ncode\n``` ` blocks
- Language Detection: Heuristics (imports, keywords, JSON, SQL, etc.)
- Output: Validates each code block through standard pipeline
- CLI: `firewall parse [file|--stdin|--url URL]`

### Configuration
- **File:** `.firewall.toml` (TOML format)
- **Options:**
  - `languages`: List of languages to validate (python, javascript, typescript)
  - `severity_threshold`: Minimum severity level (error, warning, info)
  - `cache_ttl_seconds`: Cache expiration (default: 3600)
  - `fail_on_network_error`: Block commit on registry timeout (default: false)
  - `registries.pypi_enabled`: Enable PyPI checks (default: true)
  - `registries.npm_enabled`: Enable npm checks (default: true)
  - `registries.timeout_seconds`: HTTP timeout (default: 10)

### Data Models
**Core Models** (`models.py`):
- `ValidationIssue`: Issue severity, type, location, message, confidence
- `ValidationResult`: File validation result with issues list
- `IssueType`: Enum (SYNTAX_ERROR, NONEXISTENT_PACKAGE, WRONG_SIGNATURE, MISSING_REQUIRED_ARG, UNKNOWN_PARAMETER, etc.)
- `Severity`: Enum (ERROR, WARNING, INFO)
- `Language`: Enum (PYTHON, JAVASCRIPT, TYPESCRIPT)

**New Models**:
- `CodeBlock`: Extracted code block from markdown (language, code, line_number, block_index)
- `LLMValidationReport`: Aggregated results for LLM output (total_blocks, blocks_passed, blocks_failed)

### Key Dependencies
- `jedi>=0.19` — Code intelligence for signature lookup
- `tree-sitter>=0.23` — Multi-language AST parsing
- `tree-sitter-python>=0.23` — Python grammar
- `tree-sitter-javascript>=0.23` — JavaScript/TypeScript grammar
- `fastapi>=0.115` — REST API framework
- `uvicorn>=0.32` — ASGI server
- `pydantic>=2.0` — Data validation
- `httpx>=0.27` — Async HTTP client
- `click>=8.1` — CLI framework
- `rich>=13.0` — Terminal formatting

## Key Modules

### pipeline/signature_checker.py (NEW)
**Purpose:** Extract function calls from AST and validate against real signatures

**Classes:**
- `FunctionCallExtractor` — tree-sitter AST traversal to find call nodes
- `SignatureLookup` — Jedi + inspect for resolving signatures
- `SignatureValidator` — Compare call args against signature params
- `FunctionCall`, `SignatureInfo`, `ParamInfo` — Data structures

**Flow:**
1. Extract function calls: `func_name`, `positional_count`, `keywords`, has `*args/**kwargs`
2. Look up signature: Try Jedi first, fallback to inspect (stdlib only)
3. Validate: Check required args, param count, keyword names
4. Return: List of `ValidationIssue` with error/warning severity

### parsers/llm_output_parser.py (NEW)
**Purpose:** Parse markdown output from LLMs and validate code blocks

**Functions:**
- `extract_code_blocks()` — Regex extraction with language detection
- `_normalize_language()` — Map fence tags to canonical language names
- `detect_language_heuristic()` — Infer language from code content
- `validate_llm_output()` — Main entry point (async)

**Language Detection Heuristics:**
- JSON: Try json.loads()
- SQL: "SELECT", "INSERT", "UPDATE", "CREATE TABLE"
- Bash: Shebang (#!) or $ prompt
- XML/HTML: Starts with <
- Python: `import`, `from`, `def` keywords
- JavaScript: `function`, `const`, `let`, `=>` keywords

### reporters/ (Output Formatting)
- `terminal_reporter.py` — Rich tables/colors for CLI
- `json_reporter.py` — JSON serialization for CI/CD

### registries/ (Package Lookups)
- `pypi_registry.py` — PyPI JSON API client
- `npm_registry.py` — npm registry API client
- `cache.py` — SQLite cache with TTL

## File Structure
```
src/hallucination_firewall/
├── cli.py                        # Click CLI entry
├── server.py                     # FastAPI server
├── config.py                     # Config loader
├── models.py                     # Pydantic models
├── pipeline/
│   ├── runner.py                 # Pipeline orchestrator
│   ├── ast_validator.py          # Syntax validation
│   ├── import_checker.py         # Package checks
│   └── signature_checker.py      # Signature validation (NEW)
├── parsers/
│   ├── __init__.py
│   └── llm_output_parser.py      # LLM markdown parsing (NEW)
├── registries/
│   ├── pypi_registry.py
│   ├── npm_registry.py
│   └── cache.py
├── reporters/
│   ├── terminal_reporter.py
│   └── json_reporter.py
└── utils/
    └── language_detector.py

vscode-extension/                 # TypeScript VS Code extension
├── src/
│   ├── extension.ts              # Extension activation
│   ├── diagnostics-mapper.ts     # Map issues to VS Code diagnostics
│   └── validation-client.ts      # HTTP client + debouncing
├── package.json
└── tsconfig.json

docs/                             # Documentation
├── project-overview-pdr.md       # Project overview
├── system-architecture.md        # Architecture diagram
├── code-standards.md             # Code style & patterns
├── pre-commit-setup.md           # Hook installation
└── codebase-summary.md           # This file

.pre-commit-hooks.yaml            # Pre-commit definitions
pyproject.toml                    # Python package config
```

## Usage Patterns

### CLI
```bash
# Check files
firewall check mycode.py
firewall check src/*.py

# Check from stdin
echo "import fakelib" | firewall check --stdin -l python

# Parse LLM markdown
firewall parse response.md
curl ... | firewall parse --stdin
firewall parse --url https://gist.github.com/...

# JSON output
firewall check --format json mycode.py
```

### Pre-commit
```bash
# Install
pip install pre-commit
pre-commit install

# Hooks run on commit
# Or manually: pre-commit run firewall-check --all-files
```

### API Server
```bash
firewall serve --host 0.0.0.0 --port 8000

# Validate code
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"code": "import fakelib", "language": "python"}'
```

### VS Code Extension
- Install: Load from `vscode-extension/` directory
- Configuration: Settings → "Hallucination Firewall" trigger mode (onChange/onSave)
- Usage: Real-time red/yellow squiggles in editor + Problem Panel

## Testing
- Framework: pytest + pytest-asyncio
- Location: `tests/`
- Target: >80% coverage
- Approach: No network calls (mock registries)

## Design Decisions

1. **Fail Open:** Unknown functions get warnings, not hard errors
2. **LRU Caching:** Signature lookups cached (1024 items) to reduce Jedi overhead
3. **Safe Stdlib Only:** inspect fallback only for allowlisted stdlib modules (os, sys, json, etc.)
4. **Early Exit:** Syntax errors skip deeper validation for performance
5. **Debounced IDE Validation:** VS Code onChange mode uses debounce to reduce server load
6. **Language Heuristics:** LLM parser detects language from content when fence tag missing
7. **Pluggable Reporters:** Easy to add new output formats (e.g., SARIF)

## Recent Additions (v0.1.0)

- **Signature Checker:** Layer 3 validation with Jedi + inspect
- **LLM Output Parser:** Extract and validate code blocks from markdown
- **Pre-commit Hooks:** Integration with git pre-commit framework
- **VS Code Extension:** TypeScript extension with real-time diagnostics
- **New IssueTypes:** MISSING_REQUIRED_ARG, UNKNOWN_PARAMETER
- **New Models:** CodeBlock, LLMValidationReport

## Performance Characteristics

- **First Run:** ~2-3 seconds (cache warm-up)
- **Cached Run:** <500ms for typical file
- **Large Files:** Skipped if >5 MB (MAX_FILE_SIZE)
- **Signature Lookup:** Jedi cached (LRU 1024), inspect on stdlib only
- **LLM Parsing:** Limited to 100 blocks max, 10 MB input max

## Error Handling

- Network errors: Log warning, continue if `fail_on_network_error=false`
- Syntax errors: Early exit, skip deeper validation
- Unknown functions: Warn only (fail open)
- Large files: Skip validation, report skipped
- Invalid config: Raise Pydantic validation error

## Future Enhancements

- SARIF report format for GitHub/GitLab integration
- Interactive mode for signature prompting
- Custom deprecation rule files
- Multi-threaded validation for batch processing
- Pre-compiled cache for offline validation
