# Phase 6: Testing

## Context
- [Plan Overview](./plan.md)
- [Phase 3: Validation Pipeline](./phase-03-validation-pipeline.md)
- [Phase 4: CLI Interface](./phase-04-cli-interface.md)
- [Phase 5: API Server](./phase-05-api-server.md)

## Overview
- **Priority:** P1
- **Status:** pending
- **Effort:** 2h
- **Depends on:** Phases 3, 4, 5 (all features must be implemented)
- **Description:** Comprehensive pytest suite covering pipeline validators, CLI commands, and API endpoints.

## Key Insights
- Use `pytest-asyncio` for async validator tests
- Use Click's `CliRunner` for CLI tests (no subprocess needed)
- Use FastAPI's `TestClient` for API tests (no server needed)
- Create fixture files with known hallucination patterns for reproducible tests

## Requirements
- **Functional:** Tests for each validator, CLI command, and API endpoint
- **Non-functional:** >80% coverage, tests run in <30s, no network calls (mock registries)

## Architecture

```
tests/
├── conftest.py                    # Shared fixtures
├── test_config.py                 # Config loading tests
├── test_models.py                 # Model serialization tests
├── test_pipeline/
│   ├── test_runner.py             # Pipeline orchestration
│   ├── test_ast_validator.py      # AST parsing tests
│   ├── test_import_checker.py     # Import validation tests
│   ├── test_signature_validator.py
│   └── test_deprecation_checker.py
├── test_registries/
│   ├── test_pypi_registry.py      # PyPI client (mocked)
│   ├── test_npm_registry.py       # npm client (mocked)
│   └── test_cache.py              # SQLite cache tests
├── test_reporters/
│   ├── test_terminal_reporter.py
│   └── test_json_reporter.py
├── test_cli.py                    # CLI command tests
├── test_server.py                 # API endpoint tests
└── fixtures/
    ├── valid_python.py            # Clean Python code
    ├── hallucinated_imports.py    # Fake imports
    ├── wrong_signatures.py        # Wrong method params
    ├── deprecated_apis.py         # Deprecated usage
    └── syntax_errors.py           # Malformed code
```

## Related Code Files
- **Create:** All test files listed above
- **Create:** Test fixture files in `tests/fixtures/`

## Implementation Steps

### 6.1 Shared Fixtures (`conftest.py`)

```python
import pytest
from hallucination_firewall.config import FirewallConfig
from hallucination_firewall.pipeline.runner import create_pipeline

@pytest.fixture
def config():
    return FirewallConfig()

@pytest.fixture
def sample_python_code():
    return '''
import os
import fakelib  # nonexistent
from collections import MutableMapping  # deprecated

def greet(name):
    return json.dumps(name, pretty=True)  # wrong param
'''

@pytest.fixture
def valid_python_code():
    return '''
import os
import json

def greet(name: str) -> str:
    return json.dumps({"name": name}, indent=2)
'''
```

### 6.2 Pipeline Tests

**AST Validator:**
- Test: valid Python → no issues
- Test: syntax error → ERROR issue with correct line number
- Test: multi-language support (JS file)

**Import Checker:**
- Test: stdlib imports → no issues
- Test: known PyPI package → no issues (mock registry)
- Test: nonexistent package → ERROR issue
- Test: relative imports → skipped

**Signature Validator:**
- Test: correct stdlib call → no issues
- Test: wrong parameter name → WARNING issue
- Test: nonexistent method on module → ERROR issue

**Deprecation Checker:**
- Test: `import imp` → WARNING with replacement suggestion
- Test: modern imports → no issues

### 6.3 CLI Tests

```python
from click.testing import CliRunner
from hallucination_firewall.cli import main

def test_check_file(tmp_path):
    code_file = tmp_path / "test.py"
    code_file.write_text("import fakelib")
    runner = CliRunner()
    result = runner.invoke(main, ["check", str(code_file)])
    assert result.exit_code == 1
    assert "fakelib" in result.output

def test_check_stdin():
    runner = CliRunner()
    result = runner.invoke(main, ["check", "--stdin", "-l", "python"],
                          input="import os\n")
    assert result.exit_code == 0

def test_check_json_format(tmp_path):
    code_file = tmp_path / "test.py"
    code_file.write_text("import os")
    runner = CliRunner()
    result = runner.invoke(main, ["check", "--format", "json", str(code_file)])
    assert result.exit_code == 0
    import json
    json.loads(result.output)  # valid JSON
```

### 6.4 API Tests

```python
from fastapi.testclient import TestClient
from hallucination_firewall.server import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_validate_clean_code():
    r = client.post("/validate", json={"code": "import os", "language": "python"})
    assert r.status_code == 200
    assert r.json()["has_errors"] is False

def test_validate_hallucinated_import():
    r = client.post("/validate", json={"code": "import fakelib", "language": "python"})
    assert r.status_code == 200
    assert r.json()["has_errors"] is True
```

### 6.5 Registry & Cache Tests

- Mock httpx responses for PyPI/npm (use `pytest-httpx` or manual mocking)
- Test cache set/get/expiry with in-memory SQLite
- Test cache miss returns None

## Todo List
- [ ] Create conftest.py with shared fixtures
- [ ] Create test fixture files (valid, hallucinated, deprecated, syntax errors)
- [ ] Write AST validator tests (3+ cases)
- [ ] Write import checker tests (4+ cases, mocked registry)
- [ ] Write signature validator tests (3+ cases)
- [ ] Write deprecation checker tests (2+ cases)
- [ ] Write pipeline runner integration test
- [ ] Write CLI tests (check, stdin, json output, exit codes)
- [ ] Write API server tests (health, validate, error cases)
- [ ] Write cache tests (set, get, expiry)
- [ ] Write config loading tests
- [ ] Write model serialization tests
- [ ] Verify >80% code coverage with `pytest --cov`

## Success Criteria
- `pytest` passes all tests (0 failures)
- `pytest --cov` shows >80% coverage
- No network calls in test suite (all mocked)
- Tests complete in <30s
- Both happy path and error cases covered

## Risk Assessment
- tree-sitter may behave differently in test env → include integration test with real parsing
- Mocking httpx correctly requires careful setup → use `respx` or `pytest-httpx` library
- FastAPI TestClient runs sync → async validators still work (ASGI test client handles it)
