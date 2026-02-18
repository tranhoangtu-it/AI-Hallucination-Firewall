"""Tests for configuration loading."""

import tempfile
from pathlib import Path

from hallucination_firewall.config import load_config, find_config_file


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
