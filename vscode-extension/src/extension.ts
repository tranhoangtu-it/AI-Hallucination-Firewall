import * as vscode from "vscode";
import { ValidationClient } from "./validation-client";
import { mapIssueToDiagnostic } from "./diagnostics-mapper";

const SUPPORTED_LANGUAGES = ["python", "javascript", "typescript"];

let diagnosticCollection: vscode.DiagnosticCollection;
let client: ValidationClient;
let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext): void {
  diagnosticCollection = vscode.languages.createDiagnosticCollection(
    "hallucination-firewall"
  );
  client = new ValidationClient();
  statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    100
  );
  statusBarItem.text = "$(shield) Firewall";
  statusBarItem.show();

  context.subscriptions.push(diagnosticCollection, statusBarItem);

  // Register event listeners based on trigger mode
  registerListeners(context);

  // Listen for config changes to re-register listeners
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration("hallucinationFirewall")) {
        registerListeners(context);
      }
    })
  );

  // Validate all open documents on activation
  for (const doc of vscode.workspace.textDocuments) {
    if (shouldValidate(doc)) {
      validateDocument(doc);
    }
  }
}

const disposables: vscode.Disposable[] = [];

function registerListeners(context: vscode.ExtensionContext): void {
  // Dispose previous listeners
  for (const d of disposables) {
    d.dispose();
  }
  disposables.length = 0;

  const triggerMode = vscode.workspace
    .getConfiguration("hallucinationFirewall")
    .get<string>("triggerMode", "onSave");

  // Always validate on open
  disposables.push(
    vscode.workspace.onDidOpenTextDocument((doc) => {
      if (shouldValidate(doc)) {
        validateDocument(doc);
      }
    })
  );

  if (triggerMode === "onChange") {
    disposables.push(
      vscode.workspace.onDidChangeTextDocument((event) => {
        if (shouldValidate(event.document)) {
          client.debounce(() => validateDocument(event.document));
        }
      })
    );
  } else {
    // onSave mode (default)
    disposables.push(
      vscode.workspace.onDidSaveTextDocument((doc) => {
        if (shouldValidate(doc)) {
          validateDocument(doc);
        }
      })
    );
  }

  // Clear diagnostics on close
  disposables.push(
    vscode.workspace.onDidCloseTextDocument((doc) => {
      diagnosticCollection.delete(doc.uri);
    })
  );

  context.subscriptions.push(...disposables);
}

function shouldValidate(document: vscode.TextDocument): boolean {
  const enabled = vscode.workspace
    .getConfiguration("hallucinationFirewall")
    .get<boolean>("enabled", true);
  if (!enabled) {
    return false;
  }
  return SUPPORTED_LANGUAGES.includes(document.languageId);
}

async function validateDocument(document: vscode.TextDocument): Promise<void> {
  try {
    statusBarItem.text = "$(loading~spin) Validating...";
    const code = document.getText();
    const language = document.languageId;

    const result = await client.validateCode(code, language);
    const diagnostics = result.issues.map(mapIssueToDiagnostic);
    diagnosticCollection.set(document.uri, diagnostics);

    const errorCount = result.issues.filter(
      (i) => i.severity === "error"
    ).length;
    statusBarItem.text =
      errorCount > 0
        ? `$(error) Firewall: ${errorCount} issue(s)`
        : "$(shield) Firewall: OK";
  } catch {
    diagnosticCollection.delete(document.uri);
    statusBarItem.text = "$(warning) Firewall: offline";
  }
}

export function deactivate(): void {
  client?.dispose();
  diagnosticCollection?.dispose();
}
