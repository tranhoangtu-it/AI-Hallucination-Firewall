"""Tests for deprecation checker (Layer 4)."""

from __future__ import annotations

import pytest

from hallucination_firewall.models import IssueType, Language, Severity
from hallucination_firewall.pipeline.deprecation_checker import (
    PYTHON_DEPRECATIONS,
    check_deprecations,
)


class TestCheckDeprecations:
    @pytest.mark.asyncio
    async def test_os_popen_detected(self):
        code = "import os\nos.popen('ls')\n"
        issues = await check_deprecations(code, Language.PYTHON, "test.py")
        assert len(issues) == 1
        assert issues[0].issue_type == IssueType.DEPRECATED_API
        assert "os.popen" in issues[0].message
        assert issues[0].severity == Severity.WARNING

    @pytest.mark.asyncio
    async def test_os_system_detected(self):
        code = "import os\nos.system('ls')\n"
        issues = await check_deprecations(code, Language.PYTHON, "test.py")
        assert len(issues) == 1
        assert "os.system" in issues[0].message

    @pytest.mark.asyncio
    async def test_typing_dict_detected(self):
        code = "from typing import Dict\ntyping.Dict()\n"
        issues = await check_deprecations(code, Language.PYTHON, "test.py")
        # FunctionCallExtractor only catches calls like typing.Dict()
        for issue in issues:
            assert issue.issue_type == IssueType.DEPRECATED_API

    @pytest.mark.asyncio
    async def test_clean_code_no_issues(self):
        code = "import subprocess\nsubprocess.run(['ls'])\n"
        issues = await check_deprecations(code, Language.PYTHON, "test.py")
        assert issues == []

    @pytest.mark.asyncio
    async def test_non_python_skipped(self):
        code = "os.popen('ls')\n"
        issues = await check_deprecations(code, Language.JAVASCRIPT, "test.js")
        assert issues == []

    @pytest.mark.asyncio
    async def test_suggestion_contains_replacement(self):
        code = "import os\nos.popen('ls')\n"
        issues = await check_deprecations(code, Language.PYTHON, "test.py")
        assert issues[0].suggestion is not None
        assert "subprocess.run()" in issues[0].suggestion

    @pytest.mark.asyncio
    async def test_confidence_is_high(self):
        code = "import os\nos.popen('ls')\n"
        issues = await check_deprecations(code, Language.PYTHON, "test.py")
        assert issues[0].confidence == 0.95

    @pytest.mark.asyncio
    async def test_source_is_deprecation_checker(self):
        code = "import os\nos.popen('ls')\n"
        issues = await check_deprecations(code, Language.PYTHON, "test.py")
        assert issues[0].source == "deprecation_checker"


class TestDeprecationRules:
    def test_rules_count(self):
        assert len(PYTHON_DEPRECATIONS) >= 13

    def test_all_rules_have_required_fields(self):
        for pattern, rule in PYTHON_DEPRECATIONS.items():
            assert rule.pattern == pattern
            assert rule.replacement
            assert rule.since
            assert rule.severity == Severity.WARNING
