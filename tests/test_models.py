"""Tests for Pydantic models."""

from hallucination_firewall.models import (
    FirewallConfig,
    IssueType,
    RegistryConfig,
    Severity,
    SourceLocation,
    ValidationIssue,
    ValidationResult,
)


def test_validation_issue_creation():
    issue = ValidationIssue(
        severity=Severity.ERROR,
        issue_type=IssueType.NONEXISTENT_PACKAGE,
        location=SourceLocation(file="test.py", line=1),
        message="Package 'fake_pkg' not found",
    )
    assert issue.severity == Severity.ERROR
    assert issue.confidence == 0.9


def test_validation_result_counts():
    result = ValidationResult(
        file="test.py",
        language="python",
        issues=[
            ValidationIssue(
                severity=Severity.ERROR,
                issue_type=IssueType.NONEXISTENT_PACKAGE,
                location=SourceLocation(file="test.py", line=1),
                message="error1",
            ),
            ValidationIssue(
                severity=Severity.WARNING,
                issue_type=IssueType.DEPRECATED_API,
                location=SourceLocation(file="test.py", line=2),
                message="warning1",
            ),
            ValidationIssue(
                severity=Severity.ERROR,
                issue_type=IssueType.WRONG_SIGNATURE,
                location=SourceLocation(file="test.py", line=3),
                message="error2",
            ),
        ],
    )
    assert result.error_count == 2
    assert result.warning_count == 1


def test_validation_result_empty():
    result = ValidationResult(file="test.py", language="python")
    assert result.passed is True
    assert result.error_count == 0
    assert result.warning_count == 0


def test_firewall_config_defaults():
    config = FirewallConfig()
    assert config.cache_ttl_seconds == 3600
    assert config.severity_threshold == Severity.WARNING
    assert config.registries.pypi_enabled is True
    assert config.registries.npm_enabled is True


def test_registry_config_defaults():
    config = RegistryConfig()
    assert config.timeout_seconds == 10
