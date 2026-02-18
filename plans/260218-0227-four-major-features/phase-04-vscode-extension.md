# Phase 4: VS Code Extension

## Context Links

- Research: [researcher-02-vscode-llm-parser.md](./research/researcher-02-vscode-llm-parser.md)
- API Server: `src/hallucination_firewall/server.py`
- Models: `src/hallucination_firewall/models.py`
- VS Code API: https://code.visualstudio.com/api/references/vscode-api

## Overview

**Priority:** P2
**Status:** Complete
**Effort:** 5h
**Goal:** TypeScript extension providing real-time validation via inline diagnostics

Enable developers to see hallucination warnings directly in VS Code as they type. Extension calls FastAPI `/validate` endpoint with debounce, displays inline squiggly lines for errors/warnings.

## Key Insights

From research report:
- **DiagnosticCollection API:** Core VS Code mechanism for showing inline errors
- **Debounce strategy:** 500ms delay after last keystroke (prevent API spam)
- **HTTP client:** Use native `fetch()` (Node 18+) or `node-fetch` package
- **Activation events:** `onLanguage:python`, `onLanguage:javascript` (lazy load)
- **Severities:** Map to VS Code enum: Error, Warning, Information, Hint

## Requirements

### Functional Requirements

1. Activate on opening Python, JavaScript, TypeScript files
2. Listen to document changes with 500ms debounce
3. Call `POST /validate` with code + language
4. Map `ValidationIssue` to VS Code `Diagnostic` objects
5. Display inline diagnostics with squiggly underlines
6. Support configurable API endpoint URL
7. Handle network errors gracefully (clear diagnostics)

### Non-Functional Requirements

- **Performance:** <100ms perceived latency after debounce
- **Resource usage:** Clear diagnostics on file close (prevent memory leak)
- **User experience:** Status bar shows validation state
- **Compatibility:** VS Code 1.80+ (Node 18+)

## Architecture

### Component Design

```
Extension
    ├── extension.ts          → activate(), deactivate()
    ├── validator.ts          → ValidationClient class
    ├── diagnostics.ts        → mapIssueToDiagnostic()
    └── config.ts             → loadConfig()

ValidationClient
    ├── validateCode(code, language) → Promise<Diagnostic[]>
    ├── debounce(handler, delay) → debounced function
    └── fetch(endpoint, body) → HTTP call
```

### Data Flow

```
User types code
    ↓
onDidChangeTextDocument event
    ↓
Debounce (500ms)
    ↓
ValidationClient.validateCode()
    ↓
POST http://localhost:8000/validate
    ↓
Response: ValidationResult JSON
    ↓
Map to VS Code Diagnostic[]
    ↓
DiagnosticCollection.set(uri, diagnostics)
    ↓
Inline squiggly lines appear
```

### API Integration

Extension sends:
```json
POST /validate
{
  "code": "import fakelib\nimport requests",
  "language": "python"
}
```

Server responds:
```json
{
  "file": "<stdin>",
  "language": "python",
  "issues": [
    {
      "severity": "error",
      "issue_type": "nonexistent_package",
      "location": {"file": "<stdin>", "line": 1, "column": 0},
      "message": "Package 'fakelib' not found on PyPI",
      "confidence": 0.95
    }
  ],
  "passed": false
}
```

## Related Code Files

### Files to Create

- `vscode-extension/package.json` (extension manifest, 60 lines)
- `vscode-extension/tsconfig.json` (TypeScript config, 20 lines)
- `vscode-extension/src/extension.ts` (entry point, 80 lines)
- `vscode-extension/src/validation-client.ts` (HTTP client, 100 lines)
- `vscode-extension/src/diagnostics-mapper.ts` (mapping logic, 50 lines)
- `vscode-extension/.vscodeignore` (packaging excludes)
- `vscode-extension/README.md` (extension docs)

### Files to Reference

- `src/hallucination_firewall/server.py` (API contract)
- `src/hallucination_firewall/models.py` (response schema)

## Implementation Steps

### Step 1: Initialize Extension Project (20min)

```bash
cd vscode-extension
npm init -y
npm install --save-dev @types/vscode @types/node typescript vscode-test
npm install node-fetch  # HTTP client (if not using native fetch)
```

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "ES2020",
    "outDir": "out",
    "lib": ["ES2020"],
    "sourceMap": true,
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true
  },
  "exclude": ["node_modules", ".vscode-test"]
}
```

### Step 2: Create Extension Manifest (45min)

File: `vscode-extension/package.json`

```json
{
  "name": "hallucination-firewall",
  "displayName": "AI Hallucination Firewall",
  "description": "Real-time validation for AI-generated code",
  "version": "0.1.0",
  "publisher": "tranhoangtu",
  "engines": {
    "vscode": "^1.80.0"
  },
  "categories": ["Linters"],
  "activationEvents": [
    "onLanguage:python",
    "onLanguage:javascript",
    "onLanguage:typescript"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "configuration": {
      "title": "Hallucination Firewall",
      "properties": {
        "hallucinationFirewall.apiEndpoint": {
          "type": "string",
          "default": "http://localhost:8000",
          "description": "Validation API endpoint URL"
        },
        "hallucinationFirewall.debounceDelay": {
          "type": "number",
          "default": 500,
          "description": "Debounce delay in milliseconds"
        },
        "hallucinationFirewall.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable/disable validation"
        }
      }
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "lint": "eslint src --ext ts"
  },
  "devDependencies": {
    "@types/vscode": "^1.80.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
```

### Step 3: Create Validation Client (90min)

File: `vscode-extension/src/validation-client.ts`

```typescript
import * as vscode from 'vscode';

interface ValidationRequest {
  code: string;
  language: string;
}

interface SourceLocation {
  file: string;
  line: number;
  column: number;
  end_line?: number;
  end_column?: number;
}

interface ValidationIssue {
  severity: 'error' | 'warning' | 'info';
  issue_type: string;
  location: SourceLocation;
  message: string;
  suggestion?: string;
}

interface ValidationResult {
  file: string;
  language: string;
  issues: ValidationIssue[];
  passed: boolean;
}

export class ValidationClient {
  private apiEndpoint: string;
  private debounceDelay: number;
  private debounceTimer?: NodeJS.Timeout;

  constructor() {
    this.apiEndpoint = this.getConfig('apiEndpoint');
    this.debounceDelay = this.getConfig('debounceDelay');
  }

  private getConfig<T>(key: string): T {
    const config = vscode.workspace.getConfiguration('hallucinationFirewall');
    return config.get<T>(key)!;
  }

  async validateCode(code: string, language: string): Promise<ValidationResult> {
    const url = `${this.apiEndpoint}/validate`;
    const body: ValidationRequest = { code, language };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(5000), // 5s timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Validation API error:', error);
      throw error;
    }
  }

  debounce(handler: () => void): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    this.debounceTimer = setTimeout(handler, this.debounceDelay);
  }
}
```

### Step 4: Create Diagnostics Mapper (45min)

File: `vscode-extension/src/diagnostics-mapper.ts`

```typescript
import * as vscode from 'vscode';

interface ValidationIssue {
  severity: 'error' | 'warning' | 'info';
  issue_type: string;
  location: {
    line: number;
    column: number;
    end_line?: number;
    end_column?: number;
  };
  message: string;
  suggestion?: string;
}

export function mapIssueToDiagnostic(issue: ValidationIssue): vscode.Diagnostic {
  const line = Math.max(0, issue.location.line - 1); // VS Code uses 0-indexed lines
  const column = issue.location.column;
  const endLine = issue.location.end_line ? issue.location.end_line - 1 : line;
  const endColumn = issue.location.end_column ?? column + 10; // Default span

  const range = new vscode.Range(
    new vscode.Position(line, column),
    new vscode.Position(endLine, endColumn)
  );

  const severity = mapSeverity(issue.severity);
  const message = issue.suggestion
    ? `${issue.message}\n💡 Suggestion: ${issue.suggestion}`
    : issue.message;

  const diagnostic = new vscode.Diagnostic(range, message, severity);
  diagnostic.source = 'hallucination-firewall';
  diagnostic.code = issue.issue_type;

  return diagnostic;
}

function mapSeverity(severity: string): vscode.DiagnosticSeverity {
  switch (severity) {
    case 'error':
      return vscode.DiagnosticSeverity.Error;
    case 'warning':
      return vscode.DiagnosticSeverity.Warning;
    case 'info':
      return vscode.DiagnosticSeverity.Information;
    default:
      return vscode.DiagnosticSeverity.Hint;
  }
}
```

### Step 5: Create Extension Entry Point (90min)

File: `vscode-extension/src/extension.ts`

```typescript
import * as vscode from 'vscode';
import { ValidationClient } from './validation-client';
import { mapIssueToDiagnostic } from './diagnostics-mapper';

let diagnosticCollection: vscode.DiagnosticCollection;
let validationClient: ValidationClient;

export function activate(context: vscode.ExtensionContext) {
  console.log('Hallucination Firewall extension activated');

  diagnosticCollection = vscode.languages.createDiagnosticCollection('hallucination-firewall');
  validationClient = new ValidationClient();

  context.subscriptions.push(diagnosticCollection);

  // Validate on document change (with debounce)
  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument(event => {
      const doc = event.document;
      if (shouldValidate(doc)) {
        validationClient.debounce(() => validateDocument(doc));
      }
    })
  );

  // Validate on document open
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(doc => {
      if (shouldValidate(doc)) {
        validateDocument(doc);
      }
    })
  );

  // Clear diagnostics on document close
  context.subscriptions.push(
    vscode.workspace.onDidCloseTextDocument(doc => {
      diagnosticCollection.delete(doc.uri);
    })
  );

  // Validate all open documents on activation
  vscode.workspace.textDocuments.forEach(doc => {
    if (shouldValidate(doc)) {
      validateDocument(doc);
    }
  });
}

function shouldValidate(document: vscode.TextDocument): boolean {
  const config = vscode.workspace.getConfiguration('hallucinationFirewall');
  if (!config.get<boolean>('enabled')) {
    return false;
  }

  const supportedLanguages = ['python', 'javascript', 'typescript'];
  return supportedLanguages.includes(document.languageId);
}

async function validateDocument(document: vscode.TextDocument): Promise<void> {
  try {
    const code = document.getText();
    const language = document.languageId;

    const result = await validationClient.validateCode(code, language);

    const diagnostics = result.issues.map(mapIssueToDiagnostic);
    diagnosticCollection.set(document.uri, diagnostics);

  } catch (error) {
    console.error('Validation failed:', error);
    // Clear diagnostics on error (fail gracefully)
    diagnosticCollection.delete(document.uri);

    // Show error in status bar
    vscode.window.showErrorMessage(
      'Hallucination Firewall: Validation API unavailable. Is the server running?'
    );
  }
}

export function deactivate() {
  diagnosticCollection?.dispose();
}
```

### Step 6: Create Extension README (30min)

File: `vscode-extension/README.md`

```markdown
# AI Hallucination Firewall - VS Code Extension

Real-time validation for AI-generated code. Detects hallucinated APIs, wrong signatures, and nonexistent packages.

## Features

- **Inline Diagnostics**: See errors as you type with squiggly underlines
- **Multi-Language**: Supports Python, JavaScript, TypeScript
- **Fast**: 500ms debounce for responsive validation
- **Configurable**: Customize API endpoint and delay

## Prerequisites

1. Install and run the Hallucination Firewall API server:
   ```bash
   pip install hallucination-firewall
   firewall serve
   ```

2. Verify server is running: http://localhost:8000/health

## Configuration

Open VS Code Settings and search for "Hallucination Firewall":

- **API Endpoint**: `http://localhost:8000` (default)
- **Debounce Delay**: `500` ms (default)
- **Enabled**: `true` (toggle validation)

## Usage

1. Open a Python/JavaScript file
2. Extension auto-activates and validates on save/change
3. Hover over squiggly lines to see error details
4. Click on suggestion lightbulb for fixes

## Known Issues

- Requires running API server (not bundled)
- Network latency may cause delays on slow connections
- Large files (>5MB) may timeout

## Release Notes

### 0.1.0
- Initial release
- Python, JavaScript, TypeScript support
- Debounced validation
```

### Step 7: Build and Test Extension (45min)

```bash
cd vscode-extension

# Compile TypeScript
npm run compile

# Open extension host for testing
code --extensionDevelopmentPath=$(pwd) ../AI-Hallucination-Firewall

# In extension host:
# 1. Open test file: test_hallucination.py
# 2. Type: import fakelib
# 3. Wait 500ms
# 4. See red squiggly line
```

Test cases:
- [ ] Extension activates on opening Python file
- [ ] Diagnostics appear after 500ms debounce
- [ ] Red squiggly for errors, yellow for warnings
- [ ] Diagnostics clear on closing file
- [ ] Error message shown if server offline
- [ ] Configuration changes take effect

### Step 8: Package Extension (30min)

```bash
# Install vsce (VS Code packaging tool)
npm install -g @vscode/vsce

# Package extension
vsce package
# Creates: hallucination-firewall-0.1.0.vsix

# Install locally
code --install-extension hallucination-firewall-0.1.0.vsix

# Test installed extension
code .
```

## Todo List

- [ ] Initialize extension project with npm
- [ ] Create `package.json` manifest
- [ ] Create `tsconfig.json` TypeScript config
- [ ] Implement `ValidationClient` class
- [ ] Implement `mapIssueToDiagnostic()` function
- [ ] Implement `extension.ts` entry point
- [ ] Add debounce logic for text changes
- [ ] Add configuration settings
- [ ] Create extension README
- [ ] Test extension in Extension Development Host
- [ ] Test with API server offline (graceful failure)
- [ ] Test with multiple files open
- [ ] Test configuration changes
- [ ] Package extension with vsce
- [ ] Install and test packaged .vsix
- [ ] Create demo video/GIF
- [ ] Publish to VS Code marketplace (optional)

## Success Criteria

### Functional

- [ ] Extension activates on opening Python/JS/TS files
- [ ] Diagnostics appear within 600ms after typing stops
- [ ] Errors show red squiggly lines
- [ ] Warnings show yellow squiggly lines
- [ ] Hover shows full error message
- [ ] Configuration changes apply without restart
- [ ] Graceful degradation when server offline

### Performance

- [ ] <100ms overhead after debounce (API call time)
- [ ] Zero memory leaks on opening/closing files
- [ ] Extension size <500KB packaged

### Code Quality

- [ ] TypeScript compiles without errors
- [ ] No runtime errors in Extension Host
- [ ] Clean console logs (no spam)

## Risk Assessment

### Potential Issues

1. **API server not running**
   - **Mitigation:** Show error message, clear diagnostics (fail gracefully)
   - **UX:** Add status bar indicator (🔴 offline, 🟢 online)

2. **Network latency on remote servers**
   - **Mitigation:** 5s timeout on fetch(), show "validating..." message
   - **Future:** Add offline mode with cached results

3. **Debounce delay too short (API spam)**
   - **Mitigation:** Default 500ms tested with typical typing speed
   - **Configuration:** Allow users to increase delay

4. **Large file timeout**
   - **Mitigation:** Server-side 5MB limit; extension shows timeout error
   - **Future:** Add client-side file size check before sending

## Security Considerations

### Network Security

- **HTTPS support:** Allow users to configure `https://` endpoints
- **No credentials:** Extension doesn't store API keys (future feature)
- **CORS:** Server must allow VS Code origin (already configured in FastAPI)

### Code Privacy

- **Local server default:** Code sent to `localhost:8000` (stays on machine)
- **User awareness:** Document that code is sent over network
- **Opt-out:** Users can disable extension in settings

### Extension Permissions

- **No special permissions:** Uses only standard VS Code APIs
- **No telemetry:** Extension doesn't collect usage data
- **Open source:** Code auditable on GitHub

## Next Steps

After Phase 4 completion:

1. **Marketplace publication:** Publish to VS Code marketplace
2. **Demo content:** Create video tutorial and GIF demos
3. **Analytics:** Add opt-in telemetry for error tracking
4. **Advanced features:**
   - Quick fixes (code actions) for common issues
   - Inline suggestions with AI explanations
   - Multi-file validation (entire workspace)
   - Offline mode with cached validation rules

## Configurable Trigger Mode (Added from Validation Session 1)
<!-- Updated: Validation Session 1 - Configurable trigger (default on-save, toggle on-change) -->

**Settings update in `package.json`:**
```json
"hallucinationFirewall.triggerMode": {
  "type": "string",
  "enum": ["onSave", "onChange"],
  "default": "onSave",
  "description": "When to trigger validation: onSave (default) or onChange (real-time with debounce)"
}
```

**Implementation in `extension.ts`:**
- Read `triggerMode` from config
- If `onSave`: use `onDidSaveTextDocument` only
- If `onChange`: use `onDidChangeTextDocument` with debounce
- Both modes: validate on open (`onDidOpenTextDocument`)
- Listen for config changes to switch mode without restart

**Rationale:** Default on-save reduces API calls, on-change gives real-time feedback. User chooses based on server capacity.

**Effort increase:** +30min (total phase: ~5.5h)

## Unresolved Questions

1. **Should extension bundle the API server?** → No for v1 (keep separate); consider Electron bundling in v2
2. **Support remote API servers (cloud)?** → Yes, configurable via settings; add auth in v2
3. **Code actions for auto-fix?** → Yes, add in v2 (e.g., "Install package", "Fix signature")
4. **Should we validate on open or only on change?** → Both; validate on open for immediate feedback
