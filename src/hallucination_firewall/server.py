"""FastAPI server for the hallucination firewall API."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import load_config
from .models import ValidationResult
from .pipeline.runner import ValidationPipeline

logger = logging.getLogger(__name__)

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
