# Dependency Policy

## Principles

1. Prefer standard library and existing stack components
2. Every new dependency needs a justification in the PR
3. License must be compatible with MIT distribution of Chronicle
4. Prefer maintained packages with clear ownership and release practice
5. Pin versions via lockfiles

## Allowed license families (default)

MIT, BSD, Apache-2.0, ISC, and similarly permissive licenses. Copyleft dependencies require explicit maintainer approval and documentation of obligations.

## Prohibited by default

- Dependencies that phone home without documentation and operator consent
- Unmaintained packages with known unpatched critical CVEs
- Opaque binaries without reproducible build story in critical paths
- Duplicate libraries when an existing choice already covers the need (e.g., multiple HTTP clients without reason)

## Adding a dependency

PR must include:

1. Why existing stack is insufficient
2. Alternatives considered
3. License
4. Security/maintenance notes
5. Lockfile update
6. Scope of blast radius (API, extension, desktop)

## Upgrades

- Routine patch upgrades encouraged
- Major upgrades get dedicated PRs with release notes / breaking callouts
- Security upgrades may skip non-essential process but not tests

## Python / JS specifics

| Ecosystem | Expectation |
| --- | --- |
| Python | `pyproject.toml` + lock via uv/pip-tools as standardized |
| Node | `pnpm-lock.yaml` committed |
| Rust (Tauri) | `Cargo.lock` committed for apps |

## Review automation

CI should fail on known high/critical vulnerabilities for release branches. Waivers are time-bounded and recorded.
