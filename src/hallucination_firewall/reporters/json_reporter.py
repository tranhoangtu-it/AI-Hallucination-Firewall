"""JSON reporter for CI/CD integration."""

from __future__ import annotations

import json
import sys
from typing import TextIO

from ..models import ValidationResult


def print_json(
    results: list[ValidationResult],
    output: TextIO = sys.stdout,
    pretty: bool = False,
) -> None:
    """Output validation results as JSON."""
    data = {
        "results": [r.model_dump() for r in results],
        "summary": {
            "total_files": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "total_errors": sum(r.error_count for r in results),
            "total_warnings": sum(r.warning_count for r in results),
        },
    }
    indent = 2 if pretty else None
    output.write(json.dumps(data, indent=indent, default=str))
    output.write("\n")
