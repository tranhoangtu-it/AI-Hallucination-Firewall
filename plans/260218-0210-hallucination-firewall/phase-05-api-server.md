# Phase 5: API Server (FastAPI)

## Context
- [Plan Overview](./plan.md)
- [Phase 3: Validation Pipeline](./phase-03-validation-pipeline.md)

## Overview
- **Priority:** P2
- **Status:** pending
- **Effort:** 3h
- **Depends on:** Phase 3 (pipeline must work)
- **Parallel with:** Phase 4 (CLI)
- **Description:** FastAPI REST server for CI/CD integration. Accepts code, returns validation results as JSON.

## Key Insights
- FastAPI auto-generates OpenAPI docs at `/docs` — free API documentation
- Pydantic models shared between pipeline and API — no duplication
- Async endpoint naturally fits the async pipeline
- Rate limiting optional for MVP (defer to reverse proxy in prod)

## Requirements
- **Functional:** POST `/validate` endpoint, GET `/health`, configurable host/port
- **Non-functional:** Async request handling, <2s response time, OpenAPI docs

## Architecture

```
server.py
├── POST /validate       Accept code + language → return ValidationResult
├── GET  /health         Health check endpoint
└── GET  /docs           Auto-generated OpenAPI docs (FastAPI built-in)
```

## Related Code Files
- **Create:** `src/hallucination_firewall/server.py`

## Implementation Steps

### 5.1 Request/Response Models

```python
from pydantic import BaseModel, Field

class ValidateRequest(BaseModel):
    code: str = Field(..., description="Code to validate")
    language: str = Field(default="python", description="Programming language")
    file_path: str = Field(default="<stdin>", description="Virtual file path")

class ValidateResponse(BaseModel):
    file_path: str
    language: str
    issues: list[Issue]
    duration_ms: float
    has_errors: bool
    error_count: int
    warning_count: int
```

### 5.2 FastAPI App (`server.py`)

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load config, create pipeline
    app.state.config = load_config()
    app.state.pipeline = create_pipeline(app.state.config)
    yield
    # Shutdown: cleanup

app = FastAPI(
    title="AI Hallucination Firewall",
    description="Validate AI-generated code for hallucinations",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/validate", response_model=ValidateResponse)
async def validate(request: ValidateRequest):
    result = await app.state.pipeline.run(
        code=request.code,
        language=request.language,
        file_path=request.file_path,
    )
    return ValidateResponse(
        file_path=result.file_path,
        language=result.language,
        issues=result.issues,
        duration_ms=result.duration_ms,
        has_errors=result.has_errors,
        error_count=result.error_count,
        warning_count=result.warning_count,
    )
```

### 5.3 Integration with CLI

The `firewall serve` command in cli.py starts this server:
```python
uvicorn.run("hallucination_firewall.server:app", host=host, port=port)
```

### 5.4 Error Handling

- Invalid language → 422 (Pydantic validation)
- Pipeline internal error → 500 with error detail
- Empty code → 400 with message

## Todo List
- [ ] Create ValidateRequest and ValidateResponse models
- [ ] Implement FastAPI app with lifespan handler
- [ ] Implement POST /validate endpoint
- [ ] Implement GET /health endpoint
- [ ] Add error handling middleware
- [ ] Verify OpenAPI docs render at /docs
- [ ] Test with curl: `curl -X POST localhost:8000/validate -d '{"code":"import fakelib","language":"python"}'`

## Success Criteria
- `firewall serve` starts server on 127.0.0.1:8000
- POST `/validate` with Python code returns JSON with issues
- GET `/health` returns `{"status": "ok"}`
- GET `/docs` shows interactive Swagger UI
- Invalid requests return proper 4xx errors
- Server handles concurrent requests without blocking

## Risk Assessment
- FastAPI lifespan is the modern pattern (replaces on_event) → already using it
- Large code payloads could be slow → add max code size limit (e.g., 100KB)
- No auth on MVP → document that auth should be added before public deployment
