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
exports.ValidationClient = void 0;
const vscode = __importStar(require("vscode"));
class ValidationClient {
    getEndpoint() {
        return vscode.workspace
            .getConfiguration("hallucinationFirewall")
            .get("apiEndpoint", "http://localhost:8000");
    }
    getDebounceDelay() {
        return vscode.workspace
            .getConfiguration("hallucinationFirewall")
            .get("debounceDelay", 500);
    }
    async validateCode(code, language) {
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
            return (await response.json());
        }
        finally {
            clearTimeout(timeout);
        }
    }
    debounce(handler) {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        this.debounceTimer = setTimeout(handler, this.getDebounceDelay());
    }
    dispose() {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        this.currentController?.abort();
    }
}
exports.ValidationClient = ValidationClient;
//# sourceMappingURL=validation-client.js.map