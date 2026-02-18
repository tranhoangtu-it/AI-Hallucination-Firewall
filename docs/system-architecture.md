# System Architecture

## Overview
Pipeline-based validation system with four major features: multi-layer code validation, LLM output parsing, pre-commit integration, and VS Code extension support.

## Component Diagram

```
┌──────────────────────────────────────────────────────┐
│                   Entry Points                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  CLI      │  │  API     │  │  VS Code Ext.    │   │
│  │  (Click)  │  │(FastAPI) │  │  (TypeScript)    │   │
│  └────┬─────┘  └────┬─────┘  └────────┬────────┘   │
│  ┌────────────┐  ┌──────────────────────────┐      │
│  │  Pre-commit│  │  LLM Output Parser       │      │
│  │   Hooks    │  │  (firewall parse)        │      │
│  └────┬───────┘  └──────────┬───────────────┘      │
└───────┼──────────────────────┼─────────────────────┘
        └──────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│            Validation Pipeline (runner.py)            │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Layer 1  │  │  Layer 2  │  │    Layer 3       │  │
│  │  AST      │→ │  Import   │→ │  Signature       │  │
│  │  Syntax   │  │  Check    │  │  Validation      │  │
│  │(tree-sitter)│(PyPI/npm) │(Jedi+Inspect)│  │
│  └──────────┘  └────┬─────┘  └──────────────────┘  │
└──────────────────────┼──────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│                 Registry Clients                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  PyPI     │  │  npm     │  │  SQLite Cache    │   │
│  │  Client   │  │  Client  │  │  (TTL-based)     │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│                    Reporters                         │
│  ┌──────────────────┐  ┌──────────────────────────┐ │
│  │  Terminal (Rich)  │  │  JSON / Diagnostics    │ │
│  │  (CLI/Pre-commit) │  │  (CI/CD, VS Code)      │ │
│  └──────────────────┘  └──────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## Data Flow
1. Code input → Language detection (file extension or heuristics)
2. tree-sitter AST parsing → Syntax error detection
3. Import extraction from AST → Package existence check (PyPI/npm)
4. Function call extraction (tree-sitter) → Signature validation (Jedi + inspect)
5. LLM output parsing (markdown blocks) → Validate extracted code blocks
6. Results aggregation → Reporter output (terminal/JSON/diagnostics)

## Key Design Decisions
- **Fail open:** Unknown patterns get warnings, not errors
- **Cache aggressively:** Registry data cached in SQLite (1h TTL)
- **Async pipeline:** httpx async client for registry queries
- **Layered validation:** Early failures skip expensive checks
- **Pluggable validators:** Easy to add new validation layers

## File Structure
```
src/hallucination_firewall/
├── cli.py                        # Entry: Click CLI with check/parse commands
├── server.py                     # Entry: FastAPI server
├── config.py                     # .firewall.toml loader
├── models.py                     # Pydantic models (+ CodeBlock, LLMValidationReport)
├── pipeline/                     # Validation logic
│   ├── runner.py                 # Orchestrator (4-layer pipeline)
│   ├── ast_validator.py          # tree-sitter syntax validation
│   ├── import_checker.py         # Package registry checks
│   └── signature_checker.py      # Function signature validation (NEW)
├── parsers/                      # LLM output parsing (NEW)
│   └── llm_output_parser.py      # Markdown block extraction & validation
├── registries/                   # External APIs
│   ├── pypi_registry.py
│   ├── npm_registry.py
│   └── cache.py                  # SQLite cache
├── reporters/                    # Output formatting
│   ├── terminal_reporter.py
│   └── json_reporter.py
└── utils/
    └── language_detector.py
```
