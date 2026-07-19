# Chronicle Desktop

Tauri control plane for local Chronicle operation (ADR-0022).

## Scope (0.1)

- Launch/link against a local API (`http://localhost:8000`)
- Surface consent and capture status
- Open timeline/search in the embedded webview (reuses `@chronicle/web` panels later)

## Development

```bash
# requires Rust + Tauri prerequisites
pnpm --filter @chronicle/desktop install
pnpm --filter @chronicle/desktop tauri dev
```

The shell treats the API as a remote boundary even on localhost so auth and sync assumptions stay honest.
