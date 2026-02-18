# AI Hallucination Firewall - VS Code Extension

Real-time validation for AI-generated code. Detects hallucinated APIs, wrong signatures, and nonexistent packages.

## Prerequisites

Start the Hallucination Firewall API server:

```bash
pip install hallucination-firewall
firewall serve
```

Verify: `curl http://localhost:8000/health`

## Features

- **Inline Diagnostics** — Squiggly underlines for errors/warnings
- **Multi-Language** — Python, JavaScript, TypeScript
- **Configurable Trigger** — On save (default) or on change with debounce
- **Status Bar** — Shows validation state (OK / errors / offline)

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `apiEndpoint` | `http://localhost:8000` | API server URL |
| `debounceDelay` | `500` | Debounce delay (ms) for onChange mode |
| `enabled` | `true` | Toggle validation |
| `triggerMode` | `onSave` | `onSave` or `onChange` |

## Usage

1. Start API server: `firewall serve`
2. Open a Python/JS/TS file
3. Errors appear as inline diagnostics
4. Hover for details

## Development

```bash
cd vscode-extension
npm install
npm run compile
```

Press F5 in VS Code to launch Extension Development Host.
