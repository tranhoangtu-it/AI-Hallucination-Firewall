# Project Roadmap — AI Hallucination Firewall

## Version History & Status

### v0.2 — Security & Deprecation Hardening (RELEASED)
**Status:** Complete | **Release Date:** 2026-02-18

#### Features
- [x] **Layer 4: Deprecation Detection** — 13 Python stdlib deprecation rules (os.popen, typing.Dict, imp module, etc.)
- [x] **SSRF Prevention** — URL validation in CLI blocks private IPs (localhost, 10.x, 192.168.x) and file:// scheme
- [x] **API Rate Limiting** — RateLimitMiddleware (60 req/60s per IP, sliding window)
- [x] **Code Cleanup** — Removed dead `_cached_lookup` code, improved error messages, removed unused config fields
- [x] **Test Coverage** — 140 new tests, coverage increased to 99% (from 60% in v0.1)

#### Metrics
- Total Tests: 210 (140 new)
- Coverage: 99%
- Test Files: 16
- Bug Fixes: 3 (dead code, error messages, config cleanup)
- Security Features: 2 (SSRF, rate limiting)

#### Breaking Changes
- None

---

### v0.1.0 — Multi-Layer Foundation (RELEASED)
**Status:** Complete | **Release Date:** ~2025-11-01

#### Features
- [x] **Layer 1: Syntax Validation** — tree-sitter AST parsing (Python, JavaScript, TypeScript)
- [x] **Layer 2: Import Checking** — PyPI and npm registry verification with SQLite cache
- [x] **Layer 3: Signature Validation** — Function call validation via Jedi + inspect
- [x] **LLM Output Parser** — Extract and validate code blocks from markdown
- [x] **CLI Interface** — `firewall check` and `firewall parse` commands
- [x] **Pre-commit Integration** — Git hook definitions for Python and JavaScript
- [x] **API Server** — FastAPI with JSON output for CI/CD
- [x] **VS Code Extension** — Real-time diagnostics with configurable trigger modes
- [x] **Configuration** — .firewall.toml with language, severity, cache, and registry settings

#### Metrics
- Initial Coverage: 60%
- Tests: 68
- Supported Languages: 3 (Python, JavaScript, TypeScript)

---

## Planned Roadmap

### v0.3 — Custom Rules & Performance (PLANNED)
**Estimated Timeline:** Q2 2026

#### Proposed Features
- [ ] **Custom Deprecation Rules** — User-defined YAML rule files for org-specific patterns
- [ ] **SARIF Report Format** — GitHub/GitLab integration for native issue tracking
- [ ] **Multi-threaded Validation** — Batch file processing for large codebases
- [ ] **Performance Profiling** — Benchmarks and optimization for large files (>1MB)
- [ ] **Caching Improvements** — Pre-compiled cache for offline validation

#### Success Criteria
- Support for custom rule YAML files
- 100% SARIF spec compliance
- >2x faster batch processing (50+ files)
- Sub-100ms per-file validation for cached runs

---

### v0.4 — IDE & Workflow Integration (PLANNED)
**Estimated Timeline:** Q3 2026

#### Proposed Features
- [ ] **JetBrains Plugin** — IntelliJ, PyCharm, WebStorm integration
- [ ] **GitHub Actions** — Dedicated action for CI/CD workflows
- [ ] **GitLab Integration** — Pipeline integration and security reporting
- [ ] **Interactive Mode** — CLI prompting for ambiguous signature issues
- [ ] **Telemetry (opt-in)** — Anonymous usage tracking for feature prioritization

#### Success Criteria
- 1000+ GitHub marketplace installs
- <5% CPU overhead in IDE validation

---

### v0.5 — Advanced Detection (FUTURE)
**Estimated Timeline:** Q4 2026 or later

#### Proposed Features
- [ ] **Type Stub Analysis** — .pyi file introspection for better type info
- [ ] **Security Audit Layer** — Detect hardcoded secrets, unsafe patterns
- [ ] **ML-Based Hallucination Detection** — Anomaly detection for common LLM mistakes
- [ ] **Dependency Vulnerability Check** — Integration with CVE databases
- [ ] **Multi-language AST Rewrite** — Go, Rust, C++ support

#### Success Criteria
- >95% detection rate on curated test set
- Support for 6+ programming languages

---

## Priority Matrix

| Feature | Impact | Effort | Priority | Status |
|---------|--------|--------|----------|--------|
| Deprecation Detection (v0.2) | High | Low | P0 | ✅ Complete |
| SSRF Prevention (v0.2) | High | Low | P0 | ✅ Complete |
| Rate Limiting (v0.2) | Medium | Low | P0 | ✅ Complete |
| Custom Rules (v0.3) | High | Medium | P1 | Planned |
| SARIF Format (v0.3) | Medium | Medium | P1 | Planned |
| JetBrains Plugin (v0.4) | High | High | P2 | Planned |
| Type Stub Analysis (v0.5) | Medium | High | P2 | Future |
| Security Audit Layer (v0.5) | High | High | P3 | Future |

---

## Known Limitations

### Current (v0.2)
1. **No cross-file analysis** — Each file validated independently; no dependency graph
2. **Python-only deprecations** — JS/TS deprecation detection not yet implemented
3. **Limited type inference** — Jedi fallback for complex generic types
4. **No interactive mode** — CLI prompting for ambiguous calls TBD
5. **Single-threaded** — Large batch jobs (100+ files) process sequentially

### Design Constraints
1. **Fail-open philosophy** — Unknown patterns warn only, never hard fail
2. **No external LLMs** — Self-contained detection, no cloud dependency
3. **Registry-dependent** — PyPI/npm unavailability degrades gracefully (cached results)

---

## Success Metrics (Overall Project)

### v0.2 Validation
- [x] Test coverage ≥80% (achieved: 99%)
- [x] SSRF vulnerability detection
- [x] Rate limiting for API protection
- [x] Zero critical bugs (v0.1 issues resolved)

### v0.3+ Goals
- Reach 10k+ npm/PyPI downloads/month
- <50ms avg validation latency (cached)
- <2s first-run validation per file
- <5% false positive rate on industry test set

---

## Feedback & Issue Tracking
- **GitHub Issues:** Feature requests and bug reports
- **Discussions:** Community feedback on direction
- **Telemetry (v0.4):** Anonymous usage patterns for prioritization

---

## Release Cadence
- **Hotfixes:** As needed (v0.2.1, v0.2.2, etc.)
- **Minor Versions:** Q2, Q3, Q4 annually (feature additions)
- **Major Versions:** Annual or when architectural shift required

Last Updated: 2026-02-18 | Maintained by: Docs Team
