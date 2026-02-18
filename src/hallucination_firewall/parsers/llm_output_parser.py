"""Parse markdown code fences from LLM responses and validate each block."""

from __future__ import annotations

import json
import re

from ..models import CodeBlock, LLMValidationReport, ValidationResult
from ..pipeline.runner import ValidationPipeline

# Regex for fenced code blocks: ```lang\ncode\n```
CODE_FENCE_PATTERN = re.compile(r"```([^\n]*)\n(.*?)```", re.DOTALL)

MAX_BLOCKS = 100
MAX_INPUT_SIZE = 10 * 1024 * 1024  # 10 MB


def extract_code_blocks(markdown: str) -> list[CodeBlock]:
    """Extract all fenced code blocks from markdown text."""
    blocks: list[CodeBlock] = []

    for index, match in enumerate(CODE_FENCE_PATTERN.finditer(markdown)):
        if index >= MAX_BLOCKS:
            break

        tag = match.group(1).strip().lower()
        code = match.group(2)
        # Remove trailing whitespace but keep leading (indentation matters)
        code = code.rstrip()
        line_number = markdown[: match.start()].count("\n") + 1
        language = _normalize_language(tag) if tag else detect_language_heuristic(code)

        blocks.append(
            CodeBlock(
                language=language,
                code=code,
                line_number=line_number,
                block_index=index,
                raw_tag=tag,
            )
        )

    return blocks


def _normalize_language(tag: str) -> str:
    """Normalize fence tag to canonical language name."""
    mapping = {
        "py": "python",
        "python3": "python",
        "js": "javascript",
        "jsx": "javascript",
        "ts": "typescript",
        "tsx": "typescript",
        "sh": "bash",
        "shell": "bash",
        "zsh": "bash",
    }
    return mapping.get(tag, tag)


def detect_language_heuristic(code: str) -> str:
    """Detect language from code content using heuristics."""
    # Try JSON parse
    try:
        json.loads(code)
        return "json"
    except (json.JSONDecodeError, ValueError):
        pass

    head = code[:300]

    # SQL keywords
    sql_keywords = ("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE TABLE", "ALTER TABLE")
    if any(kw in head.upper() for kw in sql_keywords):
        return "sql"

    # Shell patterns
    if code.startswith("#!") or head.lstrip().startswith("$ "):
        return "bash"

    # XML/HTML
    stripped = head.lstrip()
    if stripped.startswith("<") and ">" in stripped[:100]:
        return "xml"

    # Python imports
    if "import " in head or "from " in head or "def " in head:
        return "python"

    # JS/TS patterns
    if any(kw in head for kw in ("function ", "const ", "let ", "var ", "=>")):
        return "javascript"

    return "text"


async def validate_llm_output(
    markdown: str,
    config: object | None = None,
) -> LLMValidationReport:
    """Parse LLM markdown output and validate all code blocks."""
    if len(markdown) > MAX_INPUT_SIZE:
        return LLMValidationReport(total_blocks=0, blocks_passed=0, blocks_failed=0)

    blocks = extract_code_blocks(markdown)

    if not blocks:
        return LLMValidationReport(total_blocks=0, blocks_passed=0, blocks_failed=0)

    pipeline = ValidationPipeline(config)  # type: ignore[arg-type]
    results: list[ValidationResult] = []

    try:
        for block in blocks:
            # Only validate supported languages
            if block.language not in ("python", "javascript", "typescript"):
                results.append(
                    ValidationResult(
                        file=f"<llm-block-{block.block_index}>",
                        language=block.language,
                        passed=True,
                    )
                )
                continue

            ext = {"python": "py", "javascript": "js", "typescript": "ts"}.get(
                block.language, "txt"
            )
            file_name = f"<llm-block-{block.block_index}>.{ext}"
            result = await pipeline.validate_code(block.code, file_name)
            results.append(result)
    finally:
        await pipeline.close()

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    return LLMValidationReport(
        total_blocks=len(blocks),
        blocks_passed=passed,
        blocks_failed=failed,
        results=results,
    )
