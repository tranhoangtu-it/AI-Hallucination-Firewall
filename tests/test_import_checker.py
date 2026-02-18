"""Tests for import checker."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from hallucination_firewall.models import IssueType, Severity
from hallucination_firewall.pipeline.import_checker import (
    JS_BUILTINS,
    PYTHON_STDLIB,
    _normalize_pypi_name,
    check_js_imports,
    check_python_imports,
)


@pytest.fixture
def mock_pypi():
    registry = MagicMock()
    registry.package_exists = AsyncMock(return_value=True)
    return registry


@pytest.fixture
def mock_npm():
    registry = MagicMock()
    registry.package_exists = AsyncMock(return_value=True)
    return registry


class TestPythonImports:
    @pytest.mark.asyncio
    async def test_stdlib_import_passes(self, mock_pypi):
        issues = await check_python_imports(["os", "sys", "json"], "test.py", mock_pypi)
        assert issues == []
        mock_pypi.package_exists.assert_not_called()

    @pytest.mark.asyncio
    async def test_installed_package_passes(self, mock_pypi):
        # pytest is installed in the venv
        issues = await check_python_imports(["pytest"], "test.py", mock_pypi)
        assert issues == []

    @pytest.mark.asyncio
    async def test_nonexistent_package_fails(self, mock_pypi):
        mock_pypi.package_exists = AsyncMock(return_value=False)
        issues = await check_python_imports(
            ["totally_fake_package_xyz"], "test.py", mock_pypi
        )
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.NONEXISTENT_PACKAGE
        assert issues[0].severity == Severity.ERROR

    @pytest.mark.asyncio
    async def test_pypi_exists_passes(self, mock_pypi):
        # A package not in stdlib/local but exists on PyPI
        mock_pypi.package_exists = AsyncMock(return_value=True)
        issues = await check_python_imports(
            ["some_unknown_pkg_abc"], "test.py", mock_pypi
        )
        # If find_spec returns None, it should check PyPI
        # Since mock returns True, no issues
        for issue in issues:
            assert issue.issue_type != IssueType.NONEXISTENT_PACKAGE


class TestJsImports:
    @pytest.mark.asyncio
    async def test_node_builtin_passes(self, mock_npm):
        issues = await check_js_imports(["fs", "path", "http"], "test.js", mock_npm)
        assert issues == []
        mock_npm.package_exists.assert_not_called()

    @pytest.mark.asyncio
    async def test_node_prefix_builtin_passes(self, mock_npm):
        issues = await check_js_imports(["node:fs", "node:path"], "test.js", mock_npm)
        assert issues == []

    @pytest.mark.asyncio
    async def test_nonexistent_npm_package_fails(self, mock_npm):
        mock_npm.package_exists = AsyncMock(return_value=False)
        issues = await check_js_imports(
            ["totally-fake-npm-pkg"], "test.js", mock_npm
        )
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.NONEXISTENT_PACKAGE
        assert "npm" in issues[0].source

    @pytest.mark.asyncio
    async def test_npm_exists_passes(self, mock_npm):
        mock_npm.package_exists = AsyncMock(return_value=True)
        issues = await check_js_imports(["react"], "test.js", mock_npm)
        assert issues == []


class TestNormalizePypiName:
    def test_underscore_to_hyphen(self):
        assert _normalize_pypi_name("my_package") == "my-package"

    def test_lowercase(self):
        assert _normalize_pypi_name("MyPackage") == "mypackage"

    def test_combined(self):
        assert _normalize_pypi_name("My_Cool_Package") == "my-cool-package"


class TestConstants:
    def test_stdlib_has_common_modules(self):
        for mod in ["os", "sys", "json", "pathlib", "typing"]:
            assert mod in PYTHON_STDLIB

    def test_js_builtins_has_common_modules(self):
        for mod in ["fs", "path", "http", "crypto"]:
            assert mod in JS_BUILTINS
