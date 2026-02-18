# Code Standards

## Language & Version
- Python 3.11+ (uses tomllib, type union syntax)
- Type hints on all public functions
- `from __future__ import annotations` in all modules

## Code Style
- **Formatter:** Ruff (line length 100)
- **Linter:** Ruff (rules: E, F, I, N, W)
- **Type checker:** mypy (strict mode)
- **Naming:** snake_case for files, functions, variables; PascalCase for classes

## Project Layout
- Source: `src/hallucination_firewall/`
- Tests: `tests/`
- Config: `pyproject.toml`
- Docs: `docs/`

## Dependencies
- Use `pyproject.toml` for dependency management
- Pin minimum versions, not exact
- Dev dependencies in `[project.optional-dependencies.dev]`
- Key packages: jedi (0.19+), tree-sitter, fastapi, pydantic v2, httpx

## Patterns
- **Models:** Pydantic v2 BaseModel for all data structures
- **Config:** TOML files loaded with tomllib (support fail_on_network_error flag)
- **HTTP:** httpx async client with timeout
- **CLI:** Click groups and commands (check, parse subcommands)
- **Output:** Rich for terminal, json module for JSON, VS Code diagnostics
- **Cache:** SQLite via sqlite3 stdlib with TTL
- **AST:** tree-sitter for multi-language parsing
- **Signature Lookup:** Jedi + inspect fallback (safe stdlib modules only)
- **LLM Parsing:** Regex extraction of markdown code fences with language heuristics

## Error Handling
- **Fail open:** Network errors → warn, don't block
- **Try/except** around external calls (httpx, file I/O)
- **Pydantic validation** for config and API input
- **Exit codes:** 0 = clean, 1 = errors found

## Testing
- pytest with pytest-asyncio
- No network calls in tests (mock registries)
- Fixture files for reproducible test cases
- Target: >99% coverage (currently 99%, 210 tests)
