"""Tests for reporters."""

from __future__ import annotations

import io
import json

from rich.console import Console

from hallucination_firewall.models import (
    IssueType,
    Severity,
    SourceLocation,
    ValidationIssue,
    ValidationResult,
)
from hallucination_firewall.reporters.json_reporter import print_json
from hallucination_firewall.reporters.terminal_reporter import print_result, print_summary


def _make_result(passed: bool = True, issues: list | None = None) -> ValidationResult:
    return ValidationResult(
        file="test.py",
        language="python",
        checked_at="2026-01-01T00:00:00Z",
        passed=passed,
        issues=issues or [],
    )


def _make_issue(
    severity: Severity = Severity.ERROR,
    issue_type: IssueType = IssueType.SYNTAX_ERROR,
    message: str = "test error",
    suggestion: str | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        severity=severity,
        issue_type=issue_type,
        location=SourceLocation(file="test.py", line=10, column=5),
        message=message,
        suggestion=suggestion,
        source="test",
    )


class TestTerminalReporter:
    def test_print_result_passed(self):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=True, width=120)
        result = _make_result(passed=True)
        print_result(result, console)
        output = buf.getvalue()
        assert "test.py" in output

    def test_print_result_with_issues(self):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=True, width=120)
        issue = _make_issue(suggestion="Fix this")
        result = _make_result(passed=False, issues=[issue])
        print_result(result, console)
        output = buf.getvalue()
        assert "test.py" in output
        assert "FAILED" in output

    def test_print_result_with_warning(self):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=True, width=120)
        issue = _make_issue(severity=Severity.WARNING, message="deprecated")
        result = _make_result(passed=True, issues=[issue])
        print_result(result, console)
        output = buf.getvalue()
        assert "test.py" in output

    def test_print_result_with_info(self):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=True, width=120)
        issue = _make_issue(severity=Severity.INFO, message="info msg")
        result = _make_result(passed=True, issues=[issue])
        print_result(result, console)
        output = buf.getvalue()
        assert "test.py" in output

    def test_print_summary_all_passed(self):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=True, width=120)
        results = [_make_result(passed=True), _make_result(passed=True)]
        print_summary(results, console)
        output = buf.getvalue()
        assert "2" in output
        assert "passed" in output.lower()

    def test_print_summary_some_failed(self):
        buf = io.StringIO()
        console = Console(file=buf, no_color=True, width=120)
        issue = _make_issue()
        results = [
            _make_result(passed=True),
            _make_result(passed=False, issues=[issue]),
        ]
        print_summary(results, console)
        output = buf.getvalue()
        assert "1/2" in output
        assert "failed" in output.lower()


class TestJsonReporter:
    def test_print_json_basic(self):
        buf = io.StringIO()
        result = _make_result(passed=True)
        print_json([result], output=buf)
        data = json.loads(buf.getvalue())
        assert data["summary"]["total_files"] == 1
        assert data["summary"]["passed"] == 1

    def test_print_json_with_issues(self):
        buf = io.StringIO()
        issue = _make_issue()
        result = _make_result(passed=False, issues=[issue])
        print_json([result], output=buf)
        data = json.loads(buf.getvalue())
        assert data["summary"]["failed"] == 1
        assert data["summary"]["total_errors"] == 1

    def test_print_json_pretty(self):
        buf = io.StringIO()
        result = _make_result(passed=True)
        print_json([result], output=buf, pretty=True)
        output = buf.getvalue()
        # Pretty-printed JSON has newlines and indentation
        assert "\n" in output
        data = json.loads(output)
        assert data["summary"]["total_files"] == 1
