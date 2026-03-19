# Scaling

## Scale dimensions

| Dimension | Scale by |
| --- | --- |
| Ingest QPS | More API replicas; batch ingest; Postgres write capacity |
| Projection lag | More Celery workers; split queues (timeline vs embed) |
| Search QPS | Postgres replicas; tune HNSW; cache frequent queries |
| Embedding throughput | Dedicated embed workers; GPU hosts; batch size |
| Storage growth | Retention; partition events; cold storage tiering later |
| Sync fanout | Paginate; rate limit; separate sync workers |

## Horizontal patterns

```text
                 ┌─ api ─┐
clients ─ LB ─├─ api ─┤─ primary Postgres
                 └─ api ─┘         │
                                   ├─ replica (search/heavy read)
redis ← workers (timeline) 
     ← workers (embed)
     ← workers (graph)
```

## Vertical priorities (single node)

1. Disk IOPS and size for Postgres
2. RAM for Postgres + HNSW
3. CPU for embed workers
4. Network to clients

## Queue isolation

Do not share one queue for timeline projection and embedding. A stuck model download must not block session reconstruction.

## Limits to acknowledge

- Single primary remains write authority in v1 topologies
- Cross-region active-active is out of scope until sync semantics harden
- Redis loss may delay projections; event log remains durable in Postgres
