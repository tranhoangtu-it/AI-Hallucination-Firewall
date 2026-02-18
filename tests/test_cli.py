"""Tests for CLI commands."""

from __future__ import annotations

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
