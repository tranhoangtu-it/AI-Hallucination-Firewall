# Pre-commit Hook Setup

## Installation

1. Install pre-commit framework:
   ```bash
   pip install pre-commit
   ```

2. Add to your `.pre-commit-config.yaml`:
   ```yaml
   repos:
     - repo: https://github.com/tranhoangtu-it/AI-Hallucination-Firewall
       rev: v0.1.0
       hooks:
         - id: firewall-check
   ```

3. Install git hooks:
   ```bash
   pre-commit install
   ```

## Configuration

Create `.firewall.toml` in your project root:

```toml
[firewall]
languages = ["python", "javascript"]
severity_threshold = "warning"
cache_ttl_seconds = 3600
fail_on_network_error = false  # true = block commit on network error

[firewall.registries]
pypi_enabled = true
npm_enabled = true
timeout_seconds = 10
```

### Fail Behavior

- `fail_on_network_error = false` (default): Warn and allow commit on network error
- `fail_on_network_error = true`: Block commit if registry checks fail

## Usage

Hooks run automatically on `git commit`. Manual run:

```bash
# Run on all files
pre-commit run firewall-check --all-files

# Run on staged files only
pre-commit run firewall-check
```

## Performance

- First run: ~2-3s (cache warm-up)
- Subsequent runs: <500ms (SQLite cache hits)
- Only validates staged files

## JavaScript/TypeScript

Add the JS hook for JavaScript/TypeScript validation:

```yaml
repos:
  - repo: https://github.com/tranhoangtu-it/AI-Hallucination-Firewall
    rev: v0.1.0
    hooks:
      - id: firewall-check
      - id: firewall-check-js
```

Both hooks support the same configuration in `.firewall.toml`.

## LLM Output Validation

While pre-commit is designed for file validation, you can separately validate LLM-generated markdown responses:

```bash
# Validate a markdown file containing code blocks
firewall parse response.md

# Validate from stdin (e.g., from a curl response)
curl https://api.openai.com/... | firewall parse --stdin

# Validate from URL
firewall parse --url https://gist.github.com/your-response.md
```

The `parse` command extracts code blocks from markdown and validates each block using the standard pipeline.

## Troubleshooting

### Hook too slow
Increase cache TTL in `.firewall.toml`:
```toml
cache_ttl_seconds = 7200
```

### Skip hook for one commit
```bash
git commit --no-verify
```

### Clear cache
```bash
rm -rf ~/.cache/hallucination-firewall/
```
