# Edge Case Review Report
**AI Hallucination Firewall Project**
Date: 2026-02-18

## Summary
Reviewed 4 critical files for 7 edge cases. Found 3 unhandled, 2 partial, 2 handled.

---

## Edge Case Analysis

### 1. HTTP Timeout/Connection Error During Registry Query
**Files:** `pypi_registry.py`, `npm_registry.py`
**Status:** ✅ **Handled**

Both registries catch `httpx.HTTPError` (line 33, 56 in PyPI; line 33, 56 in npm).
- **PyPI**: Returns `True` (fail-open) on timeout → queries always succeed during fallback
- **npm**: Returns `True` (fail-open) on timeout → consistent behavior
- **Note:** Timeout configured via `config.timeout_seconds` (default 10s)

---

### 2. SQLite Concurrent Write Race Condition
**File:** `cache.py`
**Status:** ⚠️ **Partial**

**Issue:** No concurrent write protection for simultaneous cache updates.
- `set()` uses `INSERT OR REPLACE` (line 52) but lacks transaction isolation level
- Multiple async tasks can race on `set()` + `delete()` calls (line 58-59)
- SQLite default is `DEFERRED` transactions → no write locks until execution
- `get()` followed by `delete()` (line 43) is NOT atomic

**Risk:** High under concurrent load. Data may be lost or duplicated.

---

### 3. Cache JSON Corruption (Invalid Data Stored)
**File:** `cache.py`
**Status:** ❌ **Unhandled**

**Issue:** No validation of JSON on retrieval.
- Line 46: `json.loads(value)` has no try-except
- If database is corrupted or value manually edited, `JSONDecodeError` crashes the request
- No fallback to treat corrupted cache as miss

**Risk:** Server crashes on corrupted cache entries. Silent data loss if JSON is valid but malformed dict.

---

### 4. Server Pipeline is None Assertion Before Lifespan Completes
**File:** `server.py`
**Status:** ⚠️ **Partial**

**Issue:** Race condition in startup timing.
- Line 52: `assert pipeline is not None` assumes lifespan has finished
- But FastAPI may route requests before lifespan completes
- If request arrives during `ValidationPipeline(config)` initialization (line 22), assertion fails
- No graceful 503 Service Unavailable response

**Risk:** Assertion error crashes server instead of queuing/rejecting requests.

---

### 5. Large POST Body to /validate Endpoint
**File:** `server.py`
**Status:** ✅ **Handled**

**Coverage:**
- FastAPI has built-in request size limits (default ~500MB)
- `Pydantic` validates `code: str` field (line 36)
- HTTP client handles streaming
- No custom limits needed for typical use

**Note:** No explicit max_size config but acceptable for validation API.

---

### 6. Registry HTTP Clients Not Closed on Server Shutdown Error
**File:** `server.py`, `server.py` pipeline integration
**Status:** ⚠️ **Partial**

**Issue:** If `pipeline.close()` fails, HTTP clients remain open.
- Line 24: `await pipeline.close()` in lifespan has no try-except
- If PyPI or npm client fails to close, connection leaks
- Server shutdown may hang or fail silently

**Risk:** Connection pool exhaustion on repeated restarts.

---

### 7. Empty Package Name Query to Registries
**File:** `pypi_registry.py`, `npm_registry.py`
**Status:** ❌ **Unhandled**

**Issue:** No validation of package name input.
- `package_exists("")` → Query to `https://pypi.org/pypi//json` (malformed URL)
- `package_exists(None)` → Type error or HTTP 404
- No length check or regex validation
- Both registries accept any string passed in

**Risk:** Malformed HTTP requests, unexpected HTTP responses (404 vs 500), cache pollution with empty keys.

---

## Summary Table

| # | Edge Case | Status | Severity |
|---|-----------|--------|----------|
| 1 | HTTP timeout/connection error | ✅ Handled | Low |
| 2 | SQLite concurrent write race | ⚠️ Partial | **High** |
| 3 | Cache JSON corruption | ❌ Unhandled | **High** |
| 4 | Pipeline None assertion | ⚠️ Partial | **Medium** |
| 5 | Large POST body | ✅ Handled | Low |
| 6 | HTTP client closure on error | ⚠️ Partial | **Medium** |
| 7 | Empty package name query | ❌ Unhandled | **Medium** |

---

## Recommended Fixes (Priority Order)

1. **Cache JSON corruption** → Add try-except in `cache.py` line 46
2. **SQLite race condition** → Use `IMMEDIATE` transaction isolation in `cache.py`
3. **Empty package name validation** → Add regex check in registry `package_exists()` methods
4. **Pipeline None assertion** → Replace with graceful 503 error or request queue
5. **HTTP client closure** → Wrap `pipeline.close()` in try-except in `server.py`
