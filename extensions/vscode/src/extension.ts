import * as vscode from "vscode";

interface ChronicleConfig {
  apiBaseUrl: string;
  token: string;
  captureEditor: boolean;
}

function readConfig(): ChronicleConfig {
  const cfg = vscode.workspace.getConfiguration("chronicle");
  return {
    apiBaseUrl: cfg.get<string>("apiBaseUrl", "http://localhost:8000"),
    token: cfg.get<string>("token", ""),
    captureEditor: cfg.get<boolean>("capture.editor", false),
  };
}

export function activate(context: vscode.ExtensionContext): void {
  const output = vscode.window.createOutputChannel("Chronicle");
  output.appendLine("Chronicle extension activated");

  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(async (document) => {
      const config = readConfig();
      if (!config.captureEditor) {
        return;
      }
      output.appendLine(`editor.file.opened candidate: ${document.uri.fsPath}`);
      // Emission lands through the shared HTTP client once wired to workspace identity.
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("chronicle.showStatus", () => {
      const config = readConfig();
      vscode.window.showInformationMessage(
        `Chronicle API: ${config.apiBaseUrl} (editor capture ${config.captureEditor ? "on" : "off"})`
      );
    })
  );
}

export function deactivate(): void {
  // no-op
}
