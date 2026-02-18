# AI Hallucination Firewall

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/tranhoangtu-it/AI-Hallucination-Firewall/releases)
[![Tests](https://img.shields.io/badge/tests-68%20passed-brightgreen.svg)](#development)

A verification proxy that validates AI-generated code before it enters your codebase. Acts as a **"type checker for AI output"** — detects hallucinated functions, deprecated usage, invalid patterns, wrong signatures, and nonexistent packages.

## Features

- **AST Syntax Validation** — Catches syntax errors using tree-sitter (Python, JavaScript, TypeScript)
- **Import/Package Verification** — Validates packages against PyPI and npm registries
- **Function Signature Validation** — Detects wrong parameters, missing required args, unknown keywords (Jedi + inspect)
- **Deprecated API Detection** — Flags deprecated patterns with replacement suggestions
- **LLM Output Parsing** — Extract and validate code blocks from markdown responses
- **Pre-commit Integration** — Git hooks for Python and JavaScript/TypeScript
- **VS Code Extension** — Real-time diagnostics with configurable trigger modes
- **Multiple Output Modes** — Rich terminal output, JSON for CI/CD, VS Code diagnostics
- **REST API Server** — FastAPI-based server for integration with any workflow

## Quick Start

```bash
# Install
pip install -e .

# Validate a file
firewall check app.py

# Validate LLM markdown response
firewall parse response.md

# Validate from stdin
echo "import fakelib" | firewall check --stdin -l python

# JSON output for CI/CD
firewall check --format json app.py

# Start API server
firewall serve
```

## Installation

Requires Python 3.11+.

```bash
git clone https://github.com/tranhoangtu-it/AI-Hallucination-Firewall.git
cd AI-Hallucination-Firewall
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

### CLI — Code Validation

```bash
# Check single file
firewall check mycode.py

# Check multiple files
firewall check src/*.py

# Pipe from stdin
cat generated_code.py | firewall check --stdin -l python

# JSON output
firewall check --format json mycode.py
```

### CLI — LLM Output Parsing

```bash
# Validate code blocks in markdown file
firewall parse response.md

# Parse from stdin
curl https://api.example.com/response | firewall parse --stdin

# Parse from URL
firewall parse --url https://gist.github.com/my-response.md

# JSON output
firewall parse --format json response.md
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Add to .pre-commit-config.yaml
repos:
  - repo: https://github.com/tranhoangtu-it/AI-Hallucination-Firewall
    rev: v0.1.0
    hooks:
      - id: firewall-check          # Python files
      - id: firewall-check-js       # JavaScript/TypeScript files

# Install git hooks
pre-commit install

# Run manually
pre-commit run firewall-check --all-files
```

### VS Code Extension

1. Clone repository and navigate to `vscode-extension/`
2. Run `npm install && npm run compile`
3. Open VS Code command palette: `Extensions: Install from VSIX`
4. Select the built `.vsix` file
5. Configure in settings:
   - `hallucinationFirewall.triggerMode`: `onChange` (debounced) or `onSave` (default)
   - Real-time diagnostics appear in editor and Problem Panel

### API Server

```bash
# Start server
firewall serve --host 0.0.0.0 --port 8000

# Validate via API
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"code": "import fakelib", "language": "python"}'

# Health check
curl http://localhost:8000/health
```

### Configuration

Create a `.firewall.toml` in your project root:

```toml
[firewall]
languages = ["python", "javascript"]
severity_threshold = "warning"
cache_ttl_seconds = 3600
fail_on_network_error = false      # Block on registry timeout (pre-commit)
output_format = "terminal"

[firewall.registries]
pypi_enabled = true
npm_enabled = true
timeout_seconds = 10
max_retries = 2
```

## Validation Pipeline

```
Code Input → AST Parsing → Import Check → Signature Validation → Report
     │           │              │                │                  │
     │      tree-sitter    PyPI/npm         introspection     Rich/JSON
     │      (syntax)       (existence)      (correctness)     (output)
```

1. **Layer 1 — Syntax**: tree-sitter AST parsing catches malformed code
2. **Layer 2 — Imports**: Verifies packages exist on PyPI/npm registries
3. **Layer 3 — Signatures**: Validates function calls (args, parameters) using Jedi + inspect
4. **Layer 4 — Deprecation**: Flags deprecated patterns with fixes (future)

**Validation Features:**
- **Syntax Errors**: Malformed code, invalid Python/JavaScript
- **Package Validation**: Nonexistent packages on PyPI/npm
- **Signature Checks**: Missing required args, unknown parameters, wrong arg count
- **Import Validation**: Invalid or circular imports
- **LLM Output**: Extract and validate markdown code blocks

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov

# Lint
ruff check src/

# Type check
mypy src/
```

## Project Structure

```
src/hallucination_firewall/
├── cli.py                     # Click CLI (check, parse commands)
├── server.py                  # FastAPI REST server
├── config.py                  # Config loader (.firewall.toml)
├── models.py                  # Pydantic data models
├── pipeline/
│   ├── runner.py              # Pipeline orchestrator
│   ├── ast_validator.py       # tree-sitter AST validation
│   ├── import_checker.py      # Package existence verification
│   └── signature_checker.py   # Function signature validation (NEW)
├── parsers/
│   └── llm_output_parser.py   # LLM markdown parsing (NEW)
├── registries/
│   ├── pypi_registry.py       # PyPI API client
│   ├── npm_registry.py        # npm API client
│   └── cache.py               # SQLite cache layer
├── reporters/
│   ├── terminal_reporter.py   # Rich terminal output
│   └── json_reporter.py       # JSON output for CI/CD
└── utils/
    └── language_detector.py   # File language detection

vscode-extension/             # VS Code extension (NEW)
├── src/
│   ├── extension.ts           # Extension activation
│   └── diagnostics-mapper.ts  # Issue mapping
└── package.json

.pre-commit-hooks.yaml        # Pre-commit definitions (NEW)
```

## License

MIT License - see [LICENSE](LICENSE) for details.
