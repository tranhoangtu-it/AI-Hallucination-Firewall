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


def test_cache_corrupted_json():
    """Corrupted JSON entry is deleted and returns None."""
    import sqlite3

    with tempfile.TemporaryDirectory() as tmpdir:
        cache = RegistryCache(Path(tmpdir), ttl_seconds=3600)
        db_path = Path(tmpdir) / "registry_cache.db"
        # Insert invalid JSON directly into the DB
        conn = sqlite3.connect(str(db_path))
        import time

        conn.execute(
            "INSERT OR REPLACE INTO cache (key, value, created_at) VALUES (?, ?, ?)",
            ("bad_key", "{invalid json", time.time()),
        )
        conn.commit()
        conn.close()

        # get() should return None and delete the corrupted entry
        result = cache.get("bad_key")
        assert result is None
        # Verify entry was removed
        result2 = cache.get("bad_key")
        assert result2 is None


def test_cache_clear_expired():
    """clear_expired removes expired entries and returns count."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Insert with TTL=0 (immediately expired)
        cache_expired = RegistryCache(Path(tmpdir), ttl_seconds=0)
        cache_expired.set("exp1", True)
        cache_expired.set("exp2", False)

        import time

        time.sleep(0.1)  # ensure they are past TTL=0

        count = cache_expired.clear_expired()
        assert count == 2
        assert cache_expired.get("exp1") is None
        assert cache_expired.get("exp2") is None
