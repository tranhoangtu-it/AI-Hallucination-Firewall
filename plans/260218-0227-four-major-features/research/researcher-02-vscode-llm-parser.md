# Research Report: VS Code Extension & LLM Output Parser
**Date:** 2026-02-18 | **Topics:** VS Code extension validation API, LLM markdown code parsing

---

## Topic 1: VS Code Extension for Code Validation

### DiagnosticCollection API
- Core mechanism: `languages.createDiagnosticsCollection(collectionName)`
- Stores diagnostic issues (errors/warnings) mapped to file URIs
- Severities: Error, Warning, Information, Hint
- Properties: message, range (line/column), relatedInformation, code, source
- Clear diagnostics with `collection.clear()` or `collection.set(uri, [])`

### Real-Time Validation Strategy
**Event-Driven (Recommended for HTTP validation)**
- Listen to `workspace.onDidChangeTextDocument` for every keystroke
- **Pros:** Immediate feedback; responsive UX
- **Cons:** High validation frequency; network overhead if calling REST API per keystroke

**Save-Based (Conservative)**
- Listen to `workspace.onDidSaveTextDocument` only on file save
- **Pros:** Lower server load; cleaner request pattern
- **Cons:** Delayed feedback; poor UX for real-time scenarios

### Debounce Pattern (Critical for HTTP)
```typescript
// Recommended: debounce on keystroke to avoid API spam
const debounceMs = 500; // wait 500ms after last change
let debounceTimer: NodeJS.Timeout;

workspace.onDidChangeTextDocument(event => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    validateViaAPI(event.document);  // Call POST /validate
  }, debounceMs);
});
```

### HTTP API Integration
- **Built-in Options:** VS Code runs on Node.js; use native `fetch()` (Node 18+) or `node-fetch` package
- **Axios Alternative:** `axios` works in extensions but adds dependency weight (~50kb)
- **Implementation Pattern:**
  ```typescript
  const response = await fetch('http://localhost:8000/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code: document.getText(), language })
  });
  const result = await response.json();  // Expect list of Diagnostic objects
  diagnosticsCollection.set(document.uri, result);
  ```

### Extension Manifest (package.json)
- **Activation Events:** `onLanguage:python`, `onLanguage:javascript` (lazy load)
- **Capabilities:** `activationEvents`, `contributes.languages`, `main` entry point
- **Permissions:** No special permissions needed for workspace/document events

### Implementation Checklist
- [ ] Create DiagnosticCollection in `activate()`
- [ ] Subscribe to `workspace.onDidChangeTextDocument` with debounce
- [ ] Map response from `/validate` to VS Code Diagnostic objects
- [ ] Handle network errors gracefully; clear diagnostics on failure
- [ ] Consider settings: debounce delay, API endpoint URL, language selector

---

## Topic 2: LLM Output Parser for Code Blocks

### Markdown Code Block Format
**Standard Fenced Code Block (CommonMark):**
```
​```python
import os
```
```
**Regex Pattern for Extraction:**
```python
import re
# Matches: ​```[language]\n[code]\n​```
pattern = r'```([^\n]*)\n(.*?)\n```'
matches = re.findall(pattern, text, re.DOTALL)
# Returns: [(language, code), ...]
```

### Language Detection Heuristics
1. **Explicit Tag:** Parse language from fence tag (e.g., `​```python` → "python")
2. **Fallback Heuristics:**
   - JSON: Try `json.loads()` parsing
   - XML/HTML: Check for `<tag>` patterns
   - SQL: Check for `SELECT`, `INSERT`, `UPDATE` keywords
   - Shell: Check for `$`, `#!/bin/bash` patterns
3. **Default:** Return empty language string; let consumer decide

### Handling Multiple Code Blocks
- LLM outputs often contain multiple blocks (preamble code, class defs, tests)
- Use `re.findall()` or iterate with `re.finditer()` to capture all blocks
- Maintain block order and metadata (line number, language per block)
- Handle edge cases: nested backticks, code-in-comments

### LLM Output Formats
**ChatGPT/Claude Standard:**
```
Here's the implementation:
​```python
def hello():
    pass
```
```

**Copilot Variant:** May include filenames in comments or headers:
```
// filename: app.js
​```javascript
function main() {}
```
```

**Multi-File Format (llm-code-format reference):**
- Heading-based: `## filename.py` followed by `​```python​```
- Bold format: `**filename.py**` followed by `​```​```
- Handles multiple files in single response; requires tracking state

### Python Libraries for Parsing

| Library | Speed | CommonMark | Plugins | Best For |
|---------|-------|-----------|---------|----------|
| **mistune** | 3.6s | Sane subset | Yes | Fast parsing; custom renderers |
| **markdown-it-py** | 9.0s | Strict | Yes | CommonMark compliance |
| **marko** | N/A | GFM support | Yes | GitHub Markdown (tables, strikethrough) |

**Recommendation for Firewall:**
- Use `mistune` with custom renderer for code block extraction (no dependency bloat)
- Or regex-based: simple regex pattern + `re` stdlib (zero dependencies)

### Implementation Approach
```python
import re

def extract_code_blocks(llm_output: str) -> list[dict]:
    """Extract code blocks from LLM markdown response."""
    pattern = r'```([^\n]*)\n(.*?)\n```'
    blocks = []
    for lang, code in re.findall(pattern, llm_output, re.DOTALL):
        blocks.append({
            'language': lang.strip() or 'text',
            'code': code.strip()
        })
    return blocks
```

### Integration with Firewall Validation
1. Receive LLM response (markdown format)
2. Extract code blocks using regex or parser
3. For each block: call validation pipeline with detected language
4. Aggregate results; report per-block findings
5. Highlight problematic blocks in VS Code via diagnostics

---

## Recommendations for AI Hallucination Firewall

### Short Term (MVP)
- **VS Code Extension:** Simple debounce-based HTTP client; call `/validate` endpoint with code
- **LLM Parser:** Regex-based extraction; support Python, JavaScript, TypeScript initially
- **No external parsing libs:** Keep extension lightweight

### Medium Term
- **Parser Library:** If supporting complex Markdown (nested blocks, multi-file), adopt `mistune`
- **Extension Enhancement:** Settings UI for debounce delay, language selection, severity filtering
- **Batch Validation:** Support multi-block responses from single LLM call

### Technical Debt Considerations
- LLMs don't enforce Markdown structure (one token at a time); expect edge cases
- Network latency during keystroke validation: plan for offline fallback or caching
- Parser robustness: test with real LLM outputs (ChatGPT, Claude, Copilot samples)

---

## Unresolved Questions
1. Should debounce delay be user-configurable or fixed? (Recommend: fixed 500ms, user-configurable in v2)
2. Support multiple LLM providers simultaneously in one response parsing?
3. Should VS Code extension validate on open, or only on edit/save?
4. Cache regex-compiled patterns or compile fresh each parse? (Compile once at module level)

---

## Sources
- [VS Code API Reference](https://code.visualstudio.com/api/references/vscode-api)
- [VS Code Extension Sample: Diagnostics](https://github.com/microsoft/vscode-extension-samples/blob/main/code-actions-sample/src/diagnostics.ts)
- [How to Make API Calls in VS Code Extensions](https://medium.com/@angelinatsuboi/how-to-make-api-calls-in-your-vs-code-extension-60dbaf7cf448)
- [LLM Code Format Parser](https://github.com/curran/llm-code-format)
- [Mistune Markdown Parser](https://mistune.lepture.com/)
- [Why Can't AI Models Output Clean Markdown?](https://medium.com/@CultmanSachs/why-cant-ai-models-output-clean-markdown-a-technical-mess-that-still-isn-t-fixed-1dc70ff366a3)
