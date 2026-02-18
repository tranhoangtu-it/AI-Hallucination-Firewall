"""Tests for language detection utility."""

from hallucination_firewall.models import Language
from hallucination_firewall.utils.language_detector import detect_language


def test_detect_python():
    assert detect_language("app.py") == Language.PYTHON
    assert detect_language("types.pyi") == Language.PYTHON


def test_detect_javascript():
    assert detect_language("index.js") == Language.JAVASCRIPT
    assert detect_language("component.jsx") == Language.JAVASCRIPT
    assert detect_language("lib.mjs") == Language.JAVASCRIPT


def test_detect_typescript():
    assert detect_language("app.ts") == Language.TYPESCRIPT
    assert detect_language("component.tsx") == Language.TYPESCRIPT


def test_detect_unknown():
    assert detect_language("file.rb") == Language.UNKNOWN
    assert detect_language("Makefile") == Language.UNKNOWN


def test_detect_case_insensitive():
    assert detect_language("app.PY") == Language.PYTHON
    assert detect_language("app.Js") == Language.JAVASCRIPT
