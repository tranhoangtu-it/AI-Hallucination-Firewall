"""AST-based syntax validation using tree-sitter."""

from __future__ import annotations

import logging

import tree_sitter_javascript as tsjavascript
import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser

from ..models import (
    IssueType,
    Severity,
    SourceLocation,
    ValidationIssue,
)
from ..models import (
    Language as LangEnum,
)

logger = logging.getLogger(__name__)

# Initialize languages
PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())

LANGUAGE_MAP = {
    LangEnum.PYTHON: PY_LANGUAGE,
    LangEnum.JAVASCRIPT: JS_LANGUAGE,
    LangEnum.TYPESCRIPT: JS_LANGUAGE,  # basic JS parsing for TS
}


def validate_syntax(code: str, language: LangEnum, file_path: str) -> list[ValidationIssue]:
    """Parse code with tree-sitter and report syntax errors."""
    ts_lang = LANGUAGE_MAP.get(language)
    if ts_lang is None:
        return []

    try:
        parser = Parser(ts_lang)
        tree = parser.parse(code.encode("utf-8"))

        issues: list[ValidationIssue] = []
        _collect_errors(tree.root_node, file_path, issues)
        return issues
    except Exception:
        logger.exception("tree-sitter parsing failed for %s", file_path)
        return []


def _collect_errors(node: Node, file_path: str, issues: list[ValidationIssue]) -> None:
    """Recursively collect ERROR and MISSING nodes from tree-sitter AST."""
    if node.type == "ERROR" or node.is_missing:
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                issue_type=IssueType.SYNTAX_ERROR,
                location=SourceLocation(
                    file=file_path,
                    line=node.start_point[0] + 1,
                    column=node.start_point[1],
                    end_line=node.end_point[0] + 1,
                    end_column=node.end_point[1],
                ),
                message=f"Syntax error: unexpected {node.type} node",
                confidence=1.0,
                source="tree-sitter",
            )
        )

    for child in node.children:
        _collect_errors(child, file_path, issues)


def extract_imports(code: str, language: LangEnum) -> list[str]:
    """Extract import names from code using tree-sitter AST."""
    ts_lang = LANGUAGE_MAP.get(language)
    if ts_lang is None:
        return []

    try:
        parser = Parser(ts_lang)
        tree = parser.parse(code.encode("utf-8"))

        imports: list[str] = []
        if language == LangEnum.PYTHON:
            _extract_python_imports(tree.root_node, imports)
        elif language in (LangEnum.JAVASCRIPT, LangEnum.TYPESCRIPT):
            _extract_js_imports(tree.root_node, imports)

        return imports
    except Exception:
        logger.exception("Import extraction failed for language %s", language)
        return []


def _extract_python_imports(node: Node, imports: list[str]) -> None:
    """Extract Python import statements from AST."""
    if node.type == "import_statement":
        for child in node.children:
            if child.type == "dotted_name":
                # Get root package name (first identifier)
                parts = child.text.decode("utf-8").split(".")
                if parts:
                    imports.append(parts[0])

    elif node.type == "import_from_statement":
        # from X import Y → extract X
        for child in node.children:
            if child.type == "dotted_name":
                parts = child.text.decode("utf-8").split(".")
                if parts:
                    imports.append(parts[0])
                break  # only first dotted_name is the module

    for child in node.children:
        _extract_python_imports(child, imports)


def _extract_js_imports(node: Node, imports: list[str]) -> None:
    """Extract JavaScript/TypeScript import statements from AST."""
    if node.type == "import_statement":
        for child in node.children:
            if child.type == "string":
                raw = child.text.decode("utf-8").strip("'\"")
                # Get package name (handle scoped packages)
                if raw.startswith("@"):
                    parts = raw.split("/")
                    if len(parts) >= 2:
                        imports.append(f"{parts[0]}/{parts[1]}")
                elif not raw.startswith("."):
                    imports.append(raw.split("/")[0])

    for child in node.children:
        _extract_js_imports(child, imports)


def extract_import_aliases(code: str, language: LangEnum) -> dict[str, str]:
    """Extract import alias mappings from code (e.g. 'pd' -> 'pandas').

    Args:
        code: Source code to analyze
        language: Programming language

    Returns:
        Dict mapping alias names to full module paths.
        Examples: {"pd": "pandas", "np": "numpy", "plt": "matplotlib.pyplot"}
    """
    if language != LangEnum.PYTHON:
        return {}

    ts_lang = LANGUAGE_MAP.get(language)
    if ts_lang is None:
        return {}

    try:
        parser = Parser(ts_lang)
        tree = parser.parse(code.encode("utf-8"))

        aliases: dict[str, str] = {}
        _extract_python_aliases(tree.root_node, aliases)
        return aliases
    except Exception:
        logger.exception("Alias extraction failed")
        return {}


def _extract_python_aliases(node: Node, aliases: dict[str, str]) -> None:
    """Extract Python import aliases from AST.

    Handles:
    - import pandas as pd -> {"pd": "pandas"}
    - from matplotlib import pyplot as plt -> {"plt": "matplotlib.pyplot"}
    """
    if node.type == "import_statement":
        # import X as Y
        for child in node.children:
            if child.type == "aliased_import":
                # aliased_import has: dotted_name "as" identifier
                module_node = child.child_by_field_name("name")
                alias_node = child.child_by_field_name("alias")
                if module_node and alias_node:
                    module_name = module_node.text.decode("utf-8")
                    alias_name = alias_node.text.decode("utf-8")
                    aliases[alias_name] = module_name

    elif node.type == "import_from_statement":
        # from X import Y as Z
        # Get the module name (X)
        module_name = None
        for child in node.children:
            if child.type == "dotted_name":
                module_name = child.text.decode("utf-8")
                break

        if module_name:
            # Look for aliased imports in the import list
            for child in node.children:
                if child.type == "aliased_import":
                    # aliased_import has: dotted_name "as" identifier
                    name_node = child.child_by_field_name("name")
                    alias_node = child.child_by_field_name("alias")
                    if name_node and alias_node:
                        imported_name = name_node.text.decode("utf-8")
                        alias_name = alias_node.text.decode("utf-8")
                        full_name = f"{module_name}.{imported_name}"
                        aliases[alias_name] = full_name

    # Recurse into children
    for child in node.children:
        _extract_python_aliases(child, aliases)
