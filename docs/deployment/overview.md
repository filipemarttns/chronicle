# Deployment Overview

Chronicle’s reference deployment is Docker Compose on operator-controlled infrastructure (ADR-0013). This directory covers scaling, capacity, disaster recovery, and observability.

## Profiles

| Profile | Use |
| --- | --- |
| `local` | Developer laptop; single node Compose |
| `single-site` | Team self-host; TLS proxy, backups, multiple workers |
| `hardened` | Replica reads, restricted DB roles, encrypted backups, audit sinks |

## Minimum services

- `api`
- `worker`
- `postgres` (with pgvector)
- `redis`
- `web` (optional if API-only)

Scheduler recommended for retention and backfill.

## Configuration

Twelve-factor env vars; see [../../DEVELOPMENT.md](../../DEVELOPMENT.md). Production must disable dev auth.

## Upgrade procedure (summary)

1. Take backup
2. Read release migration notes
3. Drain workers or pause consumers if required
4. Migrate Postgres
5. Deploy API/workers
6. Verify `/ready` and projection lag
7. Smoke ingest + search

Details in [disaster-recovery.md](disaster-recovery.md) and [../../RELEASE.md](../../RELEASE.md).
