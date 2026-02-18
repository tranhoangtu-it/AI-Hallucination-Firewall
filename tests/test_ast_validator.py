"""Tests for AST validation and import extraction."""


from hallucination_firewall.models import IssueType, Language
from hallucination_firewall.pipeline.ast_validator import (
    extract_import_aliases,
    extract_imports,
    validate_syntax,
)


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


def test_extract_import_alias_simple():
    """Test simple import alias extraction: import X as Y."""
    code = "import pandas as pd\nimport numpy as np\n"
    aliases = extract_import_aliases(code, Language.PYTHON)
    assert aliases["pd"] == "pandas"
    assert aliases["np"] == "numpy"


def test_extract_import_alias_from_import():
    """Test alias from 'from X import Y as Z'."""
    code = "from matplotlib import pyplot as plt\n"
    aliases = extract_import_aliases(code, Language.PYTHON)
    assert aliases["plt"] == "matplotlib.pyplot"


def test_extract_import_alias_mixed():
    """Test extraction with both import styles."""
    code = """
import pandas as pd
from sklearn.model_selection import train_test_split as tts
import numpy as np
from os import path as ospath
"""
    aliases = extract_import_aliases(code, Language.PYTHON)
    assert aliases["pd"] == "pandas"
    assert aliases["np"] == "numpy"
    assert aliases["tts"] == "sklearn.model_selection.train_test_split"
    assert aliases["ospath"] == "os.path"


def test_extract_import_alias_no_aliases():
    """Test code with no import aliases."""
    code = "import os\nimport json\nfrom pathlib import Path\n"
    aliases = extract_import_aliases(code, Language.PYTHON)
    assert len(aliases) == 0


def test_extract_import_alias_non_python():
    """Test that non-Python languages return empty dict."""
    code = 'import React from "react";\n'
    aliases = extract_import_aliases(code, Language.JAVASCRIPT)
    assert len(aliases) == 0


# --- Exception path tests ---


def test_validate_syntax_exception(monkeypatch):
    """validate_syntax returns [] when tree-sitter crashes."""
    monkeypatch.setattr(
        "hallucination_firewall.pipeline.ast_validator.Parser",
        lambda *a: (_ for _ in ()).throw(RuntimeError("crash")),
    )
    result = validate_syntax("code", Language.PYTHON, "test.py")
    assert result == []


def test_extract_imports_exception(monkeypatch):
    """extract_imports returns [] when parsing fails."""
    monkeypatch.setattr(
        "hallucination_firewall.pipeline.ast_validator.Parser",
        lambda *a: (_ for _ in ()).throw(RuntimeError("crash")),
    )
    result = extract_imports("code", Language.PYTHON)
    assert result == []


def test_extract_import_aliases_exception(monkeypatch):
    """extract_import_aliases returns {} when parsing fails."""
    monkeypatch.setattr(
        "hallucination_firewall.pipeline.ast_validator.Parser",
        lambda *a: (_ for _ in ()).throw(RuntimeError("crash")),
    )
    result = extract_import_aliases("import pandas", Language.PYTHON)
    assert result == {}


def test_extract_imports_scoped_package():
    """Scoped npm packages like @babel/core are extracted."""
    code = 'import { foo } from "@babel/core";'
    result = extract_imports(code, Language.JAVASCRIPT)
    assert "@babel/core" in result


def test_extract_import_aliases_unknown_language():
    """UNKNOWN language returns empty dict."""
    result = extract_import_aliases("code", Language.UNKNOWN)
    assert result == {}
