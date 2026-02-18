"""Tests for SARIF v2.1.0 reporter — covers all branches."""

from __future__ import annotations

import io
import json

from hallucination_firewall.models import (
    IssueType,
    Severity,
    SourceLocation,
    ValidationIssue,
    ValidationResult,
)
from hallucination_firewall.reporters.sarif_reporter import (
    _build_sarif_rules,
    _issue_type_to_rule_id,
    _severity_to_sarif_level,
    print_sarif,
)


def test_severity_to_sarif_level():
    assert _severity_to_sarif_level(Severity.ERROR) == "error"
    assert _severity_to_sarif_level(Severity.WARNING) == "warning"
    assert _severity_to_sarif_level(Severity.INFO) == "note"


def test_issue_type_to_rule_id():
    assert _issue_type_to_rule_id(IssueType.SYNTAX_ERROR) == "syntax_error"
    assert _issue_type_to_rule_id(IssueType.NONEXISTENT_PACKAGE) == "nonexistent_package"
    assert _issue_type_to_rule_id(IssueType.DEPRECATED_API) == "deprecated_api"


def test_build_sarif_rules():
    rules = _build_sarif_rules()
    assert len(rules) == len(IssueType)
    assert all("id" in r and "shortDescription" in r for r in rules)

    rule_ids = {r["id"] for r in rules}
    assert "syntax_error" in rule_ids
    assert "nonexistent_package" in rule_ids
    assert "wrong_signature" in rule_ids


def test_print_sarif_empty_results():
    output = io.StringIO()
    print_sarif([], output)

    data = json.loads(output.getvalue())
    assert "sarif" in data["$schema"]
    assert data["version"] == "2.1.0"
    assert len(data["runs"]) == 1
    assert len(data["runs"][0]["results"]) == 0
    assert len(data["runs"][0]["tool"]["driver"]["rules"]) > 0


def test_print_sarif_full_output():
    issue1 = ValidationIssue(
        severity=Severity.ERROR,
        issue_type=IssueType.SYNTAX_ERROR,
        location=SourceLocation(
            file="test.py", line=10, column=5, end_line=10, end_column=15
        ),
        message="Syntax error at line 10",
        suggestion="Fix the parenthesis",
    )
    issue2 = ValidationIssue(
        severity=Severity.WARNING,
        issue_type=IssueType.NONEXISTENT_PACKAGE,
        location=SourceLocation(file="test.py", line=1, column=1),
        message="Package not found: fakelib",
    )
    result = ValidationResult(
        file="test.py", language="python", issues=[issue1, issue2]
    )

    output = io.StringIO()
    print_sarif([result], output)
    data = json.loads(output.getvalue())

    results = data["runs"][0]["results"]
    assert len(results) == 2

    # First result: error with suggestion and end positions
    r0 = results[0]
    assert r0["level"] == "error"
    assert r0["ruleId"] == "syntax_error"
    assert "Fix the parenthesis" in r0["message"]["text"]
    region0 = r0["locations"][0]["physicalLocation"]["region"]
    assert region0["startLine"] == 10
    assert region0["endLine"] == 10
    assert region0["endColumn"] == 15

    # Second result: warning without suggestion, no end positions
    r1 = results[1]
    assert r1["level"] == "warning"
    assert r1["ruleId"] == "nonexistent_package"
    assert "endLine" not in r1["locations"][0]["physicalLocation"]["region"]


def test_print_sarif_no_suggestion():
    issue = ValidationIssue(
        severity=Severity.INFO,
        issue_type=IssueType.DEPRECATED_API,
        location=SourceLocation(file="test.py", line=5),
        message="Deprecated API usage",
    )
    result = ValidationResult(file="test.py", language="python", issues=[issue])

    output = io.StringIO()
    print_sarif([result], output)
    data = json.loads(output.getvalue())

    r = data["runs"][0]["results"][0]
    assert r["level"] == "note"
    assert "Suggestion:" not in r["message"]["text"]
