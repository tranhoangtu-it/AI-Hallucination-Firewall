"""Rich terminal reporter for validation results."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..models import Severity, ValidationResult

SEVERITY_STYLES = {
    Severity.ERROR: "bold red",
    Severity.WARNING: "bold yellow",
    Severity.INFO: "bold blue",
}

SEVERITY_ICONS = {
    Severity.ERROR: "✗",
    Severity.WARNING: "⚠",
    Severity.INFO: "ℹ",
}


def print_result(result: ValidationResult, console: Console | None = None) -> None:
    """Print validation result to terminal with Rich formatting."""
    console = console or Console()

    if result.passed and not result.issues:
        console.print(f"[bold green]✓[/] {result.file} — no issues found")
        return

    # Header
    status = "[bold green]PASSED[/]" if result.passed else "[bold red]FAILED[/]"
    console.print(
        Panel(
            f"[bold]{result.file}[/] ({result.language}) — {status}",
            subtitle=f"{result.error_count} errors, {result.warning_count} warnings",
        )
    )

    # Issues table
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("", width=3)
    table.add_column("Location", style="dim", width=12)
    table.add_column("Type", width=20)
    table.add_column("Message")

    for issue in result.issues:
        icon = SEVERITY_ICONS[issue.severity]
        style = SEVERITY_STYLES[issue.severity]
        loc = f"L{issue.location.line}:{issue.location.column}"

        message = Text(issue.message)
        if issue.suggestion:
            message.append(f"\n  → {issue.suggestion}", style="dim italic")

        table.add_row(
            Text(icon, style=style),
            loc,
            issue.issue_type.value,
            message,
        )

    console.print(table)


def print_summary(results: list[ValidationResult], console: Console | None = None) -> None:
    """Print summary of multiple validation results."""
    console = console or Console()

    total_files = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total_files - passed
    total_errors = sum(r.error_count for r in results)
    total_warnings = sum(r.warning_count for r in results)

    console.print()
    if failed == 0:
        console.print(f"[bold green]All {total_files} files passed validation[/]")
    else:
        console.print(
            f"[bold red]{failed}/{total_files} files failed[/] — "
            f"{total_errors} errors, {total_warnings} warnings"
        )
