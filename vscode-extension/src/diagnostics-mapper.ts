import * as vscode from "vscode";
import type { ValidationIssue } from "./validation-client";

export function mapIssueToDiagnostic(
  issue: ValidationIssue
): vscode.Diagnostic {
  const line = Math.max(0, issue.location.line - 1);
  const column = issue.location.column;
  const endLine = issue.location.end_line
    ? issue.location.end_line - 1
    : line;
  const endColumn = issue.location.end_column ?? column + 10;

  const range = new vscode.Range(
    new vscode.Position(line, column),
    new vscode.Position(endLine, endColumn)
  );

  const severity = mapSeverity(issue.severity);
  const message = issue.suggestion
    ? `${issue.message}\nSuggestion: ${issue.suggestion}`
    : issue.message;

  const diagnostic = new vscode.Diagnostic(range, message, severity);
  diagnostic.source = "hallucination-firewall";
  diagnostic.code = issue.issue_type;

  return diagnostic;
}

function mapSeverity(severity: string): vscode.DiagnosticSeverity {
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
