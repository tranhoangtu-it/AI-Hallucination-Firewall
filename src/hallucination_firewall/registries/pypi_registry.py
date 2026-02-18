"""PyPI registry client for verifying Python package existence and metadata."""

from __future__ import annotations

import httpx

from ..models import RegistryConfig
from .cache import RegistryCache

PYPI_BASE_URL = "https://pypi.org/pypi"


class PyPIRegistry:
    """Client for querying PyPI package metadata."""

    def __init__(self, config: RegistryConfig, cache: RegistryCache) -> None:
        self.config = config
        self.cache = cache
        self.client = httpx.AsyncClient(timeout=config.timeout_seconds)

    async def package_exists(self, package_name: str) -> bool:
        """Check if a package exists on PyPI."""
        if not package_name or not package_name.strip():
            return False

        cache_key = f"pypi:exists:{package_name}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            response = await self.client.get(f"{PYPI_BASE_URL}/{package_name}/json")
            exists = response.status_code == 200
            self.cache.set(cache_key, exists)
            return exists
        except httpx.HTTPError:
            # Network error — don't cache, return True (fail open)
            return True

    async def get_package_info(self, package_name: str) -> dict | None:
        """Get package metadata from PyPI."""
        cache_key = f"pypi:info:{package_name}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            response = await self.client.get(f"{PYPI_BASE_URL}/{package_name}/json")
            if response.status_code != 200:
                return None
            data = response.json()
            # Cache only essential fields
            info = {
                "name": data["info"]["name"],
                "version": data["info"]["version"],
                "summary": data["info"]["summary"],
                "requires_python": data["info"]["requires_python"],
            }
            self.cache.set(cache_key, info)
            return info
        except httpx.HTTPError:
            return None

    async def close(self) -> None:
        await self.client.aclose()
