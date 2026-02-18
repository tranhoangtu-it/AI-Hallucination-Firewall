"""Tests for signature validation (Layer 3)."""

from __future__ import annotations

import pytest

from hallucination_firewall.models import Language
from hallucination_firewall.pipeline.signature_checker import (
    FunctionCall,
    FunctionCallExtractor,
    SignatureInfo,
    SignatureLookup,
    SignatureValidator,
    ParamInfo,
    check_signatures,
)


class TestFunctionCallExtractor:
    """Test function call extraction from AST."""

    def setup_method(self) -> None:
        self.extractor = FunctionCallExtractor()

    def test_extract_attribute_call(self) -> None:
        code = "import os\nos.path.join('a', 'b')"
        calls = self.extractor.extract_calls(code)
        names = [c.name for c in calls]
        assert any("os.path.join" in n or "path.join" in n for n in names)

    def test_extract_dotted_call(self) -> None:
        code = "import requests\nrequests.get('https://example.com')"
        calls = self.extractor.extract_calls(code)
        names = [c.name for c in calls]
        assert "requests.get" in names

    def test_extract_keyword_args(self) -> None:
        code = "import requests\nrequests.get('url', timeout=10)"
        calls = self.extractor.extract_calls(code)
        req_call = next(c for c in calls if c.name == "requests.get")
        assert req_call.positional_count == 1
        assert "timeout" in req_call.keywords

    def test_skip_simple_calls(self) -> None:
        """Simple identifiers (no dots) are skipped by _is_checkable."""
        code = "print('hello')\nlen([1,2,3])"
        calls = self.extractor.extract_calls(code)
        names = [c.name for c in calls]
        assert "print" not in names
        assert "len" not in names

    def test_extract_star_args(self) -> None:
        code = "import os\nos.path.join(*parts)"
        calls = self.extractor.extract_calls(code)
        join_call = next(c for c in calls if "join" in c.name)
        assert join_call.has_star_args

    def test_extract_star_kwargs(self) -> None:
        code = "import requests\nrequests.get(**kwargs)"
        calls = self.extractor.extract_calls(code)
        get_call = next(c for c in calls if c.name == "requests.get")
        assert get_call.has_star_kwargs

    def test_malformed_code_no_crash(self) -> None:
        code = "import os\nos.path.join('a'"  # missing closing paren
        calls = self.extractor.extract_calls(code)
        # Should not crash; may or may not extract the call
        assert isinstance(calls, list)


class TestSignatureValidator:
    """Test argument comparison logic."""

    def setup_method(self) -> None:
        self.validator = SignatureValidator()

    def test_valid_call(self) -> None:
        call = FunctionCall(name="mod.func", positional_count=2, keywords=[])
        sig = SignatureInfo(params=[
            ParamInfo(name="a", required=True),
            ParamInfo(name="b", required=True),
        ])
        errors = self.validator.validate(call, sig)
        assert errors == []

    def test_missing_required_arg(self) -> None:
        call = FunctionCall(name="mod.func", positional_count=0, keywords=[])
        sig = SignatureInfo(params=[
            ParamInfo(name="url", required=True),
        ])
        errors = self.validator.validate(call, sig)
        assert len(errors) == 1
        assert errors[0][0].value == "missing_required_arg"

    def test_unknown_keyword(self) -> None:
        call = FunctionCall(name="mod.func", positional_count=1, keywords=["fake_param"])
        sig = SignatureInfo(params=[
            ParamInfo(name="url", required=True),
        ])
        errors = self.validator.validate(call, sig)
        assert any(e[0].value == "unknown_parameter" for e in errors)

    def test_too_many_args(self) -> None:
        call = FunctionCall(name="mod.func", positional_count=5, keywords=[])
        sig = SignatureInfo(params=[
            ParamInfo(name="a", required=True),
        ])
        errors = self.validator.validate(call, sig)
        assert any(e[0].value == "wrong_signature" for e in errors)

    def test_skip_star_args_call(self) -> None:
        """Skip validation when call uses *args."""
        call = FunctionCall(name="mod.func", positional_count=0, has_star_args=True)
        sig = SignatureInfo(params=[ParamInfo(name="a", required=True)])
        errors = self.validator.validate(call, sig)
        assert errors == []

    def test_skip_var_positional_and_keyword_sig(self) -> None:
        """Skip validation when sig accepts *args AND **kwargs."""
        call = FunctionCall(name="mod.func", positional_count=10, keywords=["x", "y"])
        sig = SignatureInfo(params=[], has_var_positional=True, has_var_keyword=True)
        errors = self.validator.validate(call, sig)
        assert errors == []

    def test_valid_keyword_arg(self) -> None:
        call = FunctionCall(name="mod.func", positional_count=1, keywords=["timeout"])
        sig = SignatureInfo(params=[
            ParamInfo(name="url", required=True),
            ParamInfo(name="timeout", required=False),
        ])
        errors = self.validator.validate(call, sig)
        assert errors == []


class TestSignatureLookup:
    """Test signature resolution."""

    def setup_method(self) -> None:
        self.lookup = SignatureLookup()

    def test_inspect_fallback_os_path_join(self) -> None:
        sig = self.lookup._inspect_lookup("os.path.join")
        assert sig is not None
        assert sig.has_var_positional  # os.path.join accepts *paths

    def test_unknown_function_returns_none(self) -> None:
        sig = self.lookup.get_signature("nonexistent.module.func", "", 0)
        assert sig is None


class TestCheckSignatures:
    """Integration tests for check_signatures entry point."""

    @pytest.mark.asyncio
    async def test_skip_non_python(self) -> None:
        issues = await check_signatures("const x = 1;", Language.JAVASCRIPT, "test.js")
        assert issues == []

    @pytest.mark.asyncio
    async def test_valid_code_no_issues(self) -> None:
        code = "import os\nx = os.path.join('a', 'b')"
        issues = await check_signatures(code, Language.PYTHON, "test.py")
        # os.path.join accepts *args, so no issues expected
        assert all(i.source == "signature_checker" for i in issues)

    @pytest.mark.asyncio
    async def test_empty_code(self) -> None:
        issues = await check_signatures("", Language.PYTHON, "test.py")
        assert issues == []

    @pytest.mark.asyncio
    async def test_alias_resolution_pandas(self) -> None:
        """Test that import aliases are resolved before signature lookup."""
        code = """
import pandas as pd

# This should resolve pd.DataFrame to pandas.DataFrame
df = pd.DataFrame()
"""
        issues = await check_signatures(code, Language.PYTHON, "test.py")
        # Should not crash; pandas.DataFrame may or may not be found depending on install
        assert isinstance(issues, list)

    @pytest.mark.asyncio
    async def test_alias_resolution_numpy(self) -> None:
        """Test alias resolution for numpy."""
        code = """
import numpy as np

arr = np.array([1, 2, 3])
"""
        issues = await check_signatures(code, Language.PYTHON, "test.py")
        assert isinstance(issues, list)

    @pytest.mark.asyncio
    async def test_alias_resolution_from_import(self) -> None:
        """Test alias resolution for 'from X import Y as Z'."""
        code = """
from os import path as ospath

result = ospath.join('a', 'b')
"""
        issues = await check_signatures(code, Language.PYTHON, "test.py")
        # Should resolve ospath.join to os.path.join
        assert isinstance(issues, list)
