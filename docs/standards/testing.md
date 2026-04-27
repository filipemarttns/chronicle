# Testing Standards

## Pyramid

| Layer | Tooling | Speed | Scope |
| --- | --- | --- | --- |
| Domain unit | Pytest | Fast | Invariants, VOs, clustering |
| Application | Pytest + fakes | Fast | Use-case orchestration |
| Adapter integration | Pytest + Compose deps | Medium | SQL, Redis, outbox |
| API contract | HTTPX / schemathesis (optional) | Medium | OpenAPI conformance |
| Web unit | Vitest | Fast | Components, client logic |
| E2E | Playwright | Slow | Critical operator flows |
| Extension | Vitest / host tests | Medium | Emission + consent |

## Mandatory coverage expectations

| Change | Minimum tests |
| --- | --- |
| Domain invariant | Unit tests for success + violation |
| Ingest/idempotency | Unit + integration |
| Projector | Idempotent apply + replay |
| API endpoint | Happy path + authz failure + validation failure |
| Redaction | Detector corpus cases |
| UI critical flow | Playwright when surface is user-facing |

Exact coverage percentages may be enforced per package in CI as the codebase matures; lack of a number is not permission to skip tests.

## Rules

1. No flaky tests — fix or quarantine with issue
2. Deterministic time via `ClockPort`
3. No network in unit tests
4. No real user data in fixtures
5. Parallel-safe tests (unique keys, no shared global mutable state)
6. Prefer AAA structure (Arrange/Act/Assert) and clear names

## Naming

```
test_<unit>_<condition>_<expected>
```

Example: `test_ingest_duplicate_key_same_payload_returns_existing`

## Performance tests

Benchmarks live under benchmark suites, not as flaky CI unit tests. See [performance.md](performance.md). Smoke benches may run on RC.

## PR checklist (testing)

- [ ] Added/updated tests match risk
- [ ] CI job list covers the touched languages
- [ ] Documented manual steps only when automation is impossible (with reason)
