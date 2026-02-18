"""Pipeline orchestrator — runs validation stages in sequence."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..config import load_config
from ..models import (
    FirewallConfig,
    IssueType,
    Language,
    Severity,
    SourceLocation,
    ValidationIssue,
    ValidationResult,
)
from ..registries.cache import RegistryCache
from ..registries.npm_registry import NpmRegistry
from ..registries.pypi_registry import PyPIRegistry
from ..utils.language_detector import detect_language
from .ast_validator import extract_imports, validate_syntax
from .deprecation_checker import check_deprecations
from .import_checker import check_js_imports, check_python_imports
from .signature_checker import check_signatures

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class ValidationPipeline:
    """Orchestrates the multi-layer validation pipeline."""

    def __init__(self, config: FirewallConfig | None = None) -> None:
        self.config = config or load_config()
        self.cache = RegistryCache(
            self.config.cache_dir,
            self.config.cache_ttl_seconds,
        )
        self.pypi = PyPIRegistry(self.config.registries, self.cache)
        self.npm = NpmRegistry(self.config.registries, self.cache)

    async def validate_code(self, code: str, file_path: str = "<stdin>") -> ValidationResult:
        """Run full validation pipeline on code string."""
        language = detect_language(file_path)

        result = ValidationResult(
            file=file_path,
            language=language.value,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )

        # Layer 1: AST syntax validation
        syntax_issues = validate_syntax(code, language, file_path)
        result.issues.extend(syntax_issues)

        # If syntax errors, skip deeper checks (AST is unreliable)
        if syntax_issues:
            result.passed = False
            return result

        # Layer 2: Import/package existence check
        imports = extract_imports(code, language)
        if language == Language.PYTHON:
            import_issues = await check_python_imports(imports, file_path, self.pypi)
        elif language in (Language.JAVASCRIPT, Language.TYPESCRIPT):
            import_issues = await check_js_imports(imports, file_path, self.npm)
        else:
            import_issues = []

        result.issues.extend(import_issues)

        # Layer 3: Signature validation
        if language == Language.PYTHON:
            signature_issues = await check_signatures(code, language, file_path)
            result.issues.extend(signature_issues)

        # Layer 4: Deprecation detection
        if language == Language.PYTHON:
            deprecation_issues = await check_deprecations(code, language, file_path)
            result.issues.extend(deprecation_issues)

        result.passed = result.error_count == 0
        return result

    async def validate_file(self, file_path: str) -> ValidationResult:
        """Read and validate a file."""
        path = Path(file_path)
        if path.stat().st_size > MAX_FILE_SIZE:
            return ValidationResult(
                file=file_path,
                language="unknown",
                checked_at=datetime.now(timezone.utc).isoformat(),
                passed=False,
                issues=[
                    ValidationIssue(
                        severity=Severity.ERROR,
                        issue_type=IssueType.SYNTAX_ERROR,
                        location=SourceLocation(file=file_path, line=0),
                        message=f"File exceeds maximum size ({MAX_FILE_SIZE // (1024*1024)} MB)",
                        source="runner",
                    ),
                ],
            )

        try:
            with open(file_path, encoding="utf-8") as f:
                code = f.read()
        except (UnicodeDecodeError, ValueError) as exc:
            return ValidationResult(
                file=file_path,
                language="unknown",
                checked_at=datetime.now(timezone.utc).isoformat(),
                passed=False,
                issues=[
                    ValidationIssue(
                        severity=Severity.ERROR,
                        issue_type=IssueType.SYNTAX_ERROR,
                        location=SourceLocation(file=file_path, line=0),
                        message=f"Cannot decode file: {exc}",
                        source="runner",
                    ),
                ],
            )
        return await self.validate_code(code, file_path)

    async def close(self) -> None:
        """Clean up HTTP clients."""
        await self.pypi.close()
        await self.npm.close()
