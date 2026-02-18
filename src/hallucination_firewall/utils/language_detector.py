"""Detect programming language from file extension or content."""

from __future__ import annotations

from pathlib import Path

from ..models import Language

EXTENSION_MAP: dict[str, Language] = {
    ".py": Language.PYTHON,
    ".pyi": Language.PYTHON,
    ".js": Language.JAVASCRIPT,
    ".jsx": Language.JAVASCRIPT,
    ".mjs": Language.JAVASCRIPT,
    ".ts": Language.TYPESCRIPT,
    ".tsx": Language.TYPESCRIPT,
}


def detect_language(file_path: str) -> Language:
    """Detect language from file extension."""
    suffix = Path(file_path).suffix.lower()
    return EXTENSION_MAP.get(suffix, Language.UNKNOWN)
