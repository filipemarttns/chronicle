"""Chronicle FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from chronicle_api.container import AppContainer, get_container, reset_container_for_tests
from chronicle_application.ingest import IdempotencyConflictError, IngestEventCommand
from chronicle_domain.shared.ids import ConsentDenied, DomainValidationError


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_container()
    yield


app = FastAPI(
    title="Chronicle API",
    version="0.1.0",
    summary="Developer Memory Engine HTTP API",
    lifespan=lifespan,
)


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


def container_dep() -> AppContainer:
    return get_container()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(container: AppContainer = Depends(container_dep)) -> dict[str, Any]:
    return container.readiness()


@app.post("/v1/events", response_model=EventIngestResponse)
def ingest_event(
    body: EventIngestRequest,
    container: AppContainer = Depends(container_dep),
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
        result = container.ingest(command)
    except ConsentDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "consent_required",
                    "message": str(exc),
                    "correlation_id": body.correlation_id or str(uuid4()),
                }
            },
        ) from exc
    except IdempotencyConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "idempotency_conflict",
                    "message": str(exc),
                    "correlation_id": body.correlation_id or str(uuid4()),
                }
            },
        ) from exc
    except DomainValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "validation_failed",
                    "message": str(exc),
                    "correlation_id": body.correlation_id or str(uuid4()),
                }
            },
        ) from exc

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
    container: AppContainer = Depends(container_dep),
) -> dict[str, Any]:
    items = container.replay(workspace_id, limit=limit, after_offset=after_offset)
    return {
        "items": [asdict(item) for item in items],
        "next_cursor": str(items[-1].store_offset) if items else None,
    }


@app.post("/v1/search")
def search_memory(
    body: SearchRequest,
    container: AppContainer = Depends(container_dep),
) -> dict[str, Any]:
    hits = container.search(body.workspace_id, body.query, limit=body.limit)
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
def get_consent(
    workspace_id: UUID,
    container: AppContainer = Depends(container_dep),
) -> dict[str, Any]:
    policy = container.get_consent(workspace_id)
    return {
        "workspace_id": str(workspace_id),
        "categories": {k.value: v for k, v in policy.categories.items()},
    }


@app.put("/v1/consent")
def put_consent(
    body: ConsentUpdateRequest,
    container: AppContainer = Depends(container_dep),
) -> dict[str, Any]:
    policy = container.put_consent(body.workspace_id, body.categories)
    return {
        "workspace_id": str(body.workspace_id),
        "categories": {k.value: v for k, v in policy.categories.items()},
    }


@app.post("/v1/admin/outbox/process")
def process_outbox(
    limit: int = 50,
    container: AppContainer = Depends(container_dep),
) -> dict[str, int]:
    """Drain outbox synchronously (useful without Celery in local postgres mode)."""

    return {"processed": container.process_outbox(limit=limit)}


def reset_state() -> None:
    """Test helper to reset process-global in-memory state."""

    reset_container_for_tests()
