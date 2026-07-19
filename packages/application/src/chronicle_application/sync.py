"""Multi-device sync application helpers (event-log based)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from chronicle_application.ingest import IngestEventCommand, IngestResult, IdempotencyConflictError
from chronicle_domain.shared.ids import StoreOffset, WorkspaceId


@dataclass(frozen=True, slots=True)
class SyncConflict:
    conflict_id: UUID
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class SyncPushResult:
    accepted: list[IngestResult]
    conflicts: list[SyncConflict]


@dataclass(frozen=True, slots=True)
class SyncPullResult:
    events: list[tuple[object, StoreOffset]]
    next_cursor: int
