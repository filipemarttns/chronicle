# Capture Event Catalog

Normative telemetry types for producers. All use the standard envelope ([event-model.md](../../architecture/event-model.md), ADR-0009). Payloads below are `schema_version: 1` unless noted.

## Consent mapping

| Type prefix | Required consent category |
| --- | --- |
| `editor.*` | `editor` |
| `terminal.*` | `terminal` |
| `git.*` / `vcs.*` | `git` |
| `browser.*` | `browser` |
| `assistant.*` | `assistant` |
| `build.*` / `test.*` | `build` |
| `session.marker` | any enabled activity category or explicit |
| `system.*` / `domain.*` | server-produced; not client consent |

---

## editor.file.opened

```json
{
  "path": "apps/api/src/main.py",
  "language": "python",
  "workspace_folder": "/repo"
}
```

## editor.file.edited

```json
{
  "path": "apps/api/src/main.py",
  "language": "python",
  "change_kind": "insert|delete|replace",
  "range": { "start_line": 10, "end_line": 12 },
  "byte_delta": 42
}
```

Do not include full file contents by default.

## editor.selection.changed

```json
{
  "path": "apps/api/src/main.py",
  "start_line": 10,
  "end_line": 20
}
```

High-volume; subject to aggressive retention.

## editor.diagnostic.raised

```json
{
  "path": "apps/api/src/main.py",
  "severity": "error|warning|info",
  "code": "F401",
  "message": "unused import",
  "source": "ruff"
}
```

## terminal.command.executed

```json
{
  "shell": "powershell",
  "command": "pytest -q",
  "cwd": "C:\\repo",
  "exit_code": 0,
  "duration_ms": 1204
}
```

Command string is redacted before append.

## git.commit.created

```json
{
  "repo_root": "/repo",
  "commit_sha": "abc123",
  "branch": "feat/ingest",
  "message_subject": "feat(ingest): add batch endpoint",
  "authored_at": "2026-03-12T14:00:00Z",
  "files_changed": 3
}
```

## git.branch.checked_out

```json
{
  "repo_root": "/repo",
  "branch": "main",
  "commit_sha": "def456"
}
```

## vcs.pull_request.opened

```json
{
  "host": "github.com",
  "repo": "chronicle-dev/chronicle",
  "number": 128,
  "title": "Add ingest batch API",
  "url": "https://github.com/chronicle-dev/chronicle/pull/128"
}
```

## vcs.pull_request.reviewed

```json
{
  "host": "github.com",
  "repo": "chronicle-dev/chronicle",
  "number": 128,
  "state": "approved|changes_requested|commented",
  "reviewer": "octocat"
}
```

## browser.page.visited

```json
{
  "url": "https://docs.python.org/3/library/asyncio.html",
  "title": "asyncio — Asynchronous I/O",
  "transition": "link|typed|reload"
}
```

Opt-in only. Credentials in URLs redacted.

## build.started / build.failed / build.succeeded

```json
{
  "system": "github-actions|local|pytest",
  "name": "ci",
  "url": "https://...",
  "duration_ms": 88000,
  "error_summary": "optional on failure"
}
```

## test.run.finished

```json
{
  "runner": "pytest",
  "passed": 120,
  "failed": 1,
  "skipped": 3,
  "duration_ms": 5400,
  "failed_nodeids": ["tests/api/test_ingest.py::test_conflict"]
}
```

## assistant.interaction.recorded

```json
{
  "provider": "cursor|copilot|other",
  "interaction_id": "local-stable-id",
  "started_at": "2026-03-12T14:10:00Z",
  "ended_at": "2026-03-12T14:12:00Z",
  "prompt_chars": 1200,
  "response_chars": 3400,
  "truncated": false
}
```

Default stores **metadata only**. `truncated: true` requires explicit additional consent flag `assistant.full_text` (future settings key); otherwise omit bodies.

## session.marker

```json
{
  "action": "start|end",
  "label": "optional human label"
}
```

## stacktrace.captured

```json
{
  "language": "python",
  "summary": "KeyError: 'workspace_id'",
  "frames": [
    { "file": "apps/api/src/ingest.py", "line": 88, "function": "ingest" }
  ]
}
```

Maps to consent `build` or `editor` depending on source; producers set `source` accordingly. Category enforcement uses producer declaration + server policy table.

## file.changed (filesystem watcher / desktop)

```json
{
  "path": "packages/domain/src/session.py",
  "change": "created|modified|deleted|renamed",
  "renamed_from": null
}
```

---

## Versioning rules for payloads

1. Add optional fields freely within same `schema_version` if consumers ignore unknowns.
2. Rename/remove/change meaning → bump `schema_version`.
3. Producers advertise supported versions; server accepts N and N-1 during transition windows.
