"""Pydantic models for validation results, config, and pipeline data."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity level for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueType(str, Enum):
    """Types of hallucination issues detected."""

    NONEXISTENT_PACKAGE = "nonexistent_package"
    NONEXISTENT_METHOD = "nonexistent_method"
    WRONG_SIGNATURE = "wrong_signature"
    DEPRECATED_API = "deprecated_api"
    INVALID_IMPORT = "invalid_import"
    SYNTAX_ERROR = "syntax_error"
    VERSION_MISMATCH = "version_mismatch"
    MISSING_REQUIRED_ARG = "missing_required_arg"
    UNKNOWN_PARAMETER = "unknown_parameter"


class SourceLocation(BaseModel):
    """Location of an issue in source code."""

    file: str
    line: int
    column: int = 0
    end_line: int | None = None
    end_column: int | None = None


class ValidationIssue(BaseModel):
    """A single validation issue found in code."""

    severity: Severity
    issue_type: IssueType
    location: SourceLocation
    message: str
    suggestion: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)
    source: str = ""


class ValidationResult(BaseModel):
    """Complete validation result for a code file."""

    file: str
    language: str
    issues: list[ValidationIssue] = []
    passed: bool = True
    checked_at: str = ""

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)


class Language(str, Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    UNKNOWN = "unknown"


class CodeBlock(BaseModel):
    """A single code block extracted from LLM output."""

    language: str
    code: str
    line_number: int
    block_index: int
    raw_tag: str = ""


class LLMValidationReport(BaseModel):
    """Aggregated validation results from LLM output."""

    total_blocks: int
    blocks_passed: int
    blocks_failed: int
    results: list[ValidationResult] = []

    @property
    def passed(self) -> bool:
        return self.blocks_failed == 0


class FirewallConfig(BaseModel):
    """Configuration for the hallucination firewall."""

    languages: list[Language] = [Language.PYTHON, Language.JAVASCRIPT]
    severity_threshold: Severity = Severity.WARNING
    cache_ttl_seconds: int = 3600
    cache_dir: Path = Path.home() / ".cache" / "hallucination-firewall"
    registries: RegistryConfig = Field(default_factory=lambda: RegistryConfig())
    fail_on_network_error: bool = False
    output_format: str = "terminal"


class RegistryConfig(BaseModel):
    """Configuration for package registry lookups."""

    pypi_enabled: bool = True
    npm_enabled: bool = True
    timeout_seconds: int = 10
