"""FastAPI server for the hallucination firewall API."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import load_config
from .models import ValidationResult
from .pipeline.runner import ValidationPipeline

logger = logging.getLogger(__name__)

RATE_LIMIT = 60  # requests per window
RATE_WINDOW = 60  # seconds


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple per-IP sliding-window rate limiter."""

    def __init__(self, app, limit: int = RATE_LIMIT, window: int = RATE_WINDOW):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        # Prune old timestamps
        recent = [t for t in self._requests[client_ip] if now - t < self.window]
        if not recent:
            self._requests.pop(client_ip, None)
            recent = []
        else:
            self._requests[client_ip] = recent
        if len(recent) >= self.limit:
            return JSONResponse(
                {"detail": "Rate limit exceeded"}, status_code=429
            )
        self._requests[client_ip].append(now)
        return await call_next(request)

pipeline: ValidationPipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage pipeline lifecycle."""
    global pipeline
    config = load_config()
    pipeline = ValidationPipeline(config)
    yield
    try:
        await pipeline.close()
    except Exception:
        logger.exception("Error closing pipeline during shutdown")


app = FastAPI(
    title="AI Hallucination Firewall",
    description="Validates AI-generated code against real sources",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware)


class ValidateRequest(BaseModel):
    """Request body for code validation."""

    code: str
    file_path: str = "<api>"
    language: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.post("/validate", response_model=ValidationResult)
async def validate(request: ValidateRequest) -> ValidationResult:
    """Validate code for hallucinated APIs and patterns."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    file_path = request.file_path
    if request.language:
        file_path = f"{file_path}.{request.language}"
    return await pipeline.validate_code(request.code, file_path)
