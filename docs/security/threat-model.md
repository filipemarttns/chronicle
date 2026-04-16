# Threat Model

Threat modeling for Chronicle follows a STRIDE-oriented review of trust boundaries. This document is living; update when capture surfaces, sync, or MCP expand.

## Assets

| Asset | Sensitivity |
| --- | --- |
| Event log (commands, paths, stacks) | High |
| Browser URLs and titles | High |
| AI interaction contents | Critical |
| Embeddings derived from above | High |
| API tokens / device credentials | Critical |
| Backups of Postgres | Critical |
| Audit logs | Medium–High |

## Trust boundaries

1. Capture client ↔ API
2. API ↔ PostgreSQL / Redis
3. Worker ↔ embed model runtime
4. MCP client ↔ MCP server ↔ API
5. Sync peer ↔ sync peer
6. Operator admin actions ↔ data plane

## STRIDE summary

| Threat | Example | Mitigations |
| --- | --- | --- |
| Spoofing | Stolen extension token | Short-lived tokens, device binding, rotation, TLS |
| Tampering | Modified event batch in transit | TLS, auth, payload integrity on sync |
| Repudiation | Denied export of data | Audit events for export/purge/consent |
| Information disclosure | MCP dumps secrets to cloud model | Redaction, scoped tools, consent, docs on residual risk |
| Denial of service | Event flood | Rate limits, body size caps, backpressure metrics |
| Elevation of privilege | Cross-workspace read | Workspace authz on every query path |

## Abuse cases

1. **Silent surveillance pack** — employer enables all categories without user visibility → require visible consent state in clients; reject product features that hide capture.
2. **Token in shell history** — user exports timeline → redaction at ingest + export-time scrub.
3. **Malicious MCP client** — over-query → rate limit tools; audit; allowlist tools.
4. **Backup theft** — encrypt backups; restrict storage IAM.
5. **Poison projector event** — crash workers → quarantine + DLQ pattern.

## Security control baseline

- AuthN required outside explicit local-dev profile
- Consent gates (ADR-0012)
- Redaction (ADR-0021)
- Least-privilege DB roles in hardened deploy
- Dependency scanning on release candidates
- No secrets in git

## Residual risks

- Redaction cannot catch all secret formats
- Local operators with DB access see stored data
- Embeddings may leak information via inversion research on some models
- Compromised developer machine compromises capture clients

Operators must accept residual risk when enabling browser/AI categories and MCP forwarding to external models.

Related: [data-retention.md](data-retention.md), [redaction.md](redaction.md), [../../SECURITY.md](../../SECURITY.md).
