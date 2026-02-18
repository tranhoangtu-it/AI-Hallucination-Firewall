"""Deprecation detection — flags deprecated stdlib patterns with replacements."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import (
    IssueType,
    Severity,
    SourceLocation,
    ValidationIssue,
)
from ..models import Language as LangEnum
from .signature_checker import FunctionCallExtractor


@dataclass(frozen=True)
class DeprecationRule:
    """A single deprecation pattern."""

    pattern: str  # dotted name, e.g. "os.popen"
    replacement: str  # suggested fix
    since: str  # Python version deprecated
    severity: Severity = Severity.WARNING


# Static deprecation rules — Python stdlib only
PYTHON_DEPRECATIONS: dict[str, DeprecationRule] = {
    r.pattern: r
    for r in [
        DeprecationRule("os.popen", "subprocess.run()", "3.0"),
        DeprecationRule("os.system", "subprocess.run()", "3.0"),
        DeprecationRule("unittest.makeSuite", "TestLoader.loadTestsFromTestCase()", "3.11"),
        DeprecationRule(
            "unittest.getTestCaseNames", "TestLoader.getTestCaseNames()", "3.11"
        ),
        DeprecationRule("unittest.findTestCases", "TestLoader.discover()", "3.11"),
        DeprecationRule("typing.Dict", "dict", "3.9"),
        DeprecationRule("typing.List", "list", "3.9"),
        DeprecationRule("typing.Tuple", "tuple", "3.9"),
        DeprecationRule("typing.Set", "set", "3.9"),
        DeprecationRule("typing.FrozenSet", "frozenset", "3.9"),
        DeprecationRule("typing.Optional", "X | None", "3.10"),
        DeprecationRule("imp.find_module", "importlib.util.find_spec()", "3.4"),
        DeprecationRule("imp.load_module", "importlib.import_module()", "3.4"),
    ]
}


async def check_deprecations(
    code: str,
    language: LangEnum,
    file_path: str,
) -> list[ValidationIssue]:
    """Check code for deprecated API usage. Entry point for pipeline."""
    if language != LangEnum.PYTHON:
        return []

    extractor = FunctionCallExtractor()
    calls = extractor.extract_calls(code)
    issues: list[ValidationIssue] = []

    for call in calls:
        rule = PYTHON_DEPRECATIONS.get(call.name)
        if rule:
            issues.append(
                ValidationIssue(
                    severity=rule.severity,
                    issue_type=IssueType.DEPRECATED_API,
                    location=SourceLocation(file=file_path, line=call.line + 1, column=0),
                    message=f"'{call.name}()' is deprecated since Python {rule.since}",
                    suggestion=f"Use {rule.replacement} instead",
                    confidence=0.95,
                    source="deprecation_checker",
                )
            )

    return issues
