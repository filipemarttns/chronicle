# ADR-0013: Local-First Deployment Default

- Status: Accepted
- Date: 2026-02-05
- Deciders: Lead Maintainer
- Tags: deployment, privacy

## Context

Engineering memory is sensitive. A cloud-default product would force a trust decision before users see value and would complicate early open-source adoption.

## Decision

Chronicle’s **default deployment is local-first / self-hosted** via Docker Compose on operator-controlled infrastructure. Cloud sync and remote embedding providers are optional, explicit, and documented.

Distribution prioritizes:

1. Compose reference stack
2. Desktop control plane talking to a local API
3. Optional remote sync only after identity and encryption choices are configured

## Alternatives Considered

| Alternative | Why rejected as default |
| --- | --- |
| Hosted multi-tenant SaaS first | Privacy and tenancy complexity before core engine maturity |
| Desktop-only embedded DB with no API | Blocks extensions and MCP sharing the same memory |
| Peer-to-peer only | Harder reliability and backup story for v1 |

## Consequences

- Marketing and docs emphasize operator ownership of data.
- Multi-tenant hardening is a later milestone, not a day-one requirement.
- Benchmarks include single-node profiles first.

## References

- ADR-0018
- [deployment/overview.md](../deployment/overview.md)
