# API Error Codes

| Code | HTTP | Meaning |
| --- | --- | --- |
| `unauthorized` | 401 | Missing/invalid credentials |
| `forbidden` | 403 | Authenticated but not allowed |
| `consent_required` | 403 | Category disabled by consent policy |
| `not_found` | 404 | Resource missing in scope |
| `validation_failed` | 422 | Schema/envelope invalid |
| `idempotency_conflict` | 409 | Key reuse with different payload |
| `rate_limited` | 429 | Too many requests |
| `projection_lag` | 503 | Optional: query refused due to extreme lag (if configured) |
| `conflict_recorded` | 409 | Sync conflict registered |
| `internal_error` | 500 | Unexpected failure |

Clients should branch on `error.code`, not only HTTP status.
