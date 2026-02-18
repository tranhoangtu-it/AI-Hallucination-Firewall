import * as vscode from "vscode";

export interface SourceLocation {
  file: string;
  line: number;
  column: number;
  end_line?: number;
  end_column?: number;
}

export interface ValidationIssue {
  severity: "error" | "warning" | "info";
  issue_type: string;
  location: SourceLocation;
  message: string;
  suggestion?: string;
  confidence: number;
}

export interface ValidationResult {
  file: string;
  language: string;
  issues: ValidationIssue[];
  passed: boolean;
}

export class ValidationClient {
  private debounceTimer?: ReturnType<typeof setTimeout>;
  private currentController?: AbortController;

  getEndpoint(): string {
    return vscode.workspace
      .getConfiguration("hallucinationFirewall")
      .get<string>("apiEndpoint", "http://localhost:8000");
  }

  getDebounceDelay(): number {
    return vscode.workspace
      .getConfiguration("hallucinationFirewall")
      .get<number>("debounceDelay", 500);
  }

  async validateCode(
    code: string,
    language: string
  ): Promise<ValidationResult> {
    // Cancel any in-flight request to prevent stale results
    this.currentController?.abort();
    const controller = new AbortController();
    this.currentController = controller;

    const url = `${this.getEndpoint()}/validate`;
    const body = JSON.stringify({ code, language });
    const timeout = setTimeout(() => controller.abort(), 5000);

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return (await response.json()) as ValidationResult;
    } finally {
      clearTimeout(timeout);
    }
  }

  debounce(handler: () => void): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    this.debounceTimer = setTimeout(handler, this.getDebounceDelay());
  }

  dispose(): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    this.currentController?.abort();
  }
}
