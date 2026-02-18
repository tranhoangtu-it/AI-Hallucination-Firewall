"""SQLite cache for package registry metadata."""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RegistryCache:
    """SQLite-backed cache for registry lookups with TTL support."""

    def __init__(self, cache_dir: Path, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = cache_dir / "registry_cache.db"
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        """Create a connection with WAL mode for concurrent access."""
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)

    def get(self, key: str) -> Any | None:
        """Get cached value if not expired."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value, created_at FROM cache WHERE key = ?", (key,)
            ).fetchone()

        if row is None:
            return None

        value, created_at = row
        if time.time() - created_at > self.ttl_seconds:
            self.delete(key)
            return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Corrupted cache entry for key '%s', removing", key)
            self.delete(key)
            return None

    def set(self, key: str, value: Any) -> None:
        """Store value in cache."""
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, created_at) VALUES (?, ?, ?)",
                (key, json.dumps(value), time.time()),
            )

    def delete(self, key: str) -> None:
        """Remove key from cache."""
        with self._connect() as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))

    def clear_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        cutoff = time.time() - self.ttl_seconds
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM cache WHERE created_at < ?", (cutoff,))
            return cursor.rowcount
