# Changelog

All notable changes to Chronicle are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PostgreSQL persistence adapters for events, outbox, consent, sessions, timeline, and memory chunks
- Alembic initial schema migration (`0001_initial`)
- API dependency container with `CHRONICLE_STORE=memory|postgres`
- Celery worker task to drain outbox projections
- Next.js console pages for timeline replay and search
- Docker Compose services for Postgres, Redis, API, worker, and web

### Changed
- Ingest path projects session/timeline/memory inline when `CHRONICLE_SYNC_PROJECT=true`

### Fixed
- Timeline serialization for slotted dataclass read models

## [0.1.0-rc.1] - 2026-07-15

### Added
- Release candidate packaging for the documentation and core domain foundation
- Docker API image and Compose reference service
- OpenAPI-aligned `/v1` routes for events, timeline, search, and consent

### Fixed
- Timeline serialization for slotted dataclass read models


## [0.1.0-rc.1] - 2026-07-15

Release candidate for early self-hosted operators.

