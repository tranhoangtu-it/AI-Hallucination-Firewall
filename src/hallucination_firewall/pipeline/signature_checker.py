"""Signature validation — checks function calls against real signatures."""

from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass, field
import jedi
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

from ..models import (
    IssueType,
    Severity,
    SourceLocation,
    ValidationIssue,
)
from ..models import Language as LangEnum

logger = logging.getLogger(__name__)

PY_LANGUAGE = Language(tspython.language())


@dataclass
class FunctionCall:
    """A function call extracted from AST."""

    name: str
    positional_count: int
    keywords: list[str] = field(default_factory=list)
    has_star_args: bool = False
    has_star_kwargs: bool = False
    line: int = 0


@dataclass
class ParamInfo:
    """Parameter info from a function signature."""

    name: str
    required: bool = True
    kind: str = "POSITIONAL_OR_KEYWORD"


@dataclass
class SignatureInfo:
    """Resolved function signature."""

    params: list[ParamInfo] = field(default_factory=list)
    has_var_positional: bool = False
    has_var_keyword: bool = False


class FunctionCallExtractor:
    """Extract function calls from tree-sitter AST."""

    def __init__(self) -> None:
        self.parser = Parser(PY_LANGUAGE)

    def extract_calls(self, code: str) -> list[FunctionCall]:
        """Extract all function calls from Python code."""
        tree = self.parser.parse(code.encode("utf-8"))
        calls: list[FunctionCall] = []
        self._walk(tree.root_node, calls)
        return calls

    def _walk(self, node: object, calls: list[FunctionCall]) -> None:
        """Recursively walk AST to find call nodes."""
        if node.type == "call":  # type: ignore[union-attr]
            call = self._parse_call(node)
            if call:
                calls.append(call)
        for child in node.children:  # type: ignore[union-attr]
            self._walk(child, calls)

    def _parse_call(self, node: object) -> FunctionCall | None:
        """Parse a call node into FunctionCall."""
        func_node = node.child_by_field_name("function")  # type: ignore[union-attr]
        args_node = node.child_by_field_name("arguments")  # type: ignore[union-attr]
        if not func_node:
            return None

        name = self._get_name(func_node)
        if not name or not self._is_checkable(name):
            return None

        positional = 0
        keywords: list[str] = []
        has_star_args = False
        has_star_kwargs = False

        if args_node:
            for child in args_node.children:  # type: ignore[union-attr]
                if child.type == "keyword_argument":
                    key_node = child.child_by_field_name("name")
                    if key_node:
                        keywords.append(key_node.text.decode("utf-8"))
                elif child.type == "list_splat":
                    has_star_args = True
                elif child.type == "dictionary_splat":
                    has_star_kwargs = True
                elif child.type not in ("(", ")", ","):
                    positional += 1

        return FunctionCall(
            name=name,
            positional_count=positional,
            keywords=keywords,
            has_star_args=has_star_args,
            has_star_kwargs=has_star_kwargs,
            line=func_node.start_point[0],  # type: ignore[union-attr]
        )

    def _get_name(self, node: object) -> str:
        """Get dotted function name from AST node."""
        if node.type == "identifier":  # type: ignore[union-attr]
            return node.text.decode("utf-8")  # type: ignore[union-attr]
        if node.type == "attribute":  # type: ignore[union-attr]
            obj = node.child_by_field_name("object")  # type: ignore[union-attr]
            attr = node.child_by_field_name("attribute")  # type: ignore[union-attr]
            if obj and attr:
                obj_name = self._get_name(obj)
                attr_name = attr.text.decode("utf-8")  # type: ignore[union-attr]
                return f"{obj_name}.{attr_name}" if obj_name else attr_name
        return ""

    def _is_checkable(self, name: str) -> bool:
        """Filter out names unlikely to have resolvable signatures."""
        # Skip single-name calls like local functions, builtins print/len
        # Focus on dotted names (module.func) which are more checkable
        return "." in name


class SignatureLookup:
    """Look up function signatures using Jedi + inspect fallback."""

    def get_signature(self, func_name: str, code: str, line: int) -> SignatureInfo | None:
        """Get signature for function at given location in code."""
        # Try Jedi first
        sig = self._jedi_lookup(func_name, code, line)
        if sig:
            return sig
        # Fallback: inspect installed module
        return self._inspect_lookup(func_name)

    def _jedi_lookup(self, func_name: str, code: str, line: int) -> SignatureInfo | None:
        """Use Jedi to resolve signature."""
        try:
            script = jedi.Script(code)
            # Find the call at line+1 (Jedi uses 1-indexed lines)
            sigs = script.get_signatures(line + 1, 0)
            if not sigs:
                # Try goto to find the function definition
                names = script.goto(line + 1, 0, follow_imports=True)
                if names:
                    for name in names:
                        try:
                            name_sigs = name.get_signatures()
                            if name_sigs:
                                return self._jedi_sig_to_info(name_sigs[0])
                        except Exception:
                            continue
                return None
            return self._jedi_sig_to_info(sigs[0])
        except Exception:
            logger.debug("Jedi lookup failed for %s", func_name)
            return None

    def _jedi_sig_to_info(self, sig: object) -> SignatureInfo:
        """Convert Jedi signature to SignatureInfo."""
        params: list[ParamInfo] = []
        has_var_pos = False
        has_var_kw = False

        for p in sig.params:  # type: ignore[union-attr]
            kind = str(getattr(p, "kind", "POSITIONAL_OR_KEYWORD"))
            if "VAR_POSITIONAL" in kind:
                has_var_pos = True
                continue
            if "VAR_KEYWORD" in kind:
                has_var_kw = True
                continue
            required = not hasattr(p, "default") or p.description.find("=") == -1  # type: ignore[union-attr]
            params.append(ParamInfo(
                name=p.name,  # type: ignore[union-attr]
                required=required,
                kind=kind,
            ))

        return SignatureInfo(
            params=params, has_var_positional=has_var_pos, has_var_keyword=has_var_kw,
        )

    # Only allow importing stdlib modules for inspect fallback (security)
    _SAFE_MODULES = frozenset({
        "os", "os.path", "sys", "json", "re", "math", "datetime",
        "pathlib", "collections", "itertools", "functools", "typing",
        "io", "csv", "hashlib", "base64", "urllib", "urllib.parse",
        "shutil", "tempfile", "logging", "string", "textwrap",
    })

    def _inspect_lookup(self, func_name: str) -> SignatureInfo | None:
        """Fallback: use inspect.signature() for safe stdlib modules only."""
        if "." not in func_name:
            return None
        try:
            parts = func_name.rsplit(".", 1)
            module_name = parts[0]
            # Only import from allowlisted stdlib modules
            if module_name not in self._SAFE_MODULES:
                return None
            mod = __import__(module_name, fromlist=[parts[1]])
            obj = getattr(mod, parts[1])
            sig = inspect.signature(obj)
            return self._inspect_sig_to_info(sig)
        except Exception:
            return None

    def _inspect_sig_to_info(self, sig: inspect.Signature) -> SignatureInfo:
        """Convert inspect.Signature to SignatureInfo."""
        params: list[ParamInfo] = []
        has_var_pos = False
        has_var_kw = False

        for name, p in sig.parameters.items():
            if name == "self":
                continue
            if p.kind == inspect.Parameter.VAR_POSITIONAL:
                has_var_pos = True
                continue
            if p.kind == inspect.Parameter.VAR_KEYWORD:
                has_var_kw = True
                continue
            required = p.default is inspect.Parameter.empty
            params.append(ParamInfo(name=name, required=required))

        return SignatureInfo(
            params=params, has_var_positional=has_var_pos, has_var_keyword=has_var_kw,
        )


class SignatureValidator:
    """Compare function call arguments against signature parameters."""

    def validate(self, call: FunctionCall, sig: SignatureInfo) -> list[tuple[IssueType, str]]:
        """Return list of (issue_type, message) tuples."""
        # Skip validation if call uses *args/**kwargs unpacking
        if call.has_star_args or call.has_star_kwargs:
            return []
        # Skip validation if sig accepts *args/**kwargs
        if sig.has_var_positional and sig.has_var_keyword:
            return []

        errors: list[tuple[IssueType, str]] = []

        # Count required positional params
        required_params = [p for p in sig.params if p.required]
        total_params = len(sig.params)

        # Check too many positional args (only if no *args)
        if not sig.has_var_positional and call.positional_count > total_params:
            errors.append((
                IssueType.WRONG_SIGNATURE,
                f"Too many arguments: got {call.positional_count}, expected at most {total_params}",
            ))

        # Check missing required args
        provided = call.positional_count + len(call.keywords)
        min_required = len(required_params)
        if provided < min_required:
            missing = [p.name for p in required_params[provided:]]
            errors.append((
                IssueType.MISSING_REQUIRED_ARG,
                f"Missing required argument(s): {', '.join(missing)}",
            ))

        # Check unknown keyword args (only if no **kwargs)
        if not sig.has_var_keyword:
            known = {p.name for p in sig.params}
            for kw in call.keywords:
                if kw not in known:
                    errors.append((
                        IssueType.UNKNOWN_PARAMETER,
                        f"Unknown keyword argument: '{kw}'",
                    ))

        return errors


async def check_signatures(
    code: str,
    language: LangEnum,
    file_path: str,
) -> list[ValidationIssue]:
    """Check function signatures in code. Entry point for pipeline."""
    if language != LangEnum.PYTHON:
        return []

    extractor = FunctionCallExtractor()
    lookup = SignatureLookup()
    validator = SignatureValidator()

    calls = extractor.extract_calls(code)
    issues: list[ValidationIssue] = []

    for call in calls:
        sig = lookup.get_signature(call.name, code, call.line)
        if not sig:
            continue  # Fail-open: skip unknown functions

        errors = validator.validate(call, sig)
        for issue_type, message in errors:
            issues.append(ValidationIssue(
                severity=Severity.WARNING,
                issue_type=issue_type,
                location=SourceLocation(file=file_path, line=call.line + 1, column=0),
                message=f"{call.name}(): {message}",
                confidence=0.8,
                source="signature_checker",
            ))

    return issues
