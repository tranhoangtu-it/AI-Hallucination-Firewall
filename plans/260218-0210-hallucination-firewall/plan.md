---
title: "AI Hallucination Firewall Implementation"
description: "Python CLI + API server that validates AI-generated code for hallucinated functions, deprecated APIs, and invalid patterns"
status: pending
priority: P1
effort: 20h
branch: main
tags: [python, cli, fastapi, validation, tree-sitter, ast]
created: 2026-02-18
---

# AI Hallucination Firewall — Implementation Plan

## Goal
Build a Python CLI tool + API server that detects hallucinated functions, deprecated usage, invalid patterns, wrong signatures, and nonexistent packages in AI-generated code.

## Phase Overview

| Phase | Name | Effort | Depends On | Status |
|-------|------|--------|------------|--------|
| 1 | Project Setup & Scaffolding | 2h | — | pending |
| 2 | Core Models & Configuration | 2h | Phase 1 | pending |
| 3 | Validation Pipeline | 8h | Phase 2 | pending |
| 4 | CLI Interface (Click + Rich) | 3h | Phase 3 | pending |
| 5 | API Server (FastAPI) | 3h | Phase 3 | pending |
| 6 | Testing | 2h | Phases 3-5 | pending |

## Parallelization Map

```
Phase 1 (setup)
    └── Phase 2 (models/config)
            └── Phase 3 (pipeline)
                    ├── Phase 4 (CLI)      ← PARALLEL
                    └── Phase 5 (API)      ← PARALLEL
                            └── Phase 6 (tests) — after 4 & 5
```

- **Phases 4 & 5** can run in PARALLEL (both depend only on Phase 3)
- **Phase 6** runs after Phases 4 & 5 complete

## Key Architecture Decisions

1. **tree-sitter** for multi-language AST parsing (fast, 40+ langs)
2. **Layered pipeline**: AST → imports → signatures → deprecation
3. **Fail-open**: unknown patterns produce warnings, not errors
4. **SQLite cache**: registry responses cached with 1h TTL
5. **Async HTTP**: httpx for non-blocking registry queries
6. **Plugin-ready**: validators are independent, pluggable classes

## Research Reports
- [Code Validation Approaches](../reports/researcher-260218-0207-code-validation-approaches.md)
- [Hallucination Detection Patterns](../reports/researcher-260218-0207-hallucination-detection-patterns.md)

## Phase Details
- [Phase 1: Project Setup](./phase-01-project-setup.md)
- [Phase 2: Core Models & Config](./phase-02-core-models-and-config.md)
- [Phase 3: Validation Pipeline](./phase-03-validation-pipeline.md)
- [Phase 4: CLI Interface](./phase-04-cli-interface.md)
- [Phase 5: API Server](./phase-05-api-server.md)
- [Phase 6: Testing](./phase-06-testing.md)
