---
title: "Four Major Features for Hallucination Firewall"
description: "Add signature validation, LLM parser, pre-commit hook, and VS Code extension"
status: complete
priority: P1
effort: 16h
branch: main
tags: [signature-validation, llm-parser, pre-commit, vscode-extension]
created: 2026-02-18
---

# Implementation Plan: Four Major Features

## Overview

Add four critical features to AI Hallucination Firewall to complete the validation pipeline and enable seamless integration into development workflows.

## Architecture Summary

Current: AST (tree-sitter) → Import Check (PyPI/npm) → **[Missing Layer 3]**

New: AST → Import Check → **Signature Validation** → Report + **LLM Parser** + **Pre-commit Hook** + **VS Code Extension**

## Phases (Sequential Implementation)

### Phase 1: Signature Validation (Layer 3) — 6h
**Priority:** P1 (blocks other features)
**Status:** Complete
**File:** [phase-01-dynamic-hallucination-detection.md](./phase-01-dynamic-hallucination-detection.md)

Extract function calls from AST, validate against real signatures using Jedi + typeshed, report wrong parameters/types.

**Key Deliverables:**
- `src/hallucination_firewall/pipeline/signature_checker.py` (150 lines)
- Integration into `runner.py` as Layer 3
- Tests for Python stdlib + PyPI packages

### Phase 2: LLM Output Parser — 3h
**Priority:** P1 (enables workflow integration)
**Status:** Complete
**File:** [phase-02-entropy-rate-analysis.md](./phase-02-entropy-rate-analysis.md)

Parse markdown code fences from LLM responses, extract multiple blocks, route to validation pipeline.

**Key Deliverables:**
- `src/hallucination_firewall/parsers/llm_output_parser.py` (120 lines)
- CLI command: `firewall parse <llm-response-file>`
- Regex-based extraction (zero dependencies)

### Phase 3: Pre-commit Hook — 2h
**Priority:** P2 (developer UX)
**Status:** Complete
**File:** [phase-03-pattern-matching.md](./phase-03-pattern-matching.md)

Integrate with pre-commit framework, run validation on staged files, support `.firewall.toml`.

**Key Deliverables:**
- `.pre-commit-hooks.yaml` in repo root
- Update `pyproject.toml` console_scripts (already exists)
- Documentation for users

### Phase 4: VS Code Extension — 5h
**Priority:** P2 (IDE integration)
**Status:** Complete
**File:** [phase-04-real-time-alerts.md](./phase-04-real-time-alerts.md)

TypeScript extension calling `/validate` API with debounce, inline diagnostics, support Python/JS/TS.

**Key Deliverables:**
- `vscode-extension/` directory with TypeScript source
- Extension manifest (`package.json`)
- Debounced HTTP client (500ms)

## Dependencies

```
Phase 1 (Signature) → Required for complete validation
    ↓
Phase 2 (LLM Parser) → Consumes Phase 1 validation
    ↓
Phase 3 (Pre-commit) → Uses existing CLI from Phase 1
    ↓
Phase 4 (VS Code) → Calls API with Phase 1 features
```

## Success Metrics

- **Signature Validation:** 90% accuracy on stdlib + top 100 PyPI packages
- **LLM Parser:** Extract 100% of code blocks from GPT-4/Claude responses
- **Pre-commit:** <500ms validation time for typical commit (3-5 files)
- **VS Code:** <100ms debounce latency, zero false positives in diagnostics

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Jedi performance slow | High | Add LRU cache for signature lookups |
| Regex parser fails on edge cases | Medium | Test with 100 real LLM outputs |
| Pre-commit hook too slow | High | Use existing SQLite cache + parallel file processing |
| VS Code extension network errors | Medium | Graceful degradation + offline mode |

## Next Steps

1. Start with Phase 1 (signature validation) — core feature
2. Parallel research: Collect 50 real LLM outputs for Phase 2 testing
3. Document pre-commit setup in README after Phase 3
4. Publish VS Code extension to marketplace after Phase 4

## Validation Log

### Session 1 — 2026-02-18
**Trigger:** Initial plan creation validation
**Questions asked:** 6

#### Questions & Answers

1. **[Architecture]** Signature validation (Phase 1): Nên dùng Jedi library hay chỉ dùng `inspect.signature()` cho installed packages? Jedi mạnh hơn nhưng thêm dependency 50MB+.
   - Options: Jedi + inspect fallback | inspect.signature() only | typeshed-client + inspect
   - **Answer:** Jedi + inspect fallback (Recommended)
   - **Rationale:** Jedi provides 1000+ package stubs from typeshed, much better coverage than inspect-only approach

2. **[Architecture]** VS Code extension (Phase 4): Validate khi nào? Real-time (mỗi keystroke + debounce) hay chỉ khi save file?
   - Options: On change + 500ms debounce | On save only | Both (user configurable)
   - **Answer:** Both (user configurable)
   - **Rationale:** Default on-save, user can toggle to on-change in settings. Balances UX and performance

3. **[Tradeoff]** Pre-commit hook (Phase 3): Nên xử lý network timeout thế nào khi commit?
   - Options: Fail-open | Fail-closed | Configurable
   - **Answer:** Configurable
   - **Rationale:** Add `fail_on_network_error` option in .firewall.toml. Default fail-open, teams can enforce fail-closed

4. **[Scope]** LLM parser (Phase 2): Ngoài file input, có cần hỗ trợ stdin pipe để pipe trực tiếp từ LLM API không?
   - Options: File + stdin | File only | File + stdin + URL
   - **Answer:** File + stdin + URL
   - **Rationale:** Maximum flexibility for CI/CD pipelines and automation. URL fetching enables direct LLM API integration

5. **[Scope]** Thứ tự implement: Plan hiện tại là sequential (P1→P2→P3→P4).
   - Options: Sequential | P1+P2 parallel then P3+P4 | Phase 1 only first
   - **Answer:** Sequential (Recommended)
   - **Rationale:** Safe incremental delivery, each phase builds on previous

6. **[Scope]** Scope cho JavaScript/TypeScript signature validation: Phase 1 chỉ hỗ trợ Python.
   - Options: Python only for v1 | Python + basic JS
   - **Answer:** Python + basic JS
   - **Rationale:** Add basic JS signature checking using TypeScript language service. More effort but broader coverage

#### Confirmed Decisions
- Jedi + inspect fallback for signature lookup — best coverage
- VS Code: configurable trigger (default on-save, toggle to on-change) — balanced UX
- Pre-commit: configurable fail behavior via .firewall.toml — flexible for teams
- LLM parser: file + stdin + URL input — max CI/CD flexibility
- Sequential implementation order — safe delivery
- Python + basic JS signature support — broader language coverage

#### Action Items
- [ ] Phase 1: Add basic JS signature checking (TypeScript language service)
- [ ] Phase 2: Add `--stdin` and `--url` flags to `firewall parse` command
- [ ] Phase 3: Add `fail_on_network_error` config option to .firewall.toml
- [ ] Phase 4: Add configurable trigger mode (on-save default, on-change toggle)

#### Impact on Phases
- Phase 1: Add JS signature checking section — increases effort from 6h to ~8h
- Phase 2: Add stdin + URL input support — increases effort from 3h to ~4h
- Phase 3: Add configurable fail behavior config — minor change, +30min
- Phase 4: Change trigger from on-change-only to configurable (default on-save) — +30min
