"""npm registry client for verifying JavaScript/TypeScript package existence."""

from __future__ import annotations

import httpx

from ..models import RegistryConfig
from .cache import RegistryCache

NPM_REGISTRY_URL = "https://registry.npmjs.org"


class NpmRegistry:
    """Client for querying npm package metadata."""

    def __init__(self, config: RegistryConfig, cache: RegistryCache) -> None:
        self.config = config
        self.cache = cache
        self.client = httpx.AsyncClient(timeout=config.timeout_seconds)

    async def package_exists(self, package_name: str) -> bool:
        """Check if a package exists on npm."""
        if not package_name or not package_name.strip():
            return False

        cache_key = f"npm:exists:{package_name}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            response = await self.client.get(f"{NPM_REGISTRY_URL}/{package_name}")
            exists = response.status_code == 200
            self.cache.set(cache_key, exists)
            return exists
        except httpx.HTTPError:
            return True  # fail open

    async def get_package_info(self, package_name: str) -> dict | None:
        """Get package metadata from npm."""
        cache_key = f"npm:info:{package_name}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            response = await self.client.get(f"{NPM_REGISTRY_URL}/{package_name}")
            if response.status_code != 200:
                return None
            data = response.json()
            latest = data.get("dist-tags", {}).get("latest", "")
            info = {
                "name": data.get("name", package_name),
                "version": latest,
                "description": data.get("description", ""),
            }
            self.cache.set(cache_key, info)
            return info
        except httpx.HTTPError:
            return None

    async def close(self) -> None:
        await self.client.aclose()
