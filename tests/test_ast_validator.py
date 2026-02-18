"""Tests for AST validation and import extraction."""

from hallucination_firewall.models import Language, IssueType
from hallucination_firewall.pipeline.ast_validator import validate_syntax, extract_imports


def test_valid_python_syntax():
    code = "import os\nprint('hello')\n"
    issues = validate_syntax(code, Language.PYTHON, "test.py")
    assert len(issues) == 0


def test_invalid_python_syntax():
    code = "def foo(\n  # missing closing paren and body\n"
    issues = validate_syntax(code, Language.PYTHON, "test.py")
    assert len(issues) > 0
    assert issues[0].issue_type == IssueType.SYNTAX_ERROR


def test_valid_js_syntax():
    code = "const x = 1;\nconsole.log(x);\n"
    issues = validate_syntax(code, Language.JAVASCRIPT, "test.js")
    assert len(issues) == 0


def test_extract_python_imports():
    code = "import os\nimport json\nfrom pathlib import Path\nfrom collections.abc import Mapping\n"
    imports = extract_imports(code, Language.PYTHON)
    assert "os" in imports
    assert "json" in imports
    assert "pathlib" in imports
    assert "collections" in imports


def test_extract_python_no_imports():
    code = "x = 1\nprint(x)\n"
    imports = extract_imports(code, Language.PYTHON)
    assert len(imports) == 0


def test_extract_js_imports():
    code = 'import React from "react";\nimport { useState } from "react";\n'
    imports = extract_imports(code, Language.JAVASCRIPT)
    assert "react" in imports


def test_unsupported_language():
    code = "fn main() {}"
    issues = validate_syntax(code, Language.UNKNOWN, "test.rs")
    assert len(issues) == 0  # should skip gracefully


def test_extract_js_relative_imports_skipped():
    code = 'import { foo } from "./utils";\nimport bar from "../lib";\n'
    imports = extract_imports(code, Language.JAVASCRIPT)
    # Relative imports should not be in the list
    assert all(not i.startswith(".") for i in imports)
