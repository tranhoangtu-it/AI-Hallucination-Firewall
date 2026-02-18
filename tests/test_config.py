"""Tests for configuration loading."""

import tempfile
from pathlib import Path

from hallucination_firewall.config import find_config_file, load_config


def test_load_default_config():
    config = load_config()
    assert config.cache_ttl_seconds == 3600
    assert config.registries.pypi_enabled is True


def test_load_config_from_toml():
    with tempfile.NamedTemporaryFile(suffix=".toml", mode="w", delete=False) as f:
        f.write('[firewall]\ncache_ttl_seconds = 7200\n')
        f.flush()
        config = load_config(Path(f.name))
    assert config.cache_ttl_seconds == 7200


def test_find_config_nonexistent():
    result = find_config_file(Path("/tmp/nonexistent_dir_12345"))
    assert result is None


def test_load_config_missing_file():
    config = load_config(Path("/tmp/nonexistent.toml"))
    # Should return defaults
    assert config.cache_ttl_seconds == 3600


def test_find_config_file_found(tmp_path):
    """find_config_file returns path when .firewall.toml exists."""
    config_file = tmp_path / ".firewall.toml"
    config_file.write_text('[firewall]\nlanguages = ["python"]\n')
    result = find_config_file(tmp_path)
    assert result == config_file


def test_load_config_ci_env_firewall(tmp_path, monkeypatch):
    """FIREWALL_CI=1 enables ci_mode."""
    monkeypatch.setenv("FIREWALL_CI", "1")
    config = load_config(tmp_path / "nonexistent.toml")
    assert config.ci_mode is True


def test_load_config_ci_env_generic(tmp_path, monkeypatch):
    """CI=true enables ci_mode."""
    monkeypatch.setenv("CI", "true")
    # Ensure FIREWALL_CI is not set
    monkeypatch.delenv("FIREWALL_CI", raising=False)
    config = load_config(tmp_path / "nonexistent.toml")
    assert config.ci_mode is True
