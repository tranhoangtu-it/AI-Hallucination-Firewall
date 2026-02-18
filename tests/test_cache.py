"""Tests for registry cache."""

import tempfile
from pathlib import Path

from hallucination_firewall.registries.cache import RegistryCache


def test_cache_set_and_get():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = RegistryCache(Path(tmpdir), ttl_seconds=3600)
        cache.set("test_key", {"name": "test"})
        result = cache.get("test_key")
        assert result == {"name": "test"}


def test_cache_miss():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = RegistryCache(Path(tmpdir), ttl_seconds=3600)
        result = cache.get("nonexistent")
        assert result is None


def test_cache_expired():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = RegistryCache(Path(tmpdir), ttl_seconds=0)  # instant expiry
        cache.set("test_key", "value")
        import time
        time.sleep(0.1)
        result = cache.get("test_key")
        assert result is None


def test_cache_delete():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = RegistryCache(Path(tmpdir), ttl_seconds=3600)
        cache.set("key1", "val1")
        cache.delete("key1")
        assert cache.get("key1") is None


def test_cache_overwrite():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = RegistryCache(Path(tmpdir), ttl_seconds=3600)
        cache.set("key1", "val1")
        cache.set("key1", "val2")
        assert cache.get("key1") == "val2"
