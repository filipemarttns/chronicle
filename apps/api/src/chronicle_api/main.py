"""Chronicle FastAPI application."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from chronicle_adapters.memory import (
    InMemoryConsentPolicyStore,
    InMemoryEventStore,
    InMemoryOutbox,
    InMemorySessionRepository,
)
from chronicle_application.ingest import (
    IdempotencyConflictError,
    IngestEventCommand,
    IngestService,
)
from chronicle_application.memory import MemoryIndex
from chronicle_application.session_projection import SessionProjector
from chronicle_application.timeline import TimelineProjector
from chronicle_domain.identity.consent import ConsentCategory
from chronicle_domain.shared.ids import ConsentDenied, DomainValidationError, WorkspaceId

app = FastAPI(
    title="Chronicle API",
    version="0.1.0",
    summary="Developer Memory Engine HTTP API",
)

_store = InMemoryEventStore()
_outbox = InMemoryOutbox()
_consent = InMemoryConsentPolicyStore()
_sessions = InMemorySessionRepository()
_timeline = TimelineProjector()
_memory = MemoryIndex()
_ingest = IngestService(_store, _outbox, _consent)
_session_projector = SessionProjector(_sessions)


class EventIngestRequest(BaseModel):
    type: str
    schema_version: int = Field(ge=1)
    occurred_at: datetime
    source: str
    actor_id: UUID
    workspace_id: UUID
    device_id: UUID
    idempotency_key: str = Field(min_length=8, max_length=200)
    payload: dict[str, Any]
    event_id: UUID | None = None
    correlation_id: str | None = None
    causation_id: str | None = None


class EventIngestResponse(BaseModel):
    event_id: UUID
    store_offset: int
    created: bool


class SearchRequest(BaseModel):
    workspace_id: UUID
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=10, ge=1, le=50)


class ConsentUpdateRequest(BaseModel):
    workspace_id: UUID
    categories: dict[str, bool]


def get_ingest_service() -> IngestService:
    return _ingest


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, Any]:
    return {"status": "ready", "checks": {"event_store": "ok", "mode": "in_memory"}}


@app.post("/v1/events", response_model=EventIngestResponse)
def ingest_event(
    body: EventIngestRequest,
    service: IngestService = Depends(get_ingest_service),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> EventIngestResponse:
    key = idempotency_key or body.idempotency_key
    command = IngestEventCommand(
        type=body.type,
        schema_version=body.schema_version,
        occurred_at=body.occurred_at,
        source=body.source,
        actor_id=body.actor_id,
        workspace_id=body.workspace_id,
        device_id=body.device_id,
        idempotency_key=key,
        payload=body.payload,
        event_id=body.event_id,
        correlation_id=body.correlation_id,
        causation_id=body.causation_id,
    )
    try:
        result = service.ingest(command)
    except ConsentDenied as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
            "error": {
                "code": "consent_required",
                "message": str(exc),
                "correlation_id": body.correlation_id or str(uuid4()),
            }
        }) from exc
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
            "error": {
                "code": "idempotency_conflict",
                "message": str(exc),
                "correlation_id": body.correlation_id or str(uuid4()),
            }
        }) from exc
    except DomainValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={
            "error": {
                "code": "validation_failed",
                "message": str(exc),
                "correlation_id": body.correlation_id or str(uuid4()),
            }
        }) from exc

    from chronicle_domain.shared.ids import EventId, StoreOffset

    envelope = _store.get(EventId(result.event_id))
    if envelope is not None and result.created:
        session = _session_projector.apply(envelope)
        _timeline.apply(envelope, StoreOffset(result.store_offset), session.id.value)
        _memory.index_event(envelope)

    return EventIngestResponse(
        event_id=result.event_id,
        store_offset=result.store_offset,
        created=result.created,
    )


@app.get("/v1/timelines/replay")
def replay_timeline(
    workspace_id: UUID,
    limit: int = 50,
    after_offset: int = 0,
) -> dict[str, Any]:
    from dataclasses import asdict

    items = _timeline.replay(WorkspaceId(workspace_id), limit=limit, after_offset=after_offset)
    return {
        "items": [asdict(item) for item in items],
        "next_cursor": str(items[-1].store_offset) if items else None,
    }


@app.post("/v1/search")
def search_memory(body: SearchRequest) -> dict[str, Any]:
    hits = _memory.search(body.query, limit=body.limit)
    return {
        "hits": [
            {
                "chunk_id": str(hit.chunk_id),
                "score": hit.score,
                "snippet": hit.snippet,
                "citations": [str(c) for c in hit.citations],
            }
            for hit in hits
        ],
        "model_id": "token-overlap-v1",
    }


@app.get("/v1/consent")
def get_consent(workspace_id: UUID) -> dict[str, Any]:
    policy = _consent.get(WorkspaceId(workspace_id))
    return {
        "workspace_id": str(workspace_id),
        "categories": {k.value: v for k, v in policy.categories.items()},
    }


@app.put("/v1/consent")
def put_consent(body: ConsentUpdateRequest) -> dict[str, Any]:
    policy = _consent.get(WorkspaceId(body.workspace_id))
    for name, enabled in body.categories.items():
        policy.set_category(ConsentCategory(name), enabled)
    _consent.save(policy)
    return {
        "workspace_id": str(body.workspace_id),
        "categories": {k.value: v for k, v in policy.categories.items()},
    }


def reset_state() -> None:
    """Test helper to reset process-global in-memory state."""

    global _store, _outbox, _consent, _sessions, _timeline, _memory, _ingest, _session_projector
    _store = InMemoryEventStore()
    _outbox = InMemoryOutbox()
    _consent = InMemoryConsentPolicyStore()
    _sessions = InMemorySessionRepository()
    _timeline = TimelineProjector()
    _memory = MemoryIndex()
    _ingest = IngestService(_store, _outbox, _consent)
    _session_projector = SessionProjector(_sessions)


