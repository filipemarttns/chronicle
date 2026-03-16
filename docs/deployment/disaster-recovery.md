# Disaster Recovery

## Recovery objectives (reference)

| Objective | Single-site target |
| --- | --- |
| RPO | ≤ 15 minutes (frequent DB backups + WAL archiving recommended) |
| RTO | ≤ 2 hours for restore to last backup + catch-up |

Operators may set stricter objectives with continuous WAL shipping.

## What must be backed up

| Component | Required | Notes |
| --- | --- | --- |
| PostgreSQL data | Yes | Events + projections + vectors |
| Encryption keys / secrets | Yes | Separate from DB dumps |
| Redis | No | Ephemeral; rebuild from outbox/events |
| Object exports | Optional | Operator-generated |

## Backup practices

1. Encrypted backups at rest
2. Periodic restore drills on staging
3. Retain backup TTL consistent with [../security/data-retention.md](../security/data-retention.md)
4. Never rely solely on volume snapshots without Postgres-consistent methodology

## Failure scenarios

### Postgres primary loss

1. Promote replica if configured
2. Or restore from backup to new primary
3. Point API/workers at new DSN
4. Rebuild projections if restore is event-log-only or inconsistency detected
5. Verify ingest idempotency and lag metrics

### Redis loss

1. Restart Redis empty
2. Re-drive unpublished outbox rows
3. Expect temporary projection delay

### Poison event / projector bug

1. Pause affected queue
2. Quarantine event id
3. Patch projector
4. Resume from checkpoint
5. Rebuild if corruption suspected

### Accidental purge

1. Stop further purge jobs
2. Restore DB to point-in-time before purge if within backup window
3. Document gap if outside RPO

### Partial sync divergence

1. Inspect `ConflictRecord`s
2. Do not manually edit event payloads
3. Emit compensating events if domain requires correction
4. Rebuild projections after log convergence

## Forbidden recovery actions

- Deleting arbitrary rows from the event log without a documented purge job
- Editing `payload` in place
- Restoring Redis as source of truth

## Drill checklist

- [ ] Backup taken
- [ ] Restore to disposable environment
- [ ] `/ready` green
- [ ] Sample ingest
- [ ] Sample search
- [ ] Projection lag returns to SLO
