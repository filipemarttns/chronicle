# Security Policy

Chronicle captures engineering activity that may include source paths, command lines, browser URLs, commit messages, stack traces, and—when enabled—AI assistant interactions. Security and privacy are therefore product requirements, not afterthoughts.

## Supported versions

Security fixes are applied according to the following policy:

| Version | Supported |
| --- | --- |
| Latest `main` (pre-release / development) | Yes — best effort |
| Latest published minor release (`x.y.*`) | Yes |
| Previous minor release | Critical severity only, for 90 days after the newer minor ships |
| Older releases | No |

Exact version numbers are published with GitHub Releases and annotated tags. See [RELEASE.md](RELEASE.md).

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

### Preferred reporting channel

Use [GitHub Security Advisories](https://github.com/filipemarttns/chronicle/security/advisories/new) (**Report a vulnerability** on the Security tab).

You may also email **filipemarttns@gmail.com** with the subject prefix `[Chronicle security]`.

Do not open a public GitHub issue for security vulnerabilities.

### What to include

Provide enough detail for maintainers to reproduce and assess impact:

1. Affected component (API, worker, extension, desktop, docs site, CI)
2. Chronicle version or commit SHA
3. Deployment mode (Docker Compose, local, hardened production)
4. Step-by-step reproduction
5. Observed impact (confidentiality, integrity, availability)
6. Proof of concept limited to the minimum necessary
7. Whether the issue is already publicly known
8. Your preferred credit name (or request to remain anonymous)

Encrypt sensitive attachments when possible. Maintainers will acknowledge receipt within **3 business days** and provide a status update within **10 business days**.

## Severity classification

Chronicle uses a pragmatic severity model aligned with common open-source practice:

| Severity | Examples |
| --- | --- |
| Critical | Remote code execution; authentication bypass; mass exposure of captured session data across tenants |
| High | Privilege escalation; unauthorized read of another user's events; secret leakage via logs or exports |
| Medium | CSRF on state-changing endpoints; overly permissive CORS in default configs; missing rate limits on ingest |
| Low | Hardening gaps; verbose errors leaking internal paths without direct exploitability |
| Informational | Defense-in-depth suggestions without a demonstrated vulnerability |

## Disclosure policy

1. Reporter submits privately.
2. Maintainers confirm, assess severity, and assign an owner.
3. A fix is developed on a private branch when necessary.
4. Coordinated release: patch versions are published; advisory is prepared.
5. Public disclosure follows once a fix is available, or after a mutually agreed window.
6. Credit is given to reporters who follow responsible disclosure, unless anonymity is requested.

We ask reporters not to publish exploit details until a fixed release is available, except where required by law or a prior agreement.

## Security design principles

Chronicle's security posture is driven by the nature of its data:

### Local-first and operator-controlled

- Default deployments keep event data on infrastructure the operator controls.
- Cloud sync, if enabled, must be explicit and documented.
- Exports are user-initiated and auditable.

### Consent-scoped capture

- Browser history and AI interaction capture are **opt-in**.
- Capture categories are independently toggled.
- Extensions must fail closed when authentication or consent is missing.

### Least privilege

- Ingest tokens are scoped to device/workspace where practical.
- Workers receive only the queue and datastore permissions they require.
- Database roles separate migration, application, and read-replica access in hardened deployments.

### Defense in depth

- Authenticated APIs by default for non-local development profiles.
- Idempotency keys on ingest to reduce replay abuse.
- Rate limiting on public-facing ingest endpoints.
- Structured audit logs for authentication, export, and retention changes.
- Secrets exclusively via environment or secret managers—never committed.

### Data minimization and retention

- Prefer hashes or redaction for high-risk fields (tokens in command lines, Authorization headers, raw cookies).
- Retention policies are configurable; defaults favor finite retention for raw high-volume streams.
- Deletion must cascade through event projections, embeddings, and graph nodes for the targeted scope.

Detailed threat models, retention policies, and deployment hardening guides belong under `docs/security/` as that documentation tree is published.

## Secrets and credential handling

If you accidentally commit a secret:

1. Rotate the credential immediately.
2. Notify maintainers via GitHub Security Advisories or filipemarttns@gmail.com.
3. Open a non-public report describing where it appeared and for how long.
4. Do not assume history rewrite alone is sufficient once a secret has been pushed.

## Supply chain

- Dependencies must be pinned according to the repository dependency policy.
- CI should verify lockfiles and run vulnerability scanning on release candidates.
- Signed releases and checksums are part of the release process described in [RELEASE.md](RELEASE.md).
- Review new dependencies for license compatibility, maintenance status, and permission surface—especially in extensions and desktop code.

## Safe research guidelines

Security research against Chronicle should:

- Use local or isolated deployments you control
- Avoid testing against third-party instances without written permission
- Avoid destructive actions on shared infrastructure
- Minimize collection of real user event data

## Bug bounty

Chronicle does not currently operate a paid bug bounty program. High-quality reports are acknowledged in release notes and advisory credits.

## Contact

| Topic | Contact |
| --- | --- |
| Vulnerability reports | GitHub Security Advisories / filipemarttns@gmail.com |
| Security process questions | filipemarttns@gmail.com |
| Code of Conduct | filipemarttns@gmail.com |
| Maintainer escalation | See [MAINTAINERS.md](MAINTAINERS.md) |

This policy may evolve as the project approaches stable releases. Material changes will be noted in release communications.
