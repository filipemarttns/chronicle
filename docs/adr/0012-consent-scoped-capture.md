# ADR-0012: Consent-Scoped Capture

- Status: Accepted
- Date: 2026-02-05
- Deciders: Lead Maintainer
- Tags: security, privacy, capture

## Context

Chronicle can observe editors, terminals, browsers, and AI assistants. Without explicit consent boundaries, the project would be indistinguishable from surveillance tooling and would violate its non-goals.

## Decision

Capture is **category-scoped and consent-gated**:

| Category | Default |
| --- | --- |
| Editor activity | Off until enabled in onboarding |
| Terminal commands | Off until enabled |
| Git metadata | Off until enabled |
| Browser history | **Opt-in**, separate toggle |
| AI assistant interactions | **Opt-in**, separate toggle |
| Build/test signals | Off until enabled |

Clients must not emit events for disabled categories. The API may additionally reject disallowed categories when workspace policy is enforced server-side.

Consent grants and revocations are themselves recorded as domain events for auditability.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Capture everything by default | Violates privacy posture and trust |
| Server-only filtering without client gates | Wastes bandwidth; still risks local buffering of sensitive data |
| Employer-only master switch without user control | Conflicts with developer-agency non-goal |

## Consequences

- UX complexity in extensions and desktop.
- Incomplete timelines are expected when categories are off—document this.
- Compliance stories become clearer for self-hosters.

## References

- [security/threat-model.md](../security/threat-model.md)
- [security/data-retention.md](../security/data-retention.md)
