"""Tests for PyPI registry client — covers all branches."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from hallucination_firewall.models import RegistryConfig
from hallucination_firewall.registries.pypi_registry import PyPIRegistry


@pytest.fixture
def mock_cache():
    cache = MagicMock()
    cache.get.return_value = None
    return cache


@pytest.fixture
def registry(mock_cache):
    config = RegistryConfig()
    reg = PyPIRegistry(config=config, cache=mock_cache)
    reg.client = AsyncMock()
    return reg


# --- package_exists ---


@pytest.mark.asyncio
async def test_package_exists_empty_name(registry):
    assert await registry.package_exists("") is False


@pytest.mark.asyncio
async def test_package_exists_whitespace_name(registry):
    assert await registry.package_exists("   ") is False


@pytest.mark.asyncio
async def test_package_exists_cache_hit(registry, mock_cache):
    mock_cache.get.return_value = True
    result = await registry.package_exists("requests")
    assert result is True
    registry.client.get.assert_not_called()


@pytest.mark.asyncio
async def test_package_exists_http_200(registry, mock_cache):
    mock_response = MagicMock(status_code=200)
    registry.client.get = AsyncMock(return_value=mock_response)
    result = await registry.package_exists("requests")
    assert result is True
    mock_cache.set.assert_called_with("pypi:exists:requests", True)


@pytest.mark.asyncio
async def test_package_exists_http_404(registry, mock_cache):
    mock_response = MagicMock(status_code=404)
    registry.client.get = AsyncMock(return_value=mock_response)
    result = await registry.package_exists("fake-pkg-xyz")
    assert result is False
    mock_cache.set.assert_called_with("pypi:exists:fake-pkg-xyz", False)


@pytest.mark.asyncio
async def test_package_exists_network_error(registry, mock_cache):
    registry.client.get = AsyncMock(side_effect=httpx.ConnectError("timeout"))
    result = await registry.package_exists("requests")
    assert result is True  # fail open
    mock_cache.set.assert_not_called()


# --- get_package_info ---


@pytest.mark.asyncio
async def test_get_package_info_cache_hit(registry, mock_cache):
    cached = {"name": "requests", "version": "2.31.0"}
    mock_cache.get.return_value = cached
    result = await registry.get_package_info("requests")
    assert result == cached


@pytest.mark.asyncio
async def test_get_package_info_http_200(registry, mock_cache):
    mock_response = MagicMock(status_code=200)
    mock_response.json.return_value = {
        "info": {
            "name": "requests",
            "version": "2.31.0",
            "summary": "HTTP library",
            "requires_python": ">=3.7",
        }
    }
    registry.client.get = AsyncMock(return_value=mock_response)
    result = await registry.get_package_info("requests")
    assert result["name"] == "requests"
    assert result["version"] == "2.31.0"
    assert result["summary"] == "HTTP library"
    assert result["requires_python"] == ">=3.7"
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_package_info_http_404(registry, mock_cache):
    mock_response = MagicMock(status_code=404)
    registry.client.get = AsyncMock(return_value=mock_response)
    result = await registry.get_package_info("fake-pkg")
    assert result is None


@pytest.mark.asyncio
async def test_get_package_info_network_error(registry, mock_cache):
    registry.client.get = AsyncMock(side_effect=httpx.HTTPError("timeout"))
    result = await registry.get_package_info("requests")
    assert result is None
