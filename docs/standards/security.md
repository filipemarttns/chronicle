# Security Standards

Companion to [SECURITY.md](../../SECURITY.md) and [docs/security/](../security/).

## Secure development requirements

1. No secrets in git (tokens, private keys, `.env` with credentials)
2. AuthZ checks on every query and ingest path (workspace scope)
3. Consent enforced server-side for restricted categories
4. Redaction before event append (ADR-0021)
5. MCP and export paths redact again before egress
6. Dependency changes follow [dependencies.md](dependencies.md)
7. Security-sensitive PRs require maintainer review from the security area

## Threat-aware design checklist (PR)

- [ ] New trust boundary documented?
- [ ] New data class covered by retention?
- [ ] Logs free of raw secrets?
- [ ] Rate limits considered for new public endpoints?
- [ ] Least privilege for new DB access?

## Cryptography and tokens

- Use established libraries only; no custom crypto
- Store credential hashes, not plaintext tokens
- Prefer short-lived tokens where practical
- TLS terminated at proxy in hardened deployments

## Capture privacy

- Browser and assistant categories default off
- Clients fail closed without consent/auth
- Fixtures synthetic; never commit real timelines

## Vulnerability handling

Report via GitHub Security Advisories or filipemarttns@gmail.com — not public issues. Embargo and disclosure follow SECURITY.md.

## CI expectations

Release candidates run dependency vulnerability scans. High/critical findings block release unless waived with written rationale in the release PR.
