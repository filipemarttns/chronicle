# Error Handling Standards

## Layering

| Layer | Error style |
| --- | --- |
| Domain | Typed domain errors (`DomainValidationError`, `InvariantViolation`, `ConsentDenied`) |
| Application | Map domain errors; add use-case context; no HTTP types |
| Adapters / HTTP | Map to stable API error codes and HTTP statuses |
| Workers | Retryable vs fatal classification; poison quarantine |

## Domain error rules

1. Never use bare `Exception` for expected business violations
2. Messages are for operators/developers; do not leak secrets
3. Errors are part of the domain vocabulary where they express rules

## HTTP mapping

Align with [docs/api/errors.md](../api/errors.md):

| Domain / app condition | `error.code` | HTTP |
| --- | --- | --- |
| Missing/invalid auth | `unauthorized` | 401 |
| AuthZ failure | `forbidden` | 403 |
| Consent blocked | `consent_required` | 403 |
| Missing entity | `not_found` | 404 |
| Idempotency payload mismatch | `idempotency_conflict` | 409 |
| Schema invalid | `validation_failed` | 422 |
| Rate limit | `rate_limited` | 429 |
| Unexpected | `internal_error` | 500 |

Unknown error codes must be tolerated by clients; producers add codes additively within a major.

## Response shape

```json
{
  "error": {
    "code": "validation_failed",
    "message": "schema_version must be >= 1",
    "details": { "field": "schema_version" },
    "correlation_id": "corr_..."
  }
}
```

## Worker errors

| Class | Action |
| --- | --- |
| Transient (DB lock, Redis blip) | Retry with backoff + jitter |
| Deterministic poison | Quarantine; alert; do not infinite retry |
| Partial batch | Record per-item failure; continue when safe |

## Client guidance (extensions)

- Retry idempotent ingest with same key
- Surface `consent_required` as UX to enable category
- Never retry `validation_failed` without modifying payload

## Testing

Each new public error code needs at least one test asserting code + status.
