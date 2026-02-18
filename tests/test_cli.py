"""Tests for CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from hallucination_firewall.cli import _validate_url, main


@pytest.fixture
def runner():
    return CliRunner()


class TestCheckCommand:
    def test_check_no_args_exits_1(self, runner):
        result = runner.invoke(main, ["check"])
        assert result.exit_code == 1

    def test_check_valid_python_file(self, runner, tmp_path):
        f = tmp_path / "valid.py"
        f.write_text("x = 1\nprint(x)\n")
        result = runner.invoke(main, ["check", str(f)])
        # Should exit 0 for valid code
        assert result.exit_code == 0

    def test_check_invalid_code_exits_1(self, runner, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("def foo(\n")
        result = runner.invoke(main, ["check", str(f)])
        assert result.exit_code == 1

    def test_check_json_format(self, runner, tmp_path):
        f = tmp_path / "valid.py"
        f.write_text("x = 1\n")
        result = runner.invoke(main, ["check", str(f), "--format", "json"])
        assert result.exit_code == 0

    def test_check_stdin(self, runner):
        result = runner.invoke(main, ["check", "--stdin"], input="x = 1\n")
        assert result.exit_code == 0


class TestParseCommand:
    def test_parse_markdown_file(self, runner, tmp_path):
        f = tmp_path / "response.md"
        f.write_text("```python\nx = 1\n```\n")
        result = runner.invoke(main, ["parse", str(f)])
        assert result.exit_code == 0

    def test_parse_no_input_exits_1(self, runner):
        result = runner.invoke(main, ["parse"])
        assert result.exit_code == 1


class TestParseUrlValidation:
    def test_url_blocked_host_localhost(self):
        with pytest.raises(Exception, match="Blocked host"):
            _validate_url("http://localhost/secret")

    def test_url_blocked_host_private_ip(self):
        with pytest.raises(Exception, match="Blocked host"):
            _validate_url("http://169.254.169.254/metadata")

    def test_url_blocked_host_10_range(self):
        with pytest.raises(Exception, match="Blocked host"):
            _validate_url("http://10.0.0.1/internal")

    def test_url_blocked_host_192_168(self):
        with pytest.raises(Exception, match="Blocked host"):
            _validate_url("http://192.168.1.1/admin")

    def test_url_bad_scheme_file(self):
        with pytest.raises(Exception, match="Unsupported URL scheme"):
            _validate_url("file:///etc/passwd")

    def test_url_bad_scheme_ftp(self):
        with pytest.raises(Exception, match="Unsupported URL scheme"):
            _validate_url("ftp://example.com/file")

    def test_url_valid_https(self):
        result = _validate_url("https://example.com/page")
        assert result == "https://example.com/page"

    def test_url_valid_http(self):
        result = _validate_url("http://example.com/page")
        assert result == "http://example.com/page"


class TestInitCommand:
    def test_init_creates_config(self, runner, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(main, ["init"])
        assert result.exit_code == 0
        assert (tmp_path / ".firewall.toml").exists()

    def test_init_existing_config(self, runner, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".firewall.toml").write_text("[firewall]\n")
        result = runner.invoke(main, ["init"])
        assert "already exists" in result.output


class TestServeCommand:
    def test_serve_help(self, runner):
        result = runner.invoke(main, ["serve", "--help"])
        assert result.exit_code == 0
        assert "host" in result.output.lower()

    def test_serve_runs_uvicorn(self, runner, monkeypatch):
        mock_run = MagicMock()
        monkeypatch.setattr("uvicorn.run", mock_run)
        result = runner.invoke(main, ["serve", "--host", "0.0.0.0", "--port", "9000"])
        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs.get("host") or call_kwargs[1].get("host") == "0.0.0.0"


class TestCheckSarifFormat:
    def test_check_format_sarif(self, runner, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("def foo(\n")
        result = runner.invoke(main, ["check", str(f), "--format", "sarif"])
        # Syntax error → exit 1; SARIF output goes to sys.stdout directly
        assert result.exit_code == 1

    def test_check_format_sarif_valid(self, runner, tmp_path):
        f = tmp_path / "ok.py"
        f.write_text("x = 1\n")
        result = runner.invoke(main, ["check", str(f), "--format", "sarif"])
        assert result.exit_code == 0

    def test_check_multiple_files_summary(self, runner, tmp_path):
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_text("x = 1\n")
        f2.write_text("y = 2\n")
        result = runner.invoke(main, ["check", str(f1), str(f2)])
        assert result.exit_code == 0


class TestCheckCiMode:
    def test_check_ci_flag(self, runner, tmp_path):
        f = tmp_path / "valid.py"
        f.write_text("x = 1\nprint(x)\n")
        result = runner.invoke(main, ["check", str(f), "--ci"])
        # Valid code should still pass even in CI mode
        assert result.exit_code == 0


class TestParseExtended:
    def test_parse_format_json(self, runner, tmp_path):
        md = tmp_path / "response.md"
        md.write_text("```python\nimport os\n```\n")
        result = runner.invoke(main, ["parse", str(md), "--format", "json"])
        assert result.exit_code == 0

    def test_parse_stdin(self, runner):
        result = runner.invoke(main, ["parse", "--stdin"], input="```python\nimport os\n```\n")
        assert result.exit_code == 0

    def test_parse_failed_blocks_exit_1(self, runner, tmp_path):
        md = tmp_path / "bad.md"
        md.write_text("```python\ndef foo(\n```\n")
        result = runner.invoke(main, ["parse", str(md)])
        assert result.exit_code == 1

    def test_parse_url_fetch(self, runner, monkeypatch):
        mock_response = MagicMock()
        mock_response.text = "```python\nimport os\n```\n"
        mock_response.raise_for_status = MagicMock()
        monkeypatch.setattr("httpx.get", MagicMock(return_value=mock_response))
        result = runner.invoke(main, ["parse", "--url", "https://example.com/code.md"])
        assert result.exit_code == 0
