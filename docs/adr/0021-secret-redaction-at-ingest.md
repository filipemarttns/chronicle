# ADR-0021: Secret Redaction at Ingest

- Status: Accepted
- Date: 2026-03-06
- Deciders: Lead Maintainer
- Tags: security, privacy, ingest

## Context

Terminal commands, URLs, headers, and stack traces frequently contain tokens and passwords. Storing them raw in the event log creates a high-value secret repository.

## Decision

Apply **redaction at ingest** (API boundary) before append:

1. Run detectors for common secret patterns (API keys, bearer tokens, private key blocks, password flags, `Authorization` headers).
2. Replace matches with stable placeholders (e.g., `[REDACTED:jwt]`).
3. Record redaction counts in event metadata for debugging false positives.
4. Prefer failing closed on known high-risk headers in browser/AI payloads.

Redaction is not a guarantee of perfect secret removal; clients should still avoid emitting secrets. Defense in depth remains required.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Redact only at query time | Secrets still persist on disk/backups |
| Encrypt payload only | Operators with DB access still see secrets; key management complexity |
| No redaction, document risk | Unacceptable default for a memory engine |

## Consequences

- False positives may obscure benign strings—allow workspace-level detector tuning later.
- Historical events ingested before detector upgrades are not retroactively scrubbed unless a purge/re-ingest tool is run.
- Tests must cover detector regressions.

## References

- ADR-0012, ADR-0017
- [security/redaction.md](../security/redaction.md)
