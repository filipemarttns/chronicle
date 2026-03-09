# Event Model

Canonical event envelope and representative telemetry types.

## Envelope

See ADR-0009. Minimum required fields for persist:

```json
{
  "event_id": "018f...",
  "type": "editor.file.opened",
  "schema_version": 1,
  "occurred_at": "2026-03-12T14:22:01.120Z",
  "source": "vscode",
  "actor_id": "act_...",
  "workspace_id": "ws_...",
  "device_id": "dev_...",
  "idempotency_key": "vscode:bufopen:...",
  "correlation_id": "corr_...",
  "payload": {
    "path": "apps/api/src/main.py",
    "language": "python"
  }
}
```

Server sets `received_at` and `store_offset`.

## Telemetry type families

| Prefix | Examples |
| --- | --- |
| `editor.` | `file.opened`, `file.edited`, `selection.changed`, `diagnostic.raised` |
| `terminal.` | `command.executed` |
| `git.` | `commit.created`, `branch.checked_out` |
| `vcs.` | `pull_request.opened`, `pull_request.reviewed` |
| `browser.` | `page.visited` |
| `build.` | `started`, `failed`, `succeeded` |
| `test.` | `run.finished` |
| `assistant.` | `interaction.recorded` |
| `session.` | `marker` |
| `consent.` | `granted`, `revoked` |
| `system.` | `retention.purged` |

## Domain events vs telemetry

Telemetry events are facts from capture surfaces. Domain events express aggregate transitions (`SessionStarted`). Projectors may emit domain events into the log or maintain them as internal records—implementation must keep rebuild semantics clear and documented in code.

## Compatibility testing

CI should:

1. Validate sample fixtures against JSON Schema / Pydantic models
2. Ensure projectors accept `schema_version - 1` for supported windows
3. Reject malformed envelopes before append
