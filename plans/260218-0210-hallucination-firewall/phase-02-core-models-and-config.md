# Phase 2: Core Models & Configuration

## Context
- [Plan Overview](./plan.md)
- [Phase 1: Project Setup](./phase-01-project-setup.md)

## Overview
- **Priority:** P1
- **Status:** pending
- **Effort:** 2h
- **Depends on:** Phase 1 (structure must exist)
- **Description:** Define Pydantic v2 models for validation results, config loading from `.firewall.toml`, and shared data structures.

## Key Insights
- Pydantic v2 is 5-50x faster than v1, use `model_validator` for complex rules
- Python 3.11+ has `tomllib` built-in — no extra dependency for TOML parsing
- Models are the contract between pipeline, reporters, and API — get them right first

## Requirements
- **Functional:** Config loader reads `.firewall.toml`, models represent all validation outputs
- **Non-functional:** All models frozen/immutable where possible, JSON-serializable

## Architecture

```
config.py ──→ loads .firewall.toml ──→ FirewallConfig (pydantic)
models.py ──→ ValidationResult, Issue, Severity, etc.
```

## Related Code Files
- **Create:** `src/hallucination_firewall/config.py`, `src/hallucination_firewall/models.py`

## Implementation Steps

### 1. Define models in `models.py`

```python
from enum import StrEnum
from pydantic import BaseModel, Field

class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class IssueType(StrEnum):
    SYNTAX_ERROR = "syntax_error"
    NONEXISTENT_IMPORT = "nonexistent_import"
    NONEXISTENT_METHOD = "nonexistent_method"
    WRONG_SIGNATURE = "wrong_signature"
    DEPRECATED_API = "deprecated_api"
    INVALID_PARAMETER = "invalid_parameter"

class SourceLocation(BaseModel, frozen=True):
    file: str
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None

class Suggestion(BaseModel, frozen=True):
    text: str
    confidence: float = Field(ge=0.0, le=1.0)

class Issue(BaseModel, frozen=True):
    severity: Severity
    issue_type: IssueType
    location: SourceLocation
    message: str
    suggestion: Suggestion | None = None
    source: str = ""  # e.g., "PyPI registry", "type stubs"

class ValidationResult(BaseModel):
    file_path: str
    language: str
    issues: list[Issue] = Field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)
```

### 2. Define config in `config.py`

```python
import tomllib
from pathlib import Path
from pydantic import BaseModel, Field

class CacheConfig(BaseModel):
    enabled: bool = True
    ttl_seconds: int = 3600
    db_path: str = ".firewall_cache.db"

class RegistryConfig(BaseModel):
    check_pypi: bool = True
    check_npm: bool = False
    timeout_seconds: float = 10.0

class GeneralConfig(BaseModel):
    languages: list[str] = Field(default_factory=lambda: ["python"])
    severity_threshold: str = "warning"
    output_format: str = "terminal"  # "terminal" | "json"

class FirewallConfig(BaseModel):
    general: GeneralConfig = Field(default_factory=GeneralConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    registries: RegistryConfig = Field(default_factory=RegistryConfig)

CONFIG_FILENAME = ".firewall.toml"

def load_config(path: Path | None = None) -> FirewallConfig:
    """Load config from .firewall.toml, falling back to defaults."""
    if path is None:
        path = Path.cwd() / CONFIG_FILENAME
    if not path.exists():
        return FirewallConfig()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return FirewallConfig.model_validate(data)
```

### 3. Define base validator protocol

```python
# In models.py or a separate protocols.py
from typing import Protocol

class Validator(Protocol):
    """Protocol all pipeline validators must implement."""
    async def validate(self, code: str, language: str, file_path: str) -> list[Issue]: ...
```

### 4. Define language detector in `utils/language_detector.py`

Map file extensions to language names. Support: `.py` → python, `.js` → javascript, `.ts` → typescript, `.jsx`/`.tsx` → javascript/typescript.

## Todo List
- [ ] Create `models.py` with Severity, IssueType, SourceLocation, Suggestion, Issue, ValidationResult
- [ ] Create `config.py` with FirewallConfig, load_config()
- [ ] Create Validator protocol (in models.py)
- [ ] Create `utils/language_detector.py`
- [ ] Add docstrings to all public classes/functions
- [ ] Verify models serialize to JSON correctly

## Success Criteria
- `FirewallConfig()` returns valid defaults
- `load_config()` reads a sample `.firewall.toml` correctly
- `ValidationResult` serializes to JSON via `.model_dump_json()`
- `Issue` instances are immutable (frozen)
- Language detector correctly maps 5+ extensions

## Risk Assessment
- Config schema changes later → use Field defaults liberally, add `model_config = ConfigDict(extra="ignore")` so unknown keys don't crash
- StrEnum requires Python 3.11+ → already a project requirement
