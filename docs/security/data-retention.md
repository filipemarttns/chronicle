# Data Retention Policy

## Goals

1. Minimize sensitive data lifetime by default
2. Preserve enough history for Timeline Replay and historical debugging when operators opt in
3. Ensure deletion cascades across Events, projections, embeddings, and graph evidence

## Default retention classes

| Class | Examples | Default retention |
| --- | --- | --- |
| Raw high-volume telemetry | fine-grained selections, heartbeats | 30 days |
| Standard activity | file opens, commands, builds | 180 days |
| Durable VCS facts | commits, PR metadata | 365 days (or unbounded if operator sets) |
| Decisions / ADRs ingested | architecture decisions | unbounded until manual delete |
| AI interactions (opt-in) | prompts/responses | 90 days |
| Browser history (opt-in) | URLs | 90 days |
| Audit records | consent, export, purge, MCP | 365 days minimum |

Defaults are **starting points** for self-hosters and must be configurable per workspace.

## Deletion semantics

A purge job for scope `workspace_id` + time range or category:

1. Select target event ids
2. Delete dependent timeline items, chunks, embeddings, graph evidence/edges orphaned by policy
3. Append `system.retention.purged` summarizing counts (without re-storing purged payloads)
4. Record audit entry

Event bodies are removed; cryptographic proof of former content is not retained.

## Legal holds

Workspaces may set a legal hold flag that blocks automated purge. Hold state is audited.

## Operator checklist

- [ ] Confirm defaults at first run
- [ ] Test purge on a disposable workspace
- [ ] Verify backups expire on a schedule aligned with policy
- [ ] Document any compliance-driven deviations

## Backups vs retention

Retention in the primary database does not erase data in backups until those backups expire. Backup TTL must be documented alongside DB retention.
