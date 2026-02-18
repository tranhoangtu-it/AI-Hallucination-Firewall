# AI Hallucination Firewall

A verification proxy that validates AI-generated code before it enters your codebase. Acts as a **"type checker for AI output"** — detects hallucinated functions, deprecated usage, invalid patterns, wrong signatures, and nonexistent packages.

## Features

- **AST Syntax Validation** — Catches syntax errors using tree-sitter (Python, JavaScript, TypeScript)
- **Import/Package Verification** — Validates packages against PyPI and npm registries
- **Method Signature Checking** — Detects wrong parameters and nonexistent methods
- **Deprecated API Detection** — Flags deprecated patterns with replacement suggestions
- **Multiple Output Modes** — Rich terminal output or JSON for CI/CD
- **REST API Server** — FastAPI-based server for integration with any workflow

## Quick Start

```bash
# Install
pip install -e .

# Validate a file
firewall check app.py

# Validate from stdin (pipe from LLM)
echo "import fakelib" | firewall check --stdin -l python

# JSON output for CI/CD
firewall check --format json app.py

# Start API server
firewall serve
```

## Installation

Requires Python 3.11+.

```bash
git clone https://github.com/tranhoangtu/AI-Hallucination-Firewall.git
cd AI-Hallucination-Firewall
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

### CLI

```bash
# Check single file
firewall check mycode.py

# Check multiple files
firewall check src/*.py

# Pipe from stdin
cat generated_code.py | firewall check --stdin -l python

# JSON output
firewall check --format json mycode.py

# Initialize config
firewall init
```

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
output_format = "terminal"

[firewall.registries]
pypi_enabled = true
npm_enabled = true
timeout_seconds = 10
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
3. **Layer 3 — Signatures**: Validates method calls against real APIs
4. **Layer 4 — Deprecation**: Flags deprecated patterns with fixes

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
├── cli.py                     # Click CLI entry point
├── server.py                  # FastAPI REST server
├── config.py                  # Config loader (.firewall.toml)
├── models.py                  # Pydantic data models
├── pipeline/
│   ├── runner.py              # Pipeline orchestrator
│   ├── ast_validator.py       # tree-sitter AST validation
│   └── import_checker.py      # Package existence verification
├── registries/
│   ├── pypi_registry.py       # PyPI API client
│   ├── npm_registry.py        # npm API client
│   └── cache.py               # SQLite cache layer
├── reporters/
│   ├── terminal_reporter.py   # Rich terminal output
│   └── json_reporter.py       # JSON output for CI/CD
└── utils/
    └── language_detector.py   # File language detection
```

## License

MIT License - see [LICENSE](LICENSE) for details.
