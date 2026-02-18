# Phase 1: Project Setup & Scaffolding

## Context
- [Research: Code Validation Approaches](../reports/researcher-260218-0207-code-validation-approaches.md)
- [Plan Overview](./plan.md)

## Overview
- **Priority:** P1 (blocker for all other phases)
- **Status:** pending
- **Effort:** 2h
- **Description:** Create Python project structure with pyproject.toml, dependencies, and directory scaffolding.

## Key Insights
- Python 3.11+ gives us built-in `tomllib` for config parsing
- `pyproject.toml` is the modern standard (PEP 621), no setup.py needed
- tree-sitter requires language grammar packages installed separately

## Requirements
- Functional: Installable package via `pip install -e .`, CLI entry point `firewall`
- Non-functional: Python 3.11+ minimum, fast dev install

## Architecture
```
AI-Hallucination-Firewall/
├── pyproject.toml
├── README.md
├── LICENSE
├── .firewall.toml              # Default config example
├── src/
│   └── hallucination_firewall/
│       ├── __init__.py
│       ├── cli.py
│       ├── server.py
│       ├── config.py
│       ├── models.py
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── runner.py
│       │   ├── ast_validator.py
│       │   ├── import_checker.py
│       │   ├── signature_validator.py
│       │   └── deprecation_checker.py
│       ├── registries/
│       │   ├── __init__.py
│       │   ├── pypi_registry.py
│       │   ├── npm_registry.py
│       │   └── cache.py
│       ├── reporters/
│       │   ├── __init__.py
│       │   ├── terminal_reporter.py
│       │   └── json_reporter.py
│       └── utils/
│           ├── __init__.py
│           └── language_detector.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_pipeline/
│   ├── test_registries/
│   ├── test_reporters/
│   └── test_cli.py
└── data/
    └── deprecations/
        └── python.json          # Known deprecated APIs
```

## Related Code Files
- **Create:** `pyproject.toml`, all `__init__.py` files, directory structure
- **Modify:** `README.md` (add badges, install instructions)

## Implementation Steps

1. **Create `pyproject.toml`** with:
   ```toml
   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [project]
   name = "hallucination-firewall"
   version = "0.1.0"
   requires-python = ">=3.11"
   dependencies = [
     "click>=8.1",
     "rich>=13.0",
     "fastapi>=0.109",
     "uvicorn[standard]>=0.27",
     "httpx>=0.27",
     "pydantic>=2.5",
     "tree-sitter>=0.21",
     "tree-sitter-python>=0.21",
     "tree-sitter-javascript>=0.21",
     "aiosqlite>=0.19",
   ]

   [project.optional-dependencies]
   dev = ["pytest>=8.0", "pytest-asyncio>=0.23", "pytest-cov", "ruff"]

   [project.scripts]
   firewall = "hallucination_firewall.cli:main"
   ```

2. **Create directory structure** — all directories and `__init__.py` files per architecture above

3. **Create stub files** — minimal placeholder for each module with docstring only (prevents import errors during development)

4. **Create `.firewall.toml`** example config:
   ```toml
   [general]
   languages = ["python"]
   severity_threshold = "warning"
   output_format = "terminal"

   [cache]
   enabled = true
   ttl_seconds = 3600
   db_path = ".firewall_cache.db"

   [registries]
   check_pypi = true
   check_npm = false
   ```

5. **Create `.gitignore`** — add Python defaults, `.firewall_cache.db`, dist/, etc.

6. **Verify install** — `pip install -e ".[dev]"` succeeds, `firewall --help` runs

## Todo List
- [ ] Create pyproject.toml with all dependencies
- [ ] Create full directory structure with __init__.py files
- [ ] Create stub files for all modules
- [ ] Create .firewall.toml example config
- [ ] Create .gitignore
- [ ] Create tests/ directory structure
- [ ] Create data/deprecations/python.json skeleton
- [ ] Verify editable install works
- [ ] Verify `firewall --help` entry point works

## Success Criteria
- `pip install -e ".[dev]"` completes without errors
- `firewall --help` prints help text
- All imports resolve (`python -c "import hallucination_firewall"`)
- `ruff check src/` passes with no errors

## Risk Assessment
- tree-sitter grammar packages may have version conflicts → pin versions
- Hatchling build backend is less common than setuptools → well-documented, low risk
