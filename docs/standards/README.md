# Repository Standards

Normative engineering standards for Chronicle. These rules apply to all packages unless a document explicitly scopes an exception.

Related policies: [CONTRIBUTING.md](../../CONTRIBUTING.md), [RELEASE.md](../../RELEASE.md), [SECURITY.md](../../SECURITY.md), [GOVERNANCE.md](../../GOVERNANCE.md), ADRs under [`docs/adr/`](../adr/).

## Index

| Standard | Document |
| --- | --- |
| Naming conventions | [naming.md](naming.md) |
| Commit conventions | [commits.md](commits.md) |
| Branching strategy | [branching.md](branching.md) |
| Release strategy | [release.md](release.md) |
| Documentation standards | [documentation.md](documentation.md) |
| Security standards | [security.md](security.md) |
| Testing standards | [testing.md](testing.md) |
| Dependency policy | [dependencies.md](dependencies.md) |
| Observability standards | [observability.md](observability.md) |
| Logging standards | [logging.md](logging.md) |
| Error handling standards | [errors.md](errors.md) |
| Performance standards | [performance.md](performance.md) |

## Precedence

1. Accepted ADR for a scoped technical decision
2. This standards tree for day-to-day engineering practice
3. Root policy docs for community, security reporting, and release authority
4. Style implied by existing code in the same package

Conflicts must be resolved by updating the higher-precedence document—not by silent local exception.
