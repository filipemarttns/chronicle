# Governance

Chronicle is an open-source project stewarded for long-term maintainability, technical coherence, and trustworthiness—especially given that it processes sensitive engineering activity data.

This document defines how decisions are made, who may make them, and how conflicts are resolved.

## Mission

Build and maintain a **Developer Memory Engine** that records engineering activity and transforms it into a searchable, replayable knowledge graph—local-first, consent-respecting, and operable by individuals and teams.

## Values

1. **Correctness over spectacle** — Prefer boring, inspectable designs for the event log and projections.
2. **Privacy as a feature** — Capture is explicit; defaults favor operator control.
3. **Architectural honesty** — Public docs match running systems; ADRs record real trade-offs.
4. **Contributor respect** — Clear standards, timely review, and no surprise rewrites of accepted work without discussion.
5. **Operational realism** — Releases are runnable, observable, and recoverable.

## Roles

### Users / Operators

Anyone running Chronicle. Operators are the authority over their event data.

### Contributors

Anyone submitting issues, discussions, documentation, tests, or code under the [MIT License](LICENSE) and [Code of Conduct](CODE_OF_CONDUCT.md).

### Reviewers

Trusted contributors invited to review pull requests in specific areas. Reviewers do not merge unilaterally unless also maintainers.

### Maintainers

Individuals listed in [MAINTAINERS.md](MAINTAINERS.md) with merge rights and area ownership. Maintainers are responsible for quality, security response, and roadmap integrity in their domains.

### Lead Maintainer

The Lead Maintainer coordinates cross-cutting decisions, release authority, and escalation. The current Lead Maintainer is **Filipe Martins**.

### Steering (future)

If the maintainer group grows beyond a size where informal coordination fails, a small Steering group may be established by maintainer vote. Until then, the Lead Maintainer plus area maintainers constitute project leadership.

## Decision types

| Decision | Examples | Authority |
| --- | --- | --- |
| Routine | Typo fixes, test hardening, dependency patches within policy | Any maintainer for the area |
| Feature | New API endpoint aligned with roadmap | Area maintainer after review |
| Architecture | Event envelope change, new bounded context, storage engine | ADR + maintainer consensus |
| Security | Vulnerability severity, embargo, advisory text | Security-capable maintainers; Lead Maintainer escalation |
| Governance | Changes to this document, Code of Conduct enforcement | Lead Maintainer with maintainer majority |
| License / trademark | Relicensing, name use | Lead Maintainer; requires explicit recorded agreement |

## Architecture Decision Records

Material technical decisions are captured as ADRs under `docs/adr/` (published as that tree lands).

An ADR is required when a change:

- Alters event schema semantics or versioning rules
- Introduces or removes a bounded context
- Changes persistence technology or consistency guarantees
- Modifies trust boundaries, authn/authz, or retention defaults
- Affects public API compatibility commitments
- Selects a significant dependency with long-term lock-in

ADRs should include context, decision, alternatives, and consequences. Accepted ADRs are not silently rewritten; superseding ADRs reference prior ones.

## Consensus model

Chronicle uses **lazy consensus** for most work:

1. A proposal is posted (issue, discussion, or PR).
2. Affected maintainers are nominated via CODEOWNERS or MAINTAINERS.
3. Silence after a reasonable review window is not automatic approval for architectural or security changes.
4. For architectural and governance changes, explicit approval from a majority of active maintainers is required, including the Lead Maintainer when cross-cutting.

### Conflict resolution

1. Prefer technical evidence: benchmarks, threat analysis, compatibility impact.
2. Area maintainers decide within their ownership when impact is local.
3. Cross-area disputes escalate to the Lead Maintainer.
4. If trust breaks down, governance changes or maintainer removal follow the process below.

## Becoming a maintainer

Candidates typically demonstrate:

- Sustained, high-quality contributions
- Sound judgment on privacy and security trade-offs
- Reliable review participation
- Alignment with project values and roadmap

Nomination:

1. An existing maintainer nominates the candidate in a private maintainer channel or email.
2. Active maintainers vote (majority required).
3. [MAINTAINERS.md](MAINTAINERS.md) is updated in a PR.
4. Access rights are granted (merge, security advisories as appropriate).

## Maintainer emeritus and removal

Maintainers may step down at any time and move to emeritus status.

Maintainers may be removed for:

- Sustained inactivity without handoff (typically 6+ months)
- Breach of the Code of Conduct
- Negligent or malicious handling of security or user data
- Repeated violation of governance or licensing obligations

Removal requires Lead Maintainer action plus majority approval of remaining active maintainers, except in emergency security lockouts, which may be temporary and then ratified.

## Release authority

Releases follow [RELEASE.md](RELEASE.md). Cutting a release requires:

- A maintainer with release permissions
- Passing CI on the release commit
- Documented changelog
- Security issue check (no known unfixed criticals intended for disclosure)

Emergency security releases may skip non-essential process steps but must not skip verification of the fix.

## Communication

| Channel | Purpose |
| --- | --- |
| GitHub Issues | Defects and concrete work items |
| GitHub Discussions | Proposals and design dialogue |
| Pull requests | Change review |
| security@chronicle.dev | Vulnerabilities |
| conduct@chronicle.dev | Code of Conduct reports |

Private maintainer communication is reserved for security, conduct, and personnel matters—not for hiding ordinary technical decisions.

## Changes to governance

Amendments to this document require:

1. A pull request describing motivation and impact
2. Discussion period of at least 7 days for non-urgent changes
3. Approval by the Lead Maintainer and a majority of active maintainers

Urgent amendments related to security or legal compliance may be applied immediately and ratified afterward.

## Relationship to corporate entities

Chronicle is stewarded as an open-source project. If corporate sponsorship, foundations, or trademarks become relevant, agreements must be documented publicly and must not silently override this governance without an amendment.
