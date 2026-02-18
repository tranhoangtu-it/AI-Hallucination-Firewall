"""Tests for API server."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

import hallucination_firewall.server as server_module
from hallucination_firewall.server import app
from hallucination_firewall.pipeline.runner import ValidationPipeline


@pytest.fixture(autouse=True)
def _init_pipeline():
    """Initialize the global pipeline for tests."""
    server_module.pipeline = ValidationPipeline()
    yield
    server_module.pipeline = None


@pytest.fixture
def transport():
    return ASGITransport(app=app)


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self, transport):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestValidateEndpoint:
    @pytest.mark.asyncio
    async def test_validate_valid_code(self, transport):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/validate",
                json={"code": "x = 1\nprint(x)\n", "file_path": "test.py"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "passed" in data

    @pytest.mark.asyncio
    async def test_validate_syntax_error(self, transport):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/validate",
                json={"code": "def foo(\n", "file_path": "test.py"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["passed"] is False

    @pytest.mark.asyncio
    async def test_validate_missing_code_field(self, transport):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/validate", json={"file_path": "test.py"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_validate_with_language(self, transport):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/validate",
                json={
                    "code": "const x = 1;\n",
                    "file_path": "test",
                    "language": "js",
                },
            )
        assert resp.status_code == 200


class TestRateLimiting:
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, transport):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            for _ in range(60):
                await client.get("/health")
            resp = await client.get("/health")
        assert resp.status_code == 429
        assert "rate limit" in resp.json()["detail"].lower()
