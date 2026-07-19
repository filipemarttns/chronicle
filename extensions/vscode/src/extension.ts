import * as vscode from "vscode";
import * as crypto from "crypto";

interface ChronicleConfig {
  apiBaseUrl: string;
  token: string;
  captureEditor: boolean;
  workspaceId: string;
  actorId: string;
  deviceId: string;
}

function readConfig(): ChronicleConfig {
  const cfg = vscode.workspace.getConfiguration("chronicle");
  return {
    apiBaseUrl: cfg.get<string>("apiBaseUrl", "http://localhost:8000"),
    token: cfg.get<string>("token", ""),
    captureEditor: cfg.get<boolean>("capture.editor", false),
    workspaceId: cfg.get<string>("workspaceId", ""),
    actorId: cfg.get<string>("actorId", ""),
    deviceId: cfg.get<string>("deviceId", ""),
  };
}

function stableIdempotencyKey(parts: string[]): string {
  return crypto.createHash("sha256").update(parts.join("|")).digest("hex").slice(0, 32);
}

async function emitEvent(
  config: ChronicleConfig,
  type: string,
  payload: Record<string, unknown>,
  output: vscode.OutputChannel
): Promise<void> {
  if (!config.workspaceId || !config.actorId || !config.deviceId) {
    output.appendLine("Chronicle identity incomplete; set workspaceId/actorId/deviceId");
    return;
  }
  const body = {
    type,
    schema_version: 1,
    occurred_at: new Date().toISOString(),
    source: "vscode",
    actor_id: config.actorId,
    workspace_id: config.workspaceId,
    device_id: config.deviceId,
    idempotency_key: stableIdempotencyKey([
      type,
      config.deviceId,
      String(payload.path ?? ""),
      String(payload.occurred_bucket ?? Date.now()),
    ]),
    payload,
  };
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (config.token) {
    headers.Authorization = `Bearer ${config.token}`;
  }
  try {
    const res = await fetch(`${config.apiBaseUrl.replace(/\/$/, "")}/v1/events`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    output.appendLine(`emit ${type} -> ${res.status}`);
  } catch (err) {
    output.appendLine(`emit failed: ${String(err)}`);
  }
}

export function activate(context: vscode.ExtensionContext): void {
  const output = vscode.window.createOutputChannel("Chronicle");
  output.appendLine("Chronicle extension activated");

  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(async (document) => {
      if (document.uri.scheme !== "file") {
        return;
      }
      const config = readConfig();
      if (!config.captureEditor) {
        return;
      }
      await emitEvent(
        config,
        "editor.file.opened",
        {
          path: vscode.workspace.asRelativePath(document.uri),
          language: document.languageId,
          occurred_bucket: Math.floor(Date.now() / 1000),
        },
        output
      );
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
