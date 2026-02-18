"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const validation_client_1 = require("./validation-client");
const diagnostics_mapper_1 = require("./diagnostics-mapper");
const SUPPORTED_LANGUAGES = ["python", "javascript", "typescript"];
let diagnosticCollection;
let client;
let statusBarItem;
function activate(context) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection("hallucination-firewall");
    client = new validation_client_1.ValidationClient();
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(shield) Firewall";
    statusBarItem.show();
    context.subscriptions.push(diagnosticCollection, statusBarItem);
    // Register event listeners based on trigger mode
    registerListeners(context);
    // Listen for config changes to re-register listeners
    context.subscriptions.push(vscode.workspace.onDidChangeConfiguration((e) => {
        if (e.affectsConfiguration("hallucinationFirewall")) {
            registerListeners(context);
        }
    }));
    // Validate all open documents on activation
    for (const doc of vscode.workspace.textDocuments) {
        if (shouldValidate(doc)) {
            validateDocument(doc);
        }
    }
}
const disposables = [];
function registerListeners(context) {
    // Dispose previous listeners
    for (const d of disposables) {
        d.dispose();
    }
    disposables.length = 0;
    const triggerMode = vscode.workspace
        .getConfiguration("hallucinationFirewall")
        .get("triggerMode", "onSave");
    // Always validate on open
    disposables.push(vscode.workspace.onDidOpenTextDocument((doc) => {
        if (shouldValidate(doc)) {
            validateDocument(doc);
        }
    }));
    if (triggerMode === "onChange") {
        disposables.push(vscode.workspace.onDidChangeTextDocument((event) => {
            if (shouldValidate(event.document)) {
                client.debounce(() => validateDocument(event.document));
            }
        }));
    }
    else {
        // onSave mode (default)
        disposables.push(vscode.workspace.onDidSaveTextDocument((doc) => {
            if (shouldValidate(doc)) {
                validateDocument(doc);
            }
        }));
    }
    // Clear diagnostics on close
    disposables.push(vscode.workspace.onDidCloseTextDocument((doc) => {
        diagnosticCollection.delete(doc.uri);
    }));
    context.subscriptions.push(...disposables);
}
function shouldValidate(document) {
    const enabled = vscode.workspace
        .getConfiguration("hallucinationFirewall")
        .get("enabled", true);
    if (!enabled) {
        return false;
    }
    return SUPPORTED_LANGUAGES.includes(document.languageId);
}
async function validateDocument(document) {
    try {
        statusBarItem.text = "$(loading~spin) Validating...";
        const code = document.getText();
        const language = document.languageId;
        const result = await client.validateCode(code, language);
        const diagnostics = result.issues.map(diagnostics_mapper_1.mapIssueToDiagnostic);
        diagnosticCollection.set(document.uri, diagnostics);
        const errorCount = result.issues.filter((i) => i.severity === "error").length;
        statusBarItem.text =
            errorCount > 0
                ? `$(error) Firewall: ${errorCount} issue(s)`
                : "$(shield) Firewall: OK";
    }
    catch {
        diagnosticCollection.delete(document.uri);
        statusBarItem.text = "$(warning) Firewall: offline";
    }
}
function deactivate() {
    client?.dispose();
    diagnosticCollection?.dispose();
}
//# sourceMappingURL=extension.js.map