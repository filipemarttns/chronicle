# Documentation Standards

## Languages and tone

- Professional technical English for all project docs
- Precise, calm, non-marketing prose
- No emoji in repository documentation
- No placeholder copy (`TBD`, `lorem`, `coming soon` without issue link)
- Never claim AI authorship or generation

## Document types

| Type | Location | Rules |
| --- | --- | --- |
| Root policies | `/*.md` | Stable URLs; link heavily |
| Architecture | `docs/architecture/` | Align with ARCHITECTURE.md |
| ADRs | `docs/adr/` | Never silently rewrite accepted ADRs |
| Design contracts | `docs/design/` | Update in same PR as contract changes |
| Standards | `docs/standards/` | Normative engineering practice |
| Diagrams | `docs/diagrams/` | Mermaid preferred |

## Structure

1. Title + one-paragraph purpose
2. Normative sections before examples
3. Cross-links to ADRs and glossary terms
4. Explicit non-goals when ambiguity is likely

## Diagrams

- Mermaid in Markdown for reviewability
- Every diagram has a short narrative
- Keep labels consistent with glossary

## Code samples

- Synthetic data only
- Compilable or clearly marked as illustrative
- Include required headers (auth) when showing HTTP

## Change discipline

| Code change | Docs required |
| --- | --- |
| New endpoint | OpenAPI + api overview if resource-level |
| New event type | Event catalog + schema |
| Invariant change | ADR and/or design aggregate doc |
| New env var | DEVELOPMENT.md / deployment docs |
| Behavior fix user-visible | Changelog on release |

## Review bar

Documentation PRs are first-class. Reviewers check accuracy, links, glossary consistency, and whether the doc could mislead operators about privacy/consent.
