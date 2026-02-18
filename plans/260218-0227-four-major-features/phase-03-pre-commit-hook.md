# Phase 3: Pre-commit Hook Integration

## Context Links

- Research: [researcher-01-signature-precommit.md](./research/researcher-01-signature-precommit.md)
- CLI: `src/hallucination_firewall/cli.py`
- Config: `src/hallucination_firewall/config.py`
- pyproject.toml: `pyproject.toml`

## Overview

**Priority:** P2
**Status:** Complete
**Effort:** 2h
**Goal:** Integrate with pre-commit framework to validate staged files before commit

Enable developers to run hallucination firewall automatically on git commits via the pre-commit framework. Validates only staged files with SQLite cache to maintain <500ms performance target.

## Key Insights

From research report:
- **Pre-commit framework:** YAML-driven hook system; processes only staged files
- **Entry point exists:** `firewall` console script already defined in `pyproject.toml`
- **Hook definition:** Create `.pre-commit-hooks.yaml` in repo root
- **Performance:** Cache results via existing SQLite cache; batch file processing
- **Configuration:** Support `.firewall.toml` in user repo

## Requirements

### Functional Requirements

1. Create `.pre-commit-hooks.yaml` hook definition file
2. Support filtering by file type (`types: [python]`)
3. Accept multiple files in single invocation (batch mode)
4. Read `.firewall.toml` config from user repo
5. Exit code 0 on success, 1 on validation errors
6. Display Rich terminal output for errors

### Non-Functional Requirements

- **Performance:** <500ms for typical commit (3-5 Python files)
- **Cache utilization:** Reuse SQLite cache from previous runs
- **User experience:** Clear error messages with line numbers
- **Compatibility:** Work with pre-commit framework 3.0+

## Architecture

### Hook Flow

```
git commit
    ↓
pre-commit framework
    ↓
reads .pre-commit-config.yaml (user repo)
    ↓
installs firewall from GitHub/PyPI
    ↓
runs: firewall check <staged-files>
    ↓
exit 0 (commit) or exit 1 (abort)
```

### Configuration Layers

```
User Repo
    .pre-commit-config.yaml  → specifies firewall hook
    .firewall.toml           → firewall-specific config

Firewall Repo
    .pre-commit-hooks.yaml   → hook definition (our file)
    pyproject.toml           → console_scripts entry (exists)
```

### Integration Point

No new code required. Existing CLI handles batch files:

```bash
firewall check file1.py file2.py file3.py
```

## Related Code Files

### Files to Create

- `.pre-commit-hooks.yaml` (repo root, 15 lines)
- `docs/pre-commit-setup.md` (usage documentation)

### Files to Modify

- `README.md` (add pre-commit section)
- `.firewall.toml` (create example config in repo root for testing)

### Files to Reference

- `pyproject.toml` (verify `[project.scripts]` entry exists)
- `src/hallucination_firewall/cli.py` (confirm batch file handling)
- `src/hallucination_firewall/config.py` (confirm `.firewall.toml` loading)

## Implementation Steps

### Step 1: Create Hook Definition File (20min)

File: `.pre-commit-hooks.yaml` (repo root)

```yaml
- id: firewall-check
  name: AI Hallucination Firewall
  description: Validate AI-generated code for hallucinated APIs and wrong signatures
  entry: firewall check
  language: python
  types: [python]
  stages: [commit]
  pass_filenames: true
  require_serial: false

- id: firewall-check-js
  name: AI Hallucination Firewall (JavaScript)
  description: Validate JavaScript/TypeScript code
  entry: firewall check
  language: python
  types: [javascript, jsx, ts, tsx]
  stages: [commit]
  pass_filenames: true
  require_serial: false
```

**Key fields:**
- `entry`: Command to run (uses our CLI)
- `language: python`: Hook runs in Python venv
- `types`: File filters (separate hooks for Python/JS)
- `pass_filenames: true`: Pass staged files as args
- `require_serial: false`: Can run in parallel with other hooks

### Step 2: Verify CLI Entry Point (5min)

Check `pyproject.toml` has:

```toml
[project.scripts]
firewall = "hallucination_firewall.cli:main"
```

This already exists. No changes needed.

### Step 3: Create Example User Config (15min)

File: `.pre-commit-config.yaml` (repo root, for testing)

```yaml
repos:
  - repo: https://github.com/tranhoangtu/AI-Hallucination-Firewall
    rev: v0.1.0  # Use specific tag in production
    hooks:
      - id: firewall-check
        types: [python]

  # Optional: JavaScript/TypeScript
  - repo: https://github.com/tranhoangtu/AI-Hallucination-Firewall
    rev: v0.1.0
    hooks:
      - id: firewall-check-js
        types: [javascript, jsx, ts, tsx]
```

### Step 4: Create Documentation (30min)

File: `docs/pre-commit-setup.md`

```markdown
# Pre-commit Hook Setup

## Installation

1. Install pre-commit framework:
   ```bash
   pip install pre-commit
   ```

2. Add to your `.pre-commit-config.yaml`:
   ```yaml
   repos:
     - repo: https://github.com/tranhoangtu/AI-Hallucination-Firewall
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

[firewall.registries]
pypi_enabled = true
npm_enabled = true
```

## Usage

Hooks run automatically on `git commit`. To run manually:

```bash
pre-commit run firewall-check --all-files
```

## Performance

- First run: ~2-3s (cache warm-up)
- Subsequent runs: <500ms (cache hits)
- Only validates staged files (not entire codebase)

## Troubleshooting

### Hook too slow
- Check cache directory: `~/.cache/hallucination-firewall/`
- Increase `cache_ttl_seconds` in `.firewall.toml`

### False positives
- Adjust `severity_threshold` to "error" (ignore warnings)
- Use `# firewall: disable` comment to skip validation

### Skip hook for one commit
```bash
git commit --no-verify
```
```

### Step 5: Update README (20min)

In `README.md`, add section after "Installation":

```markdown
## Pre-commit Hook

Automatically validate code on every commit:

```bash
# Install pre-commit
pip install pre-commit

# Add to .pre-commit-config.yaml
cat >> .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/tranhoangtu/AI-Hallucination-Firewall
    rev: v0.1.0
    hooks:
      - id: firewall-check
EOF

# Install hooks
pre-commit install
```

Now `firewall check` runs automatically on `git commit`. See [docs/pre-commit-setup.md](docs/pre-commit-setup.md) for configuration.
```

### Step 6: Test Hook Locally (30min)

```bash
# Install pre-commit in firewall repo
cd AI-Hallucination-Firewall
pip install pre-commit

# Install our own hook (dogfooding)
pre-commit install

# Create test file with hallucinated import
cat > test_hallucination.py << 'EOF'
import fakelib  # Should fail validation
import requests

def test():
    requests.get()  # Should fail (missing url)
EOF

# Stage file
git add test_hallucination.py

# Try to commit (should fail)
git commit -m "Test pre-commit hook"
# Expected: Hook fails, commit aborted, errors displayed

# Fix file
cat > test_hallucination.py << 'EOF'
import requests

def test():
    requests.get("https://example.com")
EOF

# Commit again (should pass)
git add test_hallucination.py
git commit -m "Fix hallucinations"
# Expected: Hook passes, commit succeeds
```

### Step 7: Performance Testing (20min)

Test with multiple files:

```bash
# Create 10 Python files
for i in {1..10}; do
  echo "import os" > test_file_$i.py
done

git add test_file_*.py

# Measure hook execution time
time git commit -m "Test batch performance"
# Target: <500ms
```

Check cache effectiveness:

```bash
# First commit (cold cache)
time git commit -m "First commit"

# Modify and commit again (warm cache)
echo "import sys" >> test_file_1.py
git add test_file_1.py
time git commit -m "Second commit"
# Should be significantly faster
```

### Step 8: Document Cache Behavior (10min)

Add to `docs/pre-commit-setup.md`:

```markdown
## Cache Management

Firewall uses SQLite cache to speed up repeated validations.

**Cache location:** `~/.cache/hallucination-firewall/registry_cache.db`

**Cache TTL:** Configurable via `.firewall.toml` (default 3600s)

**Clear cache:**
```bash
rm -rf ~/.cache/hallucination-firewall/
```

**Disable cache (for debugging):**
```bash
firewall check --no-cache file.py  # Add flag to CLI if needed
```
```

## Todo List

- [ ] Create `.pre-commit-hooks.yaml` in repo root
- [ ] Define `firewall-check` hook for Python
- [ ] Define `firewall-check-js` hook for JavaScript/TypeScript
- [ ] Verify `pyproject.toml` console_scripts entry exists
- [ ] Create example `.pre-commit-config.yaml` for testing
- [ ] Create `docs/pre-commit-setup.md` documentation
- [ ] Update README with pre-commit section
- [ ] Test hook installation in clean repo
- [ ] Test hook with valid staged files
- [ ] Test hook with invalid staged files (should abort commit)
- [ ] Performance test with 10+ files (<500ms target)
- [ ] Test cache warm-up and cache hits
- [ ] Document cache behavior and troubleshooting
- [ ] Add to CI/CD pipeline (run pre-commit in GitHub Actions)

## Success Criteria

### Functional

- [ ] Hook installs successfully via `pre-commit install`
- [ ] Hook runs automatically on `git commit`
- [ ] Hook validates only staged files (not entire repo)
- [ ] Hook aborts commit on validation errors
- [ ] Hook passes commit on clean code
- [ ] Hook respects `.firewall.toml` configuration

### Performance

- [ ] <500ms for typical commit (3-5 Python files)
- [ ] Cache reduces validation time by 80% on repeated runs
- [ ] Batch processing faster than serial file validation

### Code Quality

- [ ] Documentation covers installation, configuration, troubleshooting
- [ ] Example configs work copy-paste
- [ ] No breaking changes to existing CLI behavior

## Risk Assessment

### Potential Issues

1. **Hook too slow for large commits**
   - **Mitigation:** SQLite cache + parallel file processing
   - **Fallback:** Users can skip with `--no-verify` for urgent commits
   - **Monitoring:** Document performance expectations in docs

2. **Cache conflicts in shared environments**
   - **Mitigation:** Cache is user-scoped (`~/.cache/`)
   - **Edge case:** Docker containers (cache not persisted)
   - **Solution:** Document cache volume mounting for containers

3. **Version conflicts with other pre-commit hooks**
   - **Mitigation:** Pin Python version in hook definition
   - **Test:** Run alongside popular hooks (black, ruff, mypy)

4. **Network timeouts during commit**
   - **Mitigation:** Existing timeout handling in registries (10s default)
   - **Fallback:** Fail-open strategy; log warning, allow commit

## Security Considerations

### Git Hook Safety

- **No code execution:** Hook only validates via AST/API checks
- **No file modification:** Read-only validation (no auto-fix)
- **Bypass option:** Users can skip with `--no-verify` (standard git)

### Cache Security

- **Cache poisoning:** SQLite cache stores only PyPI/npm metadata
- **No credentials:** Cache contains no secrets or auth tokens
- **Permissions:** Cache directory user-scoped (0700 permissions)

### Network Requests

- **HTTPS only:** PyPI/npm API calls use HTTPS
- **Timeout protection:** 10s max per request
- **Rate limiting:** Respect registry rate limits (cached responses)

## Next Steps

After Phase 3 completion:

1. **Phase 4:** Create VS Code extension calling same `/validate` API
2. **Documentation:** Add video tutorial for pre-commit setup
3. **CI/CD examples:** GitHub Actions, GitLab CI, Jenkins integration
4. **Community:** Submit PR to pre-commit/pre-commit-hooks repo for discoverability

## Configurable Fail Behavior (Added from Validation Session 1)
<!-- Updated: Validation Session 1 - Add configurable fail_on_network_error -->

**Config option in `.firewall.toml`:**
```toml
[firewall]
fail_on_network_error = false  # Default: fail-open (allow commit on network error)
```

**Implementation:**
- Add `fail_on_network_error: bool = False` to `FirewallConfig` model in `models.py`
- Update `config.py` to parse this option
- In registry clients: if `fail_on_network_error=True`, re-raise `httpx.HTTPError` instead of returning True
- Pre-commit hook behavior: `fail_on_network_error=false` → warn + allow commit; `true` → block commit

**Use cases:**
- Individual devs: fail-open (default) — don't block workflow
- Enterprise teams: fail-closed — enforce strict validation

**Effort increase:** +30min (total phase: ~2.5h)

## Unresolved Questions

1. **Parallel file processing:** Should we validate files in parallel? → No for v1 (serial is simpler); add `--parallel` flag in v2
2. **Incremental validation:** Should we store validation results per-file hash? → Yes, add in v2 (skip unchanged files)
3. **Auto-fix mode:** Should hook suggest fixes? → No, validation only; auto-fix in separate tool
4. **Commit message validation:** Should we check commit messages for "AI" mentions? → No, out of scope
