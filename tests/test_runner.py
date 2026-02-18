"""Tests for validation pipeline runner."""

from __future__ import annotations

import pytest

from hallucination_firewall.models import IssueType, Severity
from hallucination_firewall.pipeline.runner import ValidationPipeline


@pytest.fixture
def pipeline():
    return ValidationPipeline()


class TestValidateCode:
    @pytest.mark.asyncio
    async def test_validate_valid_python(self, pipeline):
        code = "import os\nprint(os.getcwd())\n"
        result = await pipeline.validate_code(code, "test.py")
        assert result.file == "test.py"
        assert result.language == "python"
        assert result.checked_at is not None

    @pytest.mark.asyncio
    async def test_validate_syntax_error(self, pipeline):
        code = "def foo(\n"
        result = await pipeline.validate_code(code, "test.py")
        assert result.passed is False
        assert any(i.issue_type == IssueType.SYNTAX_ERROR for i in result.issues)

    @pytest.mark.asyncio
    async def test_validate_unknown_language(self, pipeline):
        code = "hello world"
        result = await pipeline.validate_code(code, "test.txt")
        assert result.language == "unknown"

    @pytest.mark.asyncio
    async def test_validate_javascript(self, pipeline):
        code = "const x = 1;\nconsole.log(x);\n"
        result = await pipeline.validate_code(code, "test.js")
        assert result.language == "javascript"


class TestValidateFile:
    @pytest.mark.asyncio
    async def test_validate_file_too_large(self, tmp_path, pipeline):
        large_file = tmp_path / "big.py"
        # Create a file > 5MB
        large_file.write_text("x = 1\n" * 1_000_000)
        result = await pipeline.validate_file(str(large_file))
        assert result.passed is False
        assert len(result.issues) == 1
        assert "maximum size" in result.issues[0].message
        assert result.issues[0].severity == Severity.ERROR

    @pytest.mark.asyncio
    async def test_validate_file_decode_error(self, tmp_path, pipeline):
        bad_file = tmp_path / "bad.py"
        bad_file.write_bytes(b"\x80\x81\x82\x83")
        result = await pipeline.validate_file(str(bad_file))
        assert result.passed is False
        assert len(result.issues) == 1
        assert "Cannot decode" in result.issues[0].message

    @pytest.mark.asyncio
    async def test_validate_valid_file(self, tmp_path, pipeline):
        good_file = tmp_path / "good.py"
        good_file.write_text("x = 1\nprint(x)\n")
        result = await pipeline.validate_file(str(good_file))
        assert result.file == str(good_file)
        assert result.language == "python"


class TestPipelineLifecycle:
    @pytest.mark.asyncio
    async def test_close_no_error(self, pipeline):
        await pipeline.close()
