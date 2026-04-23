# Naming Conventions

## General principles

1. Prefer domain language from the glossary (Event, Session, Timeline, Memory, Knowledge Graph, Workspace, Actor, Device).
2. Names reveal intent; abbreviations only when ubiquitous (`id`, `url`, `http`, `sql`).
3. Consistency within a package beats clever synonyms (`fetch` vs `get` — pick one per layer).

## Glossary enforcement

| Use | Avoid as synonyms in APIs/types |
| --- | --- |
| Event | log line, activity row, breadcrumb (unless UI copy) |
| Session | sprint, block (unless analytics label) |
| Ingest | upload, post (in domain code) |
| Projection | cache table (in domain docs) |
| Workspace | tenant (until multi-tenant product language is adopted) |

## Python

| Element | Convention | Example |
| --- | --- | --- |
| Packages/modules | `snake_case` | `session_clustering.py` |
| Classes | `PascalCase` | `SessionClusteringService` |
| Functions/methods | `snake_case` | `ingest_event` |
| Constants | `UPPER_SNAKE` | `DEFAULT_IDLE_TIMEOUT` |
| Type aliases | `PascalCase` | `EventPayload` |
| Abstract ports | `PascalCase` + `Port` suffix | `EventStorePort` |
| Exceptions | `PascalCase` + error suffix | `DomainValidationError` |
| Test files | `test_*.py` | `test_session.py` |
| Test names | `test_<behavior>` | `test_close_session_on_idle_gap` |

### Domain-specific suffixes

| Suffix | Meaning |
| --- | --- |
| `Command` | Application input |
| `Result` / `Response` | Application output |
| `Service` | Domain or application service |
| `Repository` | Persistence port/adapter |
| `Projector` | Read-model worker |
| `Aggregate` | Rarely needed in type name if class is the root (`Session`) |

## TypeScript / JavaScript

| Element | Convention | Example |
| --- | --- | --- |
| Files (components) | `PascalCase.tsx` | `TimelineReplay.tsx` |
| Files (utils) | `camelCase.ts` | `buildIdempotencyKey.ts` |
| Types/interfaces | `PascalCase` | `EventEnvelope` |
| Functions | `camelCase` | `ingestEvent` |
| Constants | `UPPER_SNAKE` or `camelCase` for config objects | `DEFAULT_LIMIT` |
| Hooks | `use*` | `useTimelineReplay` |
| Packages | `@chronicle/<name>` | `@chronicle/client` |

## HTTP API

| Element | Convention | Example |
| --- | --- | --- |
| Paths | plural nouns, kebab only if multi-word | `/v1/events`, `/v1/timelines/replay` |
| Path params | `snake_case` | `{event_id}` |
| Query params | `snake_case` | `workspace_id` |
| JSON fields | `snake_case` | `store_offset` |
| Headers | `X-Correlation-Id`, `Idempotency-Key` | standard casing |
| Error codes | `snake_case` | `idempotency_conflict` |

Batch actions use Google-style custom methods when needed: `/v1/events:batch`.

## Events

| Element | Convention | Example |
| --- | --- | --- |
| Telemetry type | `family.action` dot notation | `editor.file.opened` |
| Domain type | `domain.<context>.<verb_past>` | `domain.session.started` |
| Schema files | `<type>.v<N>.schema.json` | `editor.file.opened.v1.schema.json` |

## Database

| Element | Convention | Example |
| --- | --- | --- |
| Tables | `snake_case` plural | `events`, `timeline_items` |
| Columns | `snake_case` | `occurred_at` |
| PK | `id` or composite documented | `id` |
| FK | `<entity>_id` | `workspace_id` |
| Indexes | `ix_<table>_<cols>` | `ix_events_workspace_offset` |
| Unique | `uq_<table>_<cols>` | `uq_events_workspace_idempotency` |

## Metrics and logs

| Element | Convention | Example |
| --- | --- | --- |
| Metrics | `chronicle_<name>_<unit>` | `chronicle_search_latency_seconds` |
| Log fields | `snake_case` | `correlation_id` |
| Components | short stable ids | `api`, `worker.timeline`, `mcp` |

## Git refs

See [branching.md](branching.md) and [commits.md](commits.md).

## Files and directories

- Prefer directory names matching package intent (`session/`, not `misc/`).
- No placeholder names (`foo`, `temp`, `stuff`, `new2`).
- Docs use `kebab-case.md` except root ALLCAPS policy files.
