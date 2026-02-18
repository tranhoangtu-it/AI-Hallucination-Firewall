# Phase 4: CLI Interface (Click + Rich)

## Context
- [Plan Overview](./plan.md)
- [Phase 3: Validation Pipeline](./phase-03-validation-pipeline.md)

## Overview
- **Priority:** P1
- **Status:** pending
- **Effort:** 3h
- **Depends on:** Phase 3 (pipeline must work)
- **Parallel with:** Phase 5 (API server)
- **Description:** Build Click-based CLI with Rich terminal output. Commands: `check`, `watch`, `serve`.

## Key Insights
- Click groups compose well — top-level `firewall` group, subcommands underneath
- Rich Console handles colors, tables, panels — ideal for validation reports
- `--stdin` flag enables piping from LLM output directly
- Watch mode uses filesystem polling (watchdog or simple loop)

## Requirements
- **Functional:** `firewall check <file>`, `firewall check --stdin`, `firewall watch <dir>`, `firewall serve`
- **Non-functional:** Help text for every command, <200ms CLI startup, exit code 1 on errors

## Architecture

```
cli.py
├── main()           Click group
├── check()          Validate file(s)
├── watch()          Continuous monitoring
└── serve()          Start API server (delegates to server.py)

reporters/
├── terminal_reporter.py   Rich-formatted output
└── json_reporter.py       JSON output for CI/CD
```

## Related Code Files
- **Create:** `src/hallucination_firewall/cli.py`
- **Create:** `src/hallucination_firewall/reporters/terminal_reporter.py`
- **Create:** `src/hallucination_firewall/reporters/json_reporter.py`

## Implementation Steps

### 4.1 CLI Entry Point (`cli.py`)

```python
import click
import asyncio
from pathlib import Path

@click.group()
@click.option("--config", type=click.Path(exists=True), help="Config file path")
@click.pass_context
def main(ctx, config):
    """AI Hallucination Firewall — validate AI-generated code."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(Path(config) if config else None)

@main.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--stdin", is_flag=True, help="Read code from stdin")
@click.option("--format", "output_format", type=click.Choice(["terminal", "json"]),
              default="terminal")
@click.option("--language", "-l", help="Force language (auto-detect if omitted)")
@click.pass_context
def check(ctx, files, stdin, output_format, language):
    """Validate file(s) for AI hallucinations."""
    asyncio.run(_check(ctx.obj["config"], files, stdin, output_format, language))

@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.pass_context
def watch(ctx, directory):
    """Watch directory for changes, validate on save."""
    # Poll-based watcher, re-validate changed files

@main.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8000, type=int)
@click.pass_context
def serve(ctx, host, port):
    """Start the API server."""
    import uvicorn
    uvicorn.run("hallucination_firewall.server:app", host=host, port=port)
```

### 4.2 Terminal Reporter (`reporters/terminal_reporter.py`)

Use Rich to display:
1. **Header panel:** File name, language, validation time
2. **Issues table:** Severity (colored), line:col, message, suggestion
3. **Summary:** X errors, Y warnings, Z info — with color coding
4. Exit code: 0 if no errors, 1 if errors found

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

class TerminalReporter:
    def __init__(self):
        self.console = Console()

    def report(self, result: ValidationResult) -> None:
        """Print rich-formatted validation report."""
        # Header panel
        # Issues table with severity colors
        # Summary line
```

Severity colors: ERROR=red, WARNING=yellow, INFO=blue

### 4.3 JSON Reporter (`reporters/json_reporter.py`)

```python
class JSONReporter:
    def report(self, result: ValidationResult) -> str:
        """Return JSON string of validation result."""
        return result.model_dump_json(indent=2)
```

### 4.4 Watch Mode Implementation

Simple polling loop (avoid watchdog dependency for MVP):
1. Scan directory for supported files
2. Track file modification times
3. On change, re-run pipeline on changed file
4. Display results via terminal reporter
5. Ctrl+C to stop

## Todo List
- [ ] Implement Click group with `main`, `check`, `watch`, `serve` commands
- [ ] Implement `--stdin` flag reading from sys.stdin
- [ ] Implement `--format` flag switching between terminal/json
- [ ] Implement `--language` override flag
- [ ] Implement TerminalReporter with Rich tables and panels
- [ ] Implement JSONReporter for CI/CD output
- [ ] Implement watch mode with polling
- [ ] Set correct exit codes (0=clean, 1=errors found)
- [ ] Add `--version` flag
- [ ] Write help text for all commands and options

## Success Criteria
- `firewall check sample.py` prints colored report with issues
- `firewall check --format json sample.py` outputs valid JSON
- `echo "import fakelib" | firewall check --stdin -l python` works
- `firewall serve` starts uvicorn server
- Exit code is 1 when errors found, 0 when clean
- `firewall --help` shows all commands with descriptions

## Risk Assessment
- `asyncio.run()` in Click can conflict with existing event loops → use `asyncio.run()` only at top level
- Rich output may not render in CI terminals → JSON format flag is the escape hatch
- Watch mode polling can miss rapid changes → acceptable for MVP, document limitation
