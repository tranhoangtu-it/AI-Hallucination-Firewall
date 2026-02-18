"""Validates that imported packages actually exist in registries."""

from __future__ import annotations

import asyncio
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

# Maximum concurrent registry checks
MAX_CONCURRENT_CHECKS = 10

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
    sem = asyncio.Semaphore(MAX_CONCURRENT_CHECKS)

    async def _check_one(package_name: str) -> ValidationIssue | None:
        if package_name in PYTHON_STDLIB:
            return None

        # Check if installed locally
        if importlib.util.find_spec(package_name) is not None:
            return None

        # Check PyPI with semaphore
        async with sem:
            exists = await pypi.package_exists(_normalize_pypi_name(package_name))

        if not exists:
            return ValidationIssue(
                severity=Severity.ERROR,
                issue_type=IssueType.NONEXISTENT_PACKAGE,
                location=SourceLocation(file=file_path, line=0),
                message=f"Package '{package_name}' not found on PyPI or locally",
                suggestion="Check spelling. Similar packages may exist.",
                confidence=0.9,
                source="PyPI registry",
            )
        return None

    tasks = [_check_one(pkg) for pkg in imports]
    results = await asyncio.gather(*tasks)
    return [issue for issue in results if issue is not None]


async def check_js_imports(
    imports: list[str],
    file_path: str,
    npm: NpmRegistry,
) -> list[ValidationIssue]:
    """Check JavaScript/TypeScript imports against Node.js builtins and npm."""
    sem = asyncio.Semaphore(MAX_CONCURRENT_CHECKS)

    async def _check_one(package_name: str) -> ValidationIssue | None:
        # Skip Node.js builtins (with or without node: prefix)
        clean_name = package_name.removeprefix("node:")
        if clean_name in JS_BUILTINS:
            return None

        async with sem:
            exists = await npm.package_exists(package_name)

        if not exists:
            return ValidationIssue(
                severity=Severity.ERROR,
                issue_type=IssueType.NONEXISTENT_PACKAGE,
                location=SourceLocation(file=file_path, line=0),
                message=f"Package '{package_name}' not found on npm",
                suggestion="Check spelling or verify the package name.",
                confidence=0.9,
                source="npm registry",
            )
        return None

    tasks = [_check_one(pkg) for pkg in imports]
    results = await asyncio.gather(*tasks)
    return [issue for issue in results if issue is not None]


def _normalize_pypi_name(name: str) -> str:
    """Normalize package name for PyPI lookup (underscores → hyphens)."""
    return name.replace("_", "-").lower()
