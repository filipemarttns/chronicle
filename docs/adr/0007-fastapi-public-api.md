# ADR-0007: FastAPI as Public HTTP Boundary

- Status: Accepted
- Date: 2026-01-20
- Deciders: Lead Maintainer
- Tags: api, python

## Context

Chronicle needs an HTTP boundary with first-class OpenAPI, strong request validation, async capability for I/O-bound ingest, and a typing story aligned with Python 3.14 domain code.

## Decision

Use **FastAPI** (with Pydantic models) as the inbound HTTP adapter. Controllers remain thin: authenticate, validate, call application services, map errors to the API error model.

OpenAPI is generated and published as a reviewable contract artifact.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Django REST Framework | Heavier for a service-centric hexagonal core |
| Flask + manual schema | Weaker default OpenAPI/typing integration |
| gRPC-only API | Poorer browser/extension ergonomics for v1 |
| Node HTTP API for backend | Splits domain language; Python chosen for ML/embedding adjacency |

## Consequences

- API package depends on application ports, not domain internals leaking HTTP types.
- Versioning lives in URL prefixes (`/v1`) per ADR-0016.
- Performance tuning focuses on Uvicorn/gunicorn workers and batch ingest endpoints.

## References

- ADR-0003, ADR-0016
- [api/overview.md](../api/overview.md)
