# Clients and Capture Surfaces

## Editor extension (VS Code / Cursor)

Responsibilities:

- Respect consent toggles
- Emit editor, diagnostic, and optional terminal events
- Buffer offline with bounded disk usage
- Authenticate to API with device-scoped credentials

Non-responsibilities:

- Writing projections
- Performing semantic search locally as source of truth

## Browser extension

- Disabled until opt-in
- Captures navigations related to research; excludes chrome-internal pages
- Scrubs query tokens known to be credentials before send
- Per-profile enablement recommended

## Web console

- Timeline replay, search, graph exploration, analytics
- Workspace administration and consent audit views
- Never embeds DB credentials

## Desktop (Tauri)

- Control plane: start/stop local stack hints, consent, notifications
- Reuses web panels where practical
- Secure storage for tokens

## MCP server

- Narrow tools; redaction mandatory
- Audit every invocation

See ADR-0012, ADR-0017, ADR-0022.
