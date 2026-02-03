"""Celery worker entrypoint skeleton."""

from __future__ import annotations

# Worker wiring lands with Redis-backed outbox publishing (ADR-0006 / ADR-0015).
# Local development currently projects inline in the API process for Milestone 1–3.

APP_NAME = "chronicle-worker"
