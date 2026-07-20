# Changelog

All notable changes to Chronicle are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PostgreSQL persistence adapters for events, outbox, consent, sessions, timeline, and memory chunks
- Alembic initial schema migration (`0001_initial`) and pgvector/auth follow-up (`0002_pgvector_auth`)
- API dependency container with `CHRONICLE_STORE=memory|postgres`
- Celery worker task to drain outbox projections
- Next.js console pages for timeline replay and search
- Docker Compose services for Postgres (pgvector), Redis, API, worker, and web
- Sessions, analytics summary, and sync push/pull API routes
- MCP tool surface (`search_memory`, `get_timeline`, `get_session_summary`)
- VS Code extension HTTP event emission
- Tauri desktop control-plane stub
- Hashing embedder and cosine/hybrid memory search (384-d, CI-safe)
- Workspace-scoped API credentials with hashed tokens and bootstrap issuance
- Bearer auth gate (`CHRONICLE_AUTH_MODE=token`) and `POST /v1/auth/tokens`

### Changed
- Ingest path projects session/timeline/memory inline when `CHRONICLE_SYNC_PROJECT=true`
- Compose reference API defaults to token auth with bootstrap/pepper placeholders

### Fixed
- Timeline serialization for slotted dataclass read models
- Short-query memory search when hashing embeddings alone scored near zero
- CORS for local web console origins
- Root Compose entrypoint and API smoke script for the public quick start

## [0.1.0-rc.1] - 2026-07-15

Release candidate for early self-hosted operators.

### Added
- Release candidate packaging for the documentation and core domain foundation
- Docker API image and Compose reference service
- OpenAPI-aligned `/v1` routes for events, timeline, search, and consent

### Fixed
- Timeline serialization for slotted dataclass read models

