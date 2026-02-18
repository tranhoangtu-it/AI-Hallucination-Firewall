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
exports.mapIssueToDiagnostic = mapIssueToDiagnostic;
const vscode = __importStar(require("vscode"));
function mapIssueToDiagnostic(issue) {
    const line = Math.max(0, issue.location.line - 1);
    const column = issue.location.column;
    const endLine = issue.location.end_line
        ? issue.location.end_line - 1
        : line;
    const endColumn = issue.location.end_column ?? column + 10;
    const range = new vscode.Range(new vscode.Position(line, column), new vscode.Position(endLine, endColumn));
    const severity = mapSeverity(issue.severity);
    const message = issue.suggestion
        ? `${issue.message}\nSuggestion: ${issue.suggestion}`
        : issue.message;
    const diagnostic = new vscode.Diagnostic(range, message, severity);
    diagnostic.source = "hallucination-firewall";
    diagnostic.code = issue.issue_type;
    return diagnostic;
}
function mapSeverity(severity) {
    switch (severity) {
        case "error":
            return vscode.DiagnosticSeverity.Error;
        case "warning":
            return vscode.DiagnosticSeverity.Warning;
        case "info":
            return vscode.DiagnosticSeverity.Information;
        default:
            return vscode.DiagnosticSeverity.Hint;
    }
}
//# sourceMappingURL=diagnostics-mapper.js.map