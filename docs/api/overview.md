# API Overview

Chronicle exposes a versioned HTTP JSON API as the primary integration boundary for capture clients, the web console, desktop shell, and (optionally) the MCP server.

OpenAPI is generated from FastAPI and treated as a reviewable contract. Until implementation lands, this document defines the **intended** surface.

## Base URL

```
http://localhost:8000/v1
```

Production deployments terminate TLS at a reverse proxy.

## Authentication

| Mode | Usage |
| --- | --- |
| `Authorization: Bearer <token>` | Default for clients |
| Dev mode | Local unauthenticated profile — never for production |

Tokens are workspace-scoped when possible. Device credentials preferred for extensions.

## Core resources

| Resource | Methods | Notes |
| --- | --- | --- |
| `/events` | `POST`, `POST :batch`, `GET /{id}` | Idempotent ingest |
| `/sessions` | `GET`, `GET /{id}` | Session summaries |
| `/timelines/replay` | `GET` | Cursor pagination |
| `/search` | `POST` | Semantic + filters |
| `/graph/nodes/{id}/neighbors` | `GET` | Depth-limited |
| `/analytics/summary` | `GET` | Metric windows |
| `/sync/push` `/sync/pull` | `POST` | Multi-device |
| `/consent` | `GET`, `PUT` | Category toggles |
| `/health` `/ready` | `GET` | Probes (may be unversioned) |

## Error model

```json
{
  "error": {
    "code": "idempotency_conflict",
    "message": "Idempotency key reused with different payload",
    "details": {},
    "correlation_id": "corr_..."
  }
}
```

Stable `code` values within a major version. See [errors.md](errors.md).

## Pagination

Cursor-based pagination for timelines and event listings. Do not use offset pagination for the event log at scale.

## Idempotency

See ADR-0010. Clients must send `Idempotency-Key` header or body field as specified by OpenAPI.

## Rate limiting

Ingest endpoints are rate-limited per token/device. `429` responses include `Retry-After` when possible.

Cursor pagination is mandatory for timeline replay at scale.

