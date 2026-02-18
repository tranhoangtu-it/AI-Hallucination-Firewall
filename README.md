🇺🇸 [English](README.md) | 🇻🇳 [Tiếng Việt](README.vi.md) | 🇯🇵 [日本語](README.ja.md) | 🇰🇷 [한국어](README.ko.md)

---

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/tranhoangtu-it/AI-Hallucination-Firewall/releases)
[![Tests](https://img.shields.io/badge/tests-68%20passed-brightgreen.svg)](#development)
[![GitHub Pages](https://img.shields.io/badge/docs-live-blue.svg)](https://tranhoangtu-it.github.io/AI-Hallucination-Firewall/)

<p align="center">
  <img src="img/ai-hallucination-firewall.png" alt="AI Hallucination Firewall" width="600"/>
</p>

<p align="center">
  <strong>🌐 <a href="https://tranhoangtu-it.github.io/AI-Hallucination-Firewall/">Visit Landing Page</a></strong>
</p>

# AI Hallucination Firewall

A verification proxy that validates AI-generated code before it enters your codebase. Acts as a **"type checker for AI output"** — detects hallucinated functions, deprecated usage, invalid patterns, wrong signatures, and nonexistent packages.

## Features

- 🌳 **AST Syntax Validation** — tree-sitter parsing detects malformed code in Python, JavaScript, TypeScript
- 📦 **Import/Package Verification** — validates packages against PyPI and npm registries
- 🔍 **Function Signature Validation** — Jedi + inspect verifies parameters, required args, keyword arguments
- 📄 **LLM Output Parsing** — extracts and validates code blocks from markdown responses
- 🪝 **Pre-commit Integration** — automatic Git hooks for Python and JavaScript/TypeScript
- 🔌 **VS Code Extension** — real-time inline diagnostics with configurable trigger modes

## How It Works

```
Code Input → AST Parsing → Import Check → Signature Validation → Report
     │           │              │                │                  │
tree-sitter    PyPI/npm        Jedi         Rich/JSON output
 (syntax)    (packages)     (correctness)
```

**4-Layer Validation:**
1. **Syntax** — tree-sitter AST catches malformed code
2. **Imports** — verifies packages exist on PyPI/npm
3. **Signatures** — validates function parameters against real APIs
4. **Deprecation** — flags deprecated patterns with fixes (future)

## Installation

Requires Python 3.11+.

```bash
# Clone and install
git clone https://github.com/tranhoangtu-it/AI-Hallucination-Firewall.git
cd AI-Hallucination-Firewall
pip install -e ".[dev]"
```

## Quick Start

```bash
# Validate a file
firewall check app.py

# Validate LLM markdown response
firewall parse response.md

# JSON output for CI/CD
firewall check --format json app.py

# Start API server
firewall serve
```

## Usage

### CLI Commands

```bash
# Check single file
firewall check mycode.py

# Check multiple files
firewall check src/*.py

# Pipe from stdin
cat generated_code.py | firewall check --stdin -l python
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/tranhoangtu-it/AI-Hallucination-Firewall
    rev: v0.1.0
    hooks:
      - id: firewall-check
      - id: firewall-check-js
```

### VS Code Extension

1. Navigate to `vscode-extension/`, run `npm install && npm run compile`
2. Install via VS Code: `Extensions: Install from VSIX`
3. Configure `hallucinationFirewall.triggerMode`: `onSave` (default) or `onChange`

### API Server

```bash
# Start server
firewall serve --host 0.0.0.0 --port 8000

# Validate via API
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"code": "import fakelib", "language": "python"}'
```

### Configuration

Create `.firewall.toml` in your project root:

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
├── cli.py                     # Click CLI
├── server.py                  # FastAPI server
├── pipeline/                  # Validation layers
├── parsers/                   # LLM output parsing
├── registries/                # PyPI/npm clients
└── reporters/                 # Output formatting

vscode-extension/              # VS Code extension
.pre-commit-hooks.yaml         # Pre-commit definitions
```

## Who's This For?

- ✅ Developers using AI code assistants (Copilot, Claude, ChatGPT)
- ✅ Teams integrating LLM-generated code in CI/CD pipelines
- ✅ Projects enforcing code quality standards on AI output
- ✅ Anyone who wants to validate code before running it

## License

MIT License — see [LICENSE](LICENSE) for details.
