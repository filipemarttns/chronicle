# TypeScript Package Strategy

## Workspace tool

**pnpm workspaces** at repository root.

## Packages / apps

| Path | Package name | Role |
| --- | --- | --- |
| `apps/web` | `@chronicle/web` | Next.js console |
| `apps/desktop` | `@chronicle/desktop` | Tauri + frontend shell |
| `extensions/vscode` | `@chronicle/vscode` | VS Code/Cursor extension |
| `extensions/browser` | `@chronicle/browser` | Browser extension |
| `packages/ts-client` | `@chronicle/client` | HTTP client for `/v1` |
| `packages/ui` | `@chronicle/ui` | Shared UI primitives (optional) |
| `packages/event-types` | `@chronicle/event-types` | Shared TS types for envelopes |

## Dependency rule

```text
extensions/* → @chronicle/client, @chronicle/event-types
apps/web → @chronicle/client, @chronicle/ui, @chronicle/event-types
apps/desktop → web UI packages as appropriate; still calls API as remote
@chronicle/client → must not depend on Next.js or VS Code APIs
```

## Codegen

Preferred pipeline once API exists:

1. Export OpenAPI from FastAPI
2. Generate `@chronicle/client` types
3. Keep hand-written helpers for idempotency and batching

Until codegen lands, `docs/design/api/openapi-v1.yaml` is the contract; `@chronicle/event-types` mirrors the event catalog manually.

## Testing

| Package | Tool |
| --- | --- |
| unit | Vitest |
| web e2e | Playwright |
| extension | VS Code test host / Vitest for pure logic |

## Versioning

Workspace packages use `0.0.0` private until publish. Extension marketplace versions follow [RELEASE.md](../../../RELEASE.md) when publishing.
