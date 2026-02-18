"""Validates that imported packages actually exist in registries."""

from __future__ import annotations

import importlib.util
import sys

from ..models import (
    IssueType,
    Severity,
    SourceLocation,
    ValidationIssue,
)
from ..registries.npm_registry import NpmRegistry
from ..registries.pypi_registry import PyPIRegistry

# Python stdlib modules — skip checking these
PYTHON_STDLIB = frozenset(sys.stdlib_module_names)

# Common built-in JS globals — not packages
JS_BUILTINS = frozenset({
    "fs", "path", "os", "http", "https", "url", "util",
    "crypto", "stream", "events", "child_process", "assert",
    "buffer", "cluster", "dgram", "dns", "net", "readline",
    "tls", "zlib", "querystring", "string_decoder", "timers",
    "tty", "v8", "vm", "worker_threads", "perf_hooks",
})


async def check_python_imports(
    imports: list[str],
    file_path: str,
    pypi: PyPIRegistry,
) -> list[ValidationIssue]:
    """Check Python imports against stdlib, local install, and PyPI."""
    issues: list[ValidationIssue] = []

    for package_name in imports:
        if package_name in PYTHON_STDLIB:
            continue

        # Check if installed locally
        if importlib.util.find_spec(package_name) is not None:
            continue

        # Check PyPI
        exists = await pypi.package_exists(_normalize_pypi_name(package_name))
        if not exists:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    issue_type=IssueType.NONEXISTENT_PACKAGE,
                    location=SourceLocation(file=file_path, line=0),
                    message=f"Package '{package_name}' not found on PyPI or locally",
                    suggestion="Check spelling. Similar packages may exist.",
                    confidence=0.9,
                    source="PyPI registry",
                )
            )

    return issues


async def check_js_imports(
    imports: list[str],
    file_path: str,
    npm: NpmRegistry,
) -> list[ValidationIssue]:
    """Check JavaScript/TypeScript imports against Node.js builtins and npm."""
    issues: list[ValidationIssue] = []

    for package_name in imports:
        # Skip Node.js builtins (with or without node: prefix)
        clean_name = package_name.removeprefix("node:")
        if clean_name in JS_BUILTINS:
            continue

        exists = await npm.package_exists(package_name)
        if not exists:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    issue_type=IssueType.NONEXISTENT_PACKAGE,
                    location=SourceLocation(file=file_path, line=0),
                    message=f"Package '{package_name}' not found on npm",
                    suggestion="Check spelling or verify the package name.",
                    confidence=0.9,
                    source="npm registry",
                )
            )

    return issues


def _normalize_pypi_name(name: str) -> str:
    """Normalize package name for PyPI lookup (underscores → hyphens)."""
    return name.replace("_", "-").lower()
