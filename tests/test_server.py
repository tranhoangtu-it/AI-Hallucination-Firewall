"""Tests for API server."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

import hallucination_firewall.server as server_module
from hallucination_firewall.pipeline.runner import ValidationPipeline
from hallucination_firewall.server import MetricsCollector, app, lifespan


def _find_rate_limiter(obj, depth=5):
    """Walk ASGI middleware stack to find RateLimitMiddleware instance."""
    from hallucination_firewall.server import RateLimitMiddleware

    if isinstance(obj, RateLimitMiddleware):
        return obj
    if depth <= 0:
        return None
    inner = getattr(obj, "app", None)
    if inner is not None:
        return _find_rate_limiter(inner, depth - 1)
    return None


@pytest.fixture(autouse=True)
def _init_pipeline():
    """Initialize the global pipeline and reset rate limiter + metrics for tests."""
    server_module.pipeline = ValidationPipeline()
    # Reset rate limiter state between tests
    rl = _find_rate_limiter(app.middleware_stack)
    if rl:
        rl._requests.clear()
    # Reset global metrics to avoid state leak between tests
    server_module.metrics = MetricsCollector()
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


class TestMetricsCollector:
    def test_record_request_error(self):
        m = MetricsCollector()
        m.record_request(latency_ms=100, is_error=True)
        assert m.error_count == 1
        assert m.request_count == 1

    def test_latency_histogram_buckets(self):
        m = MetricsCollector()
        m.record_request(50, False)
        assert m.latency_histogram["<100ms"] == 1
        m.record_request(200, False)
        assert m.latency_histogram["<500ms"] == 1
        m.record_request(800, False)
        assert m.latency_histogram["<1000ms"] == 1
        m.record_request(2000, False)
        assert m.latency_histogram[">1000ms"] == 1

    def test_cache_hit_miss(self):
        m = MetricsCollector()
        m.record_cache_hit()
        m.record_cache_miss()
        assert m.cache_hits == 1
        assert m.cache_misses == 1

    def test_get_metrics_zero_requests(self):
        m = MetricsCollector()
        data = m.get_metrics()
        assert data["avg_latency_ms"] == 0
        assert data["cache_hit_rate"] == 0

    def test_get_metrics_avg_latency(self):
        m = MetricsCollector()
        m.record_request(100, False)
        m.record_request(200, False)
        data = m.get_metrics()
        assert data["avg_latency_ms"] == 150.0

    def test_get_metrics_cache_hit_rate(self):
        m = MetricsCollector()
        m.record_cache_hit()
        m.record_cache_hit()
        m.record_cache_miss()
        data = m.get_metrics()
        assert data["cache_hit_rate"] == pytest.approx(0.667, abs=0.001)


class TestLifespan:
    @pytest.mark.asyncio
    async def test_lifespan_startup_shutdown(self, monkeypatch):
        mock_pipeline = MagicMock()
        mock_pipeline.close = AsyncMock()
        mock_pipeline.cache = MagicMock()
        mock_pipeline.cache.get = MagicMock(return_value=None)

        monkeypatch.setattr(
            "hallucination_firewall.server.load_config",
            lambda *a, **kw: MagicMock(),
        )
        monkeypatch.setattr(
            "hallucination_firewall.server.ValidationPipeline",
            lambda *a, **kw: mock_pipeline,
        )

        async with lifespan(None):
            assert server_module.pipeline is not None

        mock_pipeline.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_exception(self, monkeypatch, caplog):
        mock_pipeline = MagicMock()
        mock_pipeline.close = AsyncMock(side_effect=RuntimeError("cleanup error"))
        mock_pipeline.cache = MagicMock()
        mock_pipeline.cache.get = MagicMock(return_value=None)

        monkeypatch.setattr(
            "hallucination_firewall.server.load_config",
            lambda *a, **kw: MagicMock(),
        )
        monkeypatch.setattr(
            "hallucination_firewall.server.ValidationPipeline",
            lambda *a, **kw: mock_pipeline,
        )

        with caplog.at_level(logging.ERROR):
            async with lifespan(None):
                pass

        assert "Error closing pipeline" in caplog.text


class TestPipelineNone:
    @pytest.mark.asyncio
    async def test_validate_returns_503_when_pipeline_none(self, transport, monkeypatch):
        monkeypatch.setattr(server_module, "pipeline", None)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/validate", json={"code": "x = 1", "language": "python"}
            )
        assert resp.status_code == 503


class TestMetricsEndpoint:
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, transport):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "request_count" in data
        assert "cache_hits" in data
        assert "latency_histogram" in data
