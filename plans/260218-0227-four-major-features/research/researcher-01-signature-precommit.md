# Research Report: Function Signature Validation & Pre-commit Integration
**Date:** 2026-02-18 | **Project:** AI Hallucination Firewall

## Topic 1: Python Function Signature Validation

### Extraction: tree-sitter vs AST

**tree-sitter (Recommended)**
- S-expression queries: `(call function: (identifier) @fn arguments: (argument_list) @args)`
- Graceful handling of incomplete/malformed code (critical for AI hallucinations)
- Structured match captures for processing

**Python AST Module**
- Built-in; strict validation; fails on malformed code
- Not ideal for LLM-generated content

**Choice:** tree-sitter

### Signature Lookup Methods

| Method | Coverage | Speed | Best For |
|--------|----------|-------|----------|
| **Jedi + typeshed** | stdlib + 1000+ packages | Fast | Primary lookup |
| **inspect.signature()** | Installed packages only | Fastest | Runtime fallback |
| **MyPy stubs** | Full type info | Slower | Type validation |
| **PyPI metadata** | Limited | Slow | Unknown packages |

**Recommended Stack:**
1. Extract call sites via tree-sitter
2. Lookup signatures: Jedi → typeshed stubs
3. Fallback: inspect.signature() for installed pkgs
4. Validate: arg count, types, keyword names

---

## Topic 2: Git Pre-commit Hook Integration

### Pre-commit Framework Overview

**Core Concept**
- YAML-driven hook framework (`.pre-commit-config.yaml` in user repo)
- Hooks defined in `.pre-commit-hooks.yaml` (hook provider repo)
- Runs on git commit; configurable stages: commit, push, merge-commit, etc.
- Performance: Only processes staged files; minimal overhead

**Installation**
```bash
pip install pre-commit
pre-commit install  # Installs .git/hooks/pre-commit
```

### Custom Hook Configuration

**.pre-commit-hooks.yaml (hook provider - our firewall repo)**
```yaml
- id: firewall-check
  name: AI Hallucination Firewall
  entry: firewall check
  language: python
  types: [python]
  stages: [commit]
```

**setup.py Entry Point (firewall package)**
```python
entry_points={
    'console_scripts': [
        'firewall=hallucination_firewall.cli:main',
    ]
}
```

This creates `/path/.venv/bin/firewall` executable when installed.

**.pre-commit-config.yaml (user project)**
```yaml
repos:
  - repo: https://github.com/tranhoangtu/AI-Hallucination-Firewall
    rev: v1.0.0
    hooks:
      - id: firewall-check
        types: [python]
```

### Performance Optimization

**Best Practices**
- Filter by file type: `types: [python]` reduces hook runs
- Process only staged files: Pre-commit handles this automatically
- Batch file processing: Accept multiple files in single invocation
- Cache results: SQLite cache (existing in firewall arch) prevents re-validation
- Async hooks: Mark as `pass_filenames: false` to batch process

**Avoid**
- Running heavy I/O per file (PyPI checks already cached)
- Re-parsing same files (use caching layer)
- Subprocess overhead: Use direct Python calls when possible

---

## Implementation Roadmap

1. **Signature Extractor Module**
   - tree-sitter query executor for `call_expression` nodes
   - Jedi wrapper for signature lookups with caching
   - Comparison logic (arity, types, keywords)

2. **Pre-commit Hook Scaffold**
   - Update `setup.py` with firewall console_scripts entry
   - Create `.pre-commit-hooks.yaml` in repo root
   - CLI accepts `--check-mode=pre-commit` to optimize for staged files

3. **Integration Testing**
   - Test hook with user `.pre-commit-config.yaml`
   - Verify signature validation on staged code
   - Performance profiling on real projects

---

## Unresolved Questions

1. **Jedi caching layer:** Should we cache full Jedi AST or just signature results?
2. **Stub freshness:** How often to refresh typeshed snapshot (pinned version vs. live)?
3. **PyPI signature validation:** For packages not in typeshed, fallback strategy?
4. **Hook performance target:** <500ms per invocation on typical commit?

---

## Sources

- [tree-sitter Python Bindings](https://github.com/tree-sitter/py-tree-sitter)
- [tree-sitter Query Syntax](https://tree-sitter.github.io/tree-sitter/using-parsers/queries/1-syntax.html)
- [Jedi Documentation](https://jedi.readthedocs.io/en/latest/docs/api-classes.html)
- [Python inspect Module](https://docs.python.org/3/library/inspect.html)
- [pre-commit Framework](https://pre-commit.com/)
- [Pre-commit Custom Hooks Guide](https://stefaniemolin.com/articles/devx/pre-commit/hook-creation-guide/)
- [Pre-commit Hook Creation with Python](https://medium.com/@slash.gordon.dev/supercharge-your-workflow-with-pre-commit-how-to-create-custom-hooks-2cbe6ca4c6df)
- [Tree-sitter Query Tips](https://cycode.com/blog/tips-for-using-tree-sitter-queries/)
