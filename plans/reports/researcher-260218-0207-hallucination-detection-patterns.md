# LLM Hallucination Detection Patterns Research Report

**Date:** 2026-02-18 | **Status:** Complete

## 1. Common Hallucination Patterns in Code

### Fake/Nonexistent APIs
```python
# Hallucinated: pandas.DataFrame.to_graphql() doesn't exist
df.to_graphql("endpoint")
# Hallucinated: requests.get() with nonexistent parameter
requests.get(url, auto_retry=True)
```

### Wrong Method Signatures
```python
# Real: json.dumps(obj, indent=None, sort_keys=False)
# Hallucinated: json.dumps(obj, pretty=True, ordered=True)
```

### Nonexistent Packages
```python
import fastjson  # doesn't exist on PyPI
from torch.quantum import QuantumLayer  # nonexistent submodule
```

### Deprecated/Removed APIs
```python
# Removed in Python 3.12
import imp  # should use importlib
asyncio.get_event_loop()  # deprecated pattern
```

### Version Mismatches
```python
# React 18 pattern applied to React 16 project
import { useId } from 'react'  # only available React 18+
```

### Invented Parameters/Options
```javascript
// fetch() doesn't have 'timeout' option natively
fetch(url, { timeout: 5000 })
```

## 2. Detection Heuristics

### Pattern-Based Detection
- **Import scanning:** Check every import against known package registries
- **Method call validation:** Verify method exists on object type via AST
- **Parameter checking:** Compare call args against real function signatures
- **Version constraint analysis:** Cross-ref API usage with declared dependency versions

### Confidence Scoring
- **High confidence (90%+):** Package doesn't exist on registry
- **Medium (70-90%):** Method not found in type stubs/docs
- **Low (50-70%):** Unusual parameter combinations
- **Flag only:** Deprecated but still functional APIs

### Heuristic Red Flags
1. Too-convenient API names (e.g., `auto_fix=True`, `smart_mode=True`)
2. Camel/snake case mixing within same library
3. Methods that combine multiple operations suspiciously
4. Parameter names that are English words but not standard in the library

## 3. Proxy/Middleware Architecture

### Design Pattern: Intercepting Proxy
```
Developer → LLM API → [Firewall Proxy] → Validated Output
                            ↓
                    [Validation Pipeline]
                    ├── AST Parser
                    ├── Import Checker
                    ├── Signature Validator
                    └── Registry Lookup
```

### Implementation Options
| Approach | Latency | Complexity | Integration |
|---|---|---|---|
| CLI pipe (`llm | firewall`) | Low | Low | Universal |
| HTTP proxy (mitm) | Medium | Medium | API-based |
| Language server (LSP) | Low | High | IDE |
| Git pre-commit hook | Zero runtime | Low | Git workflow |

### Recommended: Multi-mode Architecture
- **CLI mode:** `firewall check <file>` for batch validation
- **Watch mode:** `firewall watch ./src` for continuous monitoring
- **API mode:** REST server for CI/CD integration
- **LSP mode:** (future) Real-time IDE diagnostics

## 4. Correction & Suggestion Strategy

### Mapping Wrong → Right
1. **Fuzzy matching:** Levenshtein distance to find closest real API
2. **Semantic search:** Embed method names, find nearest neighbor in real API index
3. **Version-aware:** Suggest correct API for project's dependency version
4. **Migration paths:** Link deprecated APIs to their replacements

### Output Format
```json
{
  "severity": "error",
  "type": "nonexistent_method",
  "location": {"file": "app.py", "line": 42, "col": 5},
  "message": "pandas.DataFrame.to_graphql() does not exist",
  "suggestion": "Did you mean: .to_json(), .to_sql(), .to_parquet()?",
  "confidence": 0.95,
  "source": "PyPI registry + type stubs"
}
```

## 5. Python Ecosystem for Building

| Library | Purpose | Why |
|---|---|---|
| **tree-sitter** | Multi-language AST parsing | Fast, supports 40+ languages |
| **Click** | CLI framework | Clean, composable commands |
| **Rich** | Terminal output | Beautiful error reports |
| **FastAPI** | API server mode | Async, auto-docs, fast |
| **httpx** | Registry API calls | Async HTTP client |
| **pydantic** | Data validation | Config/report models |
| **pytest** | Testing | Standard Python testing |
| **importlib** | Python introspection | Validate installed packages |

### Recommended Stack
- **Python 3.11+** (tomllib built-in, performance improvements)
- **tree-sitter + language grammars** for AST parsing
- **Click + Rich** for CLI
- **FastAPI + uvicorn** for API mode
- **httpx** for async registry queries
- **pydantic v2** for config/models
- **SQLite** for local cache (package metadata)

## 6. Key Implementation Insights

1. **Start with Python validation** — inspect module gives free introspection
2. **Cache aggressively** — registry responses rarely change hourly
3. **Fail open, not closed** — unknown patterns → warning, not error
4. **Incremental validation** — only check changed lines for speed
5. **Pluggable architecture** — easy to add new language validators

## Unresolved Questions

1. How to handle private/internal packages not on public registries?
2. Should we support custom rule definitions (like Semgrep)?
3. How to distinguish intentional monkey-patching from hallucinations?
