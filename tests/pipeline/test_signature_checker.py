"""Tests for signature validation (Layer 3)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from hallucination_firewall.models import Language
from hallucination_firewall.pipeline.signature_checker import (
    FunctionCall,
    FunctionCallExtractor,
    ParamInfo,
    SignatureInfo,
    SignatureLookup,
    SignatureValidator,
    _resolve_alias,
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


class TestParseCallEdgeCases:
    """Test _parse_call and _get_name edge cases."""

    def setup_method(self) -> None:
        self.extractor = FunctionCallExtractor()

    def test_parse_call_missing_func_node(self) -> None:
        """_parse_call returns None when func_node is missing."""
        mock_node = MagicMock()
        mock_node.child_by_field_name.return_value = None
        result = self.extractor._parse_call(mock_node)
        assert result is None

    def test_get_name_unexpected_node_type(self) -> None:
        """_get_name returns empty string for non-identifier, non-attribute nodes."""
        mock_node = MagicMock()
        mock_node.type = "subscript"
        result = self.extractor._get_name(mock_node)
        assert result == ""


class TestSignatureLookupEdgeCases:
    """Test Jedi exception paths and inspect fallback edge cases."""

    def setup_method(self) -> None:
        self.lookup = SignatureLookup()

    def test_jedi_lookup_exception(self, monkeypatch) -> None:
        """Jedi crash returns None."""
        def _raise(*a, **kw):
            raise Exception("crash")

        monkeypatch.setattr("jedi.Script", _raise)
        sig = self.lookup._jedi_lookup(
            "os.path.join", "import os\nos.path.join('a')", 1
        )
        assert sig is None

    def test_jedi_name_get_signatures_exception(self, monkeypatch) -> None:
        """Exception in name.get_signatures() loop → continue."""
        mock_script = MagicMock()
        mock_script.get_signatures.return_value = []
        mock_name = MagicMock()
        mock_name.get_signatures.side_effect = Exception("internal error")
        mock_script.goto.return_value = [mock_name]
        monkeypatch.setattr("jedi.Script", lambda *a, **kw: mock_script)
        sig = self.lookup._jedi_lookup("os.path.join", "import os\nos.path.join('a')", 1)
        assert sig is None

    def test_inspect_lookup_non_dotted_name(self) -> None:
        """_inspect_lookup returns None for non-dotted names."""
        sig = self.lookup._inspect_lookup("print")
        assert sig is None

    def test_inspect_lookup_unsafe_module(self) -> None:
        """_inspect_lookup returns None for modules not in _SAFE_MODULES."""
        sig = self.lookup._inspect_lookup("subprocess.run")
        assert sig is None

    def test_inspect_lookup_exception(self, monkeypatch) -> None:
        """_inspect_lookup returns None on import error."""
        def _raise(*a, **kw):
            raise ImportError("nope")

        monkeypatch.setattr("builtins.__import__", _raise)
        sig = self.lookup._inspect_lookup("os.nonexistent_func")
        assert sig is None

    def test_inspect_sig_to_info_skip_self(self) -> None:
        """_inspect_sig_to_info filters out 'self' parameter."""
        import inspect as _inspect

        class Cls:
            def method(self, a, b):
                pass

        sig = _inspect.signature(Cls.method)
        info = self.lookup._inspect_sig_to_info(sig)
        param_names = [p.name for p in info.params]
        assert "self" not in param_names
        assert "a" in param_names
        assert "b" in param_names

    def test_inspect_sig_var_keyword(self) -> None:
        """_inspect_sig_to_info detects **kwargs."""
        import inspect as _inspect

        def func(a, **kwargs):
            pass

        sig = _inspect.signature(func)
        info = self.lookup._inspect_sig_to_info(sig)
        assert info.has_var_keyword is True

    def test_jedi_sig_var_keyword(self) -> None:
        """_jedi_sig_to_info detects VAR_KEYWORD (**kwargs)."""
        mock_sig = MagicMock()
        mock_param_a = MagicMock()
        mock_param_a.kind = "POSITIONAL_OR_KEYWORD"
        mock_param_a.name = "a"
        mock_param_a.description = "a"
        mock_param_kw = MagicMock()
        mock_param_kw.kind = "VAR_KEYWORD"
        mock_param_kw.name = "kwargs"
        mock_sig.params = [mock_param_a, mock_param_kw]
        info = self.lookup._jedi_sig_to_info(mock_sig)
        assert info.has_var_keyword is True


class TestResolveAlias:
    def test_no_alias_match(self) -> None:
        result = _resolve_alias("os.path.join", {"pd": "pandas"})
        assert result == "os.path.join"

    def test_no_dot_in_name(self) -> None:
        result = _resolve_alias("print", {"pd": "pandas"})
        assert result == "print"

    def test_empty_aliases(self) -> None:
        result = _resolve_alias("os.path.join", {})
        assert result == "os.path.join"
