# Event Schema Conventions

## JSON Schema location (intended)

```
packages/schemas/events/
  envelope.schema.json
  editor.file.opened.v1.schema.json
  ...
packages/schemas/domain/
  domain.session.started.v1.schema.json
  ...
```

Python: generated or hand-written Pydantic models mirroring schemas.  
TypeScript: zod or types generated from JSON Schema for extensions.

## Envelope schema (normative fields)

| Field | Required | Type |
| --- | --- | --- |
| `event_id` | no (server may assign) | uuid |
| `type` | yes | string |
| `schema_version` | yes | integer ≥ 1 |
| `occurred_at` | yes | date-time |
| `source` | yes | string |
| `actor_id` | yes | uuid |
| `workspace_id` | yes | uuid |
| `device_id` | yes | uuid |
| `idempotency_key` | yes | string |
| `correlation_id` | no | string |
| `causation_id` | no | string |
| `payload` | yes | object |

Server adds: `received_at`, `store_offset`, `redaction_meta`.

## Canonicalization for fingerprints

1. Parse JSON
2. Remove non-payload envelope fields
3. Sort object keys recursively
4. UTF-8 JSON with separators `(',', ':')`
5. SHA-256 hex

Used for idempotency conflict detection.

## Validation pipeline order

1. Envelope structural validation
2. Consent category resolution
3. Redaction
4. Per-type payload schema validation
5. Persist
