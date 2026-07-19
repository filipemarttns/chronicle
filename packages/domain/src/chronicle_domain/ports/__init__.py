"""Ports for persistence and infrastructure (domain-facing protocols)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from chronicle_domain.capture.envelope import EventEnvelope
from chronicle_domain.identity.consent import ConsentPolicy
from chronicle_domain.session.session import Session
from chronicle_domain.shared.ids import DeviceId, EventId, SessionId, StoreOffset, WorkspaceId


@dataclass(frozen=True, slots=True)
class AppendResult:
    event_id: EventId
    store_offset: StoreOffset
    created: bool


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class EventStorePort(Protocol):
    def append(self, envelope: EventEnvelope) -> AppendResult: ...

    def get(self, event_id: EventId) -> EventEnvelope | None: ...

    def get_by_idempotency(
        self, workspace_id: WorkspaceId, key: str
    ) -> tuple[EventEnvelope, str, StoreOffset] | None: ...

    def read_from(
        self, workspace_id: WorkspaceId, offset: StoreOffset, limit: int
    ) -> list[tuple[EventEnvelope, StoreOffset]]: ...


class OutboxPort(Protocol):
    def enqueue(self, event_id: EventId, job_type: str = "project_event") -> None: ...


class ConsentPolicyPort(Protocol):
    def get(self, workspace_id: WorkspaceId) -> ConsentPolicy: ...

    def save(self, policy: ConsentPolicy) -> None: ...


class SessionRepositoryPort(Protocol):
    def save(self, session: Session) -> None: ...

    def get(self, session_id: SessionId) -> Session | None: ...

    def find_open(self, workspace_id: WorkspaceId, device_id: DeviceId) -> Session | None: ...


class ClockPort(Protocol):
    def now(self) -> Any: ...


class IdGeneratorPort(Protocol):
    def new_uuid(self) -> Any: ...


class EmbeddingPort(Protocol):
    """Produce dense vectors for memory indexing and query embedding."""

    model_id: str
    dims: int

    def embed(self, text: str) -> list[float]: ...
