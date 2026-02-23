# ADR-0016: API Versioning Strategy

- Status: Accepted
- Date: 2026-02-18
- Deciders: Lead Maintainer
- Tags: api, compatibility

## Context

Extensions, desktop, and MCP clients will ship on independent cadences. Breaking the HTTP contract without a clear policy forces silent failures in the field.

## Decision

- Public HTTP APIs are prefixed with a major version: `/v1/...`.
- Additive, backward-compatible changes stay in the current major.
- Breaking changes require `/v2` (or higher) and a documented deprecation window for the previous major once Chronicle is past `1.0.0`.
- During `0.x`, breaking changes may occur in minor releases but must be called out in release notes with migration steps ([RELEASE.md](../../RELEASE.md)).
- Event schema versioning is independent of HTTP major version (ADR-0009) but coordinated in release communications when both move.

Error response shape remains stable within a major version.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Header-only versioning | Easy to misconfigure in extensions; poorer discoverability |
| Date-based versions | Unusual for self-hosted ops mental model |
| No versioning until 1.0 | Encourages irreversible coupling |

## Consequences

- OpenAPI files published per major.
- CI contract tests against committed OpenAPI snapshots.
- Dual-running majors possible for a transition window in future.

## References

- [api/versioning.md](../api/versioning.md)
- ADR-0007
