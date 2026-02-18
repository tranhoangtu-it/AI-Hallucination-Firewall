# Project Overview — AI Hallucination Firewall

## Purpose
Verification proxy between developers and LLMs that validates AI-generated code before it enters the codebase.

## Problem Statement
LLMs frequently generate code with hallucinated APIs, nonexistent packages, wrong method signatures, and deprecated patterns. Developers waste significant time debugging AI-generated code that looks correct but references nonexistent functionality.

## Solution
A multi-layer validation pipeline that checks generated code against real sources:
1. AST syntax validation (tree-sitter)
2. Package existence verification (PyPI, npm)
3. Method signature validation (introspection)
4. Deprecated API detection

## Target Users
- Developers using AI code assistants (Copilot, Claude, ChatGPT)
- CI/CD pipelines integrating LLM-generated code
- Teams enforcing code quality standards on AI output

## Key Metrics
- Detection rate: catch 80%+ of hallucinated code patterns
- Latency: <2s per file validation
- False positive rate: <5%

## Tech Stack
- **Language:** Python 3.11+
- **AST Parsing:** tree-sitter
- **CLI:** Click + Rich
- **API:** FastAPI + uvicorn
- **HTTP Client:** httpx (async)
- **Models:** Pydantic v2
- **Cache:** SQLite
- **Testing:** pytest

## Architecture
Pipeline-based design with pluggable validators. Each layer runs in sequence, and early failures (syntax errors) skip deeper checks for speed.

## Delivery Modes
| Mode | Use Case |
|------|----------|
| CLI (`firewall check`) | Local file validation |
| CLI (`firewall parse`) | LLM markdown output validation |
| Pre-commit hooks | Git integration (Python/JS) |
| API (`firewall serve`) | CI/CD integration |
| VS Code extension | Real-time IDE diagnostics |
| JSON output | Automated processing |

## Feature Summary (v0.1.0)

### Layer 3: Signature Validation
- **File:** `src/hallucination_firewall/pipeline/signature_checker.py`
- **Method:** Jedi + inspect fallback with LRU caching
- **Detection:** Missing required args, unknown parameters, wrong signatures
- **Issue Types:** MISSING_REQUIRED_ARG, UNKNOWN_PARAMETER, WRONG_SIGNATURE
- **Scope:** Python only, dotted function names (e.g., `module.func()`)

### LLM Output Parser
- **File:** `src/hallucination_firewall/parsers/llm_output_parser.py`
- **Method:** Regex extraction of markdown fenced code blocks
- **Language Detection:** Heuristics (imports, keywords, JSON, SQL, XML)
- **Support:** Python, JavaScript, TypeScript, SQL, Bash, XML, JSON
- **CLI:** `firewall parse [file|--stdin|--url <markdown-url>]`

### Pre-commit Hooks
- **File:** `.pre-commit-hooks.yaml`
- **Hooks:** firewall-check (Python), firewall-check-js (JavaScript/TypeScript)
- **Config:** fail_on_network_error flag in .firewall.toml
- **Integration:** Standard pre-commit framework

### VS Code Extension
- **Path:** `vscode-extension/` (TypeScript)
- **Features:** Real-time diagnostics, debounced validation, configurable trigger mode
- **Modes:** onChange (debounced), onSave (default)
- **Output:** VS Code Problem Panel integration
