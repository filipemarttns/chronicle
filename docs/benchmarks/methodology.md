# Benchmark Methodology

Chronicle benchmarks measure ingest, projection, embedding, search, and replay. Claims in README design targets must be reproducible with scripts in this directory once implementation lands.

## Principles

1. Publish hardware profile with every result table
2. Use synthetic datasets only
3. Separate cold vs warm cache runs
4. Report p50/p95/p99, not only averages
5. For ANN, report recall@k against exact search on a sample

## Hardware profiles

| Profile | Example |
| --- | --- |
| `dev-laptop` | 8–16 vCPU class, 32 GB RAM, NVMe |
| `single-site` | 8 vCPU, 32–64 GB RAM, SSD |
| `embed-gpu` | CUDA GPU for embedding throughput tests |

Exact SKUs recorded in result JSON.

## Workloads

| Suite | Measures |
| --- | --- |
| `ingest_sync` | Single-event POST ack latency/throughput |
| `ingest_batch` | Batch append throughput |
| `project_timeline` | Events/s projected |
| `embed_chunks` | Chunks/s |
| `search_ann` | Query latency + recall@10 |
| `replay_session` | Reconstruct 1h session |

## Dataset generators

Generators create deterministic synthetic events with seeded RNG. Parameters: event count, payload size distribution, workspace count, session idle patterns.

## Result format

```json
{
  "suite": "search_ann",
  "commit": "abc123",
  "profile": "single-site",
  "params": { "vectors": 1000000, "dims": 768, "k": 10 },
  "metrics": { "p50_ms": 0, "p95_ms": 0, "p99_ms": 0, "recall_at_10": 0 }
}
```

Store results under `docs/benchmarks/results/` when publishing release evidence.
