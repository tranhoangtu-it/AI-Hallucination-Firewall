# Edge Case Scout Report
**Files Reviewed:** runner.py, ast_validator.py, import_checker.py, cli.py

---

## Edge Case Analysis

1. **Empty code string to validate_code()**
   - ✅ **Handled**. Empty string parses fine with tree-sitter, returns empty import list, passes syntax validation.

2. **Binary/non-UTF8 file input to validate_file()**
   - ❌ **Unhandled**. Line 67 opens file with `encoding="utf-8"`. Non-UTF8 files crash with UnicodeDecodeError, not caught.

3. **Massive file (>10MB) no size limit**
   - ❌ **Unhandled**. No file size check before reading. Could cause memory exhaustion or OOM crash.

4. **AST parser crash on severely malformed code**
   - ⚠️ **Partial**. tree-sitter handles most malformed code gracefully, but edge cases (null bytes, truncated UTF-8) may crash parser without try-except wrapper.

5. **Python `import x as y` alias extraction**
   - ⚠️ **Partial**. Extracts root package only (correct behavior), but doesn't distinguish aliases. Works for validation but misses import alias context.

6. **Python `from . import x` relative import handling**
   - ⚠️ **Partial**. Lines 96-103 only extract first dotted_name; relative imports (`.`) are skipped silently. Not reported as issue.

7. **Scoped npm packages `@scope/pkg` extraction**
   - ✅ **Handled**. Lines 116-119 explicitly handle scoped packages with `@` prefix and `/` split logic.

8. **Missing pipeline.close() on exception in CLI _run_check**
   - ✅ **Handled**. Lines 104-115 use try-finally block; close() runs regardless of exception.

---

## Critical Gaps
- File encoding errors need try-except with graceful fallback
- Missing file size validation before read operations
- Parser robustness not guaranteed for edge case inputs
