"""Chronicle FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from chronicle_api.auth import Principal, enforce_workspace, require_principal
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


class SyncPushRequest(BaseModel):
    workspace_id: UUID
    device_id: UUID
    events: list[EventIngestRequest]


class SyncPullRequest(BaseModel):
    workspace_id: UUID
    device_id: UUID
    cursor: int = Field(ge=0)
    limit: int = Field(default=100, ge=1, le=500)


class IssueTokenRequest(BaseModel):
    workspace_id: UUID
    actor_id: UUID
    label: str = "default"


def container_dep() -> AppContainer:
    return get_container()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(container: AppContainer = Depends(container_dep)) -> dict[str, Any]:
    return container.readiness()


@app.post("/v1/auth/tokens")
def issue_token(
    body: IssueTokenRequest,
    container: AppContainer = Depends(container_dep),
    x_chronicle_bootstrap: str | None = Header(default=None, alias="X-Chronicle-Bootstrap"),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    """Issue a workspace-scoped API token.

    In ``token`` auth mode, callers must present ``X-Chronicle-Bootstrap`` matching
    ``CHRONICLE_BOOTSTRAP_TOKEN``, or an existing valid bearer token for the same workspace.
    """

    if container.settings.auth_mode == "token":
        bootstrap = container.settings.bootstrap_token
        allowed = bool(bootstrap) and x_chronicle_bootstrap == bootstrap
        if not allowed and authorization and authorization.lower().startswith("bearer "):
            record = container.resolve_token(authorization.split(" ", 1)[1].strip())
            allowed = record is not None and record.workspace_id == body.workspace_id
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "unauthorized",
                        "message": "Bootstrap or workspace token required to issue credentials",
                        "correlation_id": "auth",
                    }
                },
            )
    issued = container.issue_credential(
        workspace_id=body.workspace_id, actor_id=body.actor_id, label=body.label
    )
    return {
        "credential_id": str(issued.credential_id),
        "workspace_id": str(issued.workspace_id),
        "actor_id": str(issued.actor_id),
        "token": issued.token,
        "label": issued.label,
        "created_at": issued.created_at.isoformat(),
    }


@app.post("/v1/events", response_model=EventIngestResponse)
def ingest_event(
    body: EventIngestRequest,
    container: AppContainer = Depends(container_dep),
    principal: Principal = Depends(require_principal),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> EventIngestResponse:
    enforce_workspace(principal, body.workspace_id)
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
    principal: Principal = Depends(require_principal),
) -> dict[str, Any]:
    enforce_workspace(principal, workspace_id)
    items = container.replay(workspace_id, limit=limit, after_offset=after_offset)
    return {
        "items": [asdict(item) for item in items],
        "next_cursor": str(items[-1].store_offset) if items else None,
    }


@app.post("/v1/search")
def search_memory(
    body: SearchRequest,
    container: AppContainer = Depends(container_dep),
    principal: Principal = Depends(require_principal),
) -> dict[str, Any]:
    enforce_workspace(principal, body.workspace_id)
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
        "model_id": container.embedder.model_id,
    }


@app.get("/v1/consent")
def get_consent(
    workspace_id: UUID,
    container: AppContainer = Depends(container_dep),
    principal: Principal = Depends(require_principal),
) -> dict[str, Any]:
    enforce_workspace(principal, workspace_id)
    policy = container.get_consent(workspace_id)
    return {
        "workspace_id": str(workspace_id),
        "categories": {k.value: v for k, v in policy.categories.items()},
    }


@app.put("/v1/consent")
def put_consent(
    body: ConsentUpdateRequest,
    container: AppContainer = Depends(container_dep),
    principal: Principal = Depends(require_principal),
) -> dict[str, Any]:
    enforce_workspace(principal, body.workspace_id)
    policy = container.put_consent(body.workspace_id, body.categories)
    return {
        "workspace_id": str(body.workspace_id),
        "categories": {k.value: v for k, v in policy.categories.items()},
    }


@app.get("/v1/sessions")
def list_sessions(
    workspace_id: UUID,
    container: AppContainer = Depends(container_dep),
    principal: Principal = Depends(require_principal),
) -> dict[str, Any]:
    enforce_workspace(principal, workspace_id)
    sessions = container.list_sessions(workspace_id)
    return {
        "items": [
            {
                "id": str(s.id),
                "workspace_id": str(s.workspace_id),
                "device_id": str(s.device_id),
                "started_at": s.started_at.isoformat(),
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "algorithm_version": s.algorithm_version,
                "last_activity_at": s.last_activity_at.isoformat(),
            }
            for s in sessions
        ],
        "next_cursor": None,
    }


@app.get("/v1/analytics/summary")
def analytics_summary(
    workspace_id: UUID,
    container: AppContainer = Depends(container_dep),
    principal: Principal = Depends(require_principal),
    from_time: datetime = Query(..., alias="from"),
    to_time: datetime = Query(..., alias="to"),
) -> dict[str, Any]:
    enforce_workspace(principal, workspace_id)
    summary = container.analytics_summary(workspace_id, from_time, to_time)
    return {
        "workspace_id": summary.workspace_id,
        "from": summary.from_time.isoformat(),
        "to": summary.to_time.isoformat(),
        "metrics": summary.metrics,
    }


@app.post("/v1/sync/push")
def sync_push(
    body: SyncPushRequest,
    container: AppContainer = Depends(container_dep),
    principal: Principal = Depends(require_principal),
) -> dict[str, Any]:
    enforce_workspace(principal, body.workspace_id)
    commands = [
        IngestEventCommand(
            type=event.type,
            schema_version=event.schema_version,
            occurred_at=event.occurred_at,
            source=event.source,
            actor_id=event.actor_id,
            workspace_id=body.workspace_id,
            device_id=body.device_id,
            idempotency_key=event.idempotency_key,
            payload=event.payload,
            event_id=event.event_id,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
        )
        for event in body.events
    ]
    result = container.sync_push(commands)
    return {
        "accepted": [
            {
                "event_id": item.event_id,
                "store_offset": item.store_offset,
                "created": item.created,
            }
            for item in result.accepted
        ],
        "conflicts": [
            {
                "conflict_id": str(conflict.conflict_id),
                "idempotency_key": conflict.idempotency_key,
            }
            for conflict in result.conflicts
        ],
    }


@app.post("/v1/sync/pull")
def sync_pull(
    body: SyncPullRequest,
    container: AppContainer = Depends(container_dep),
    principal: Principal = Depends(require_principal),
) -> dict[str, Any]:
    enforce_workspace(principal, body.workspace_id)
    rows, next_cursor = container.sync_pull(
        body.workspace_id, body.cursor, limit=body.limit
    )
    events = []
    for envelope, offset in rows:
        events.append(
            {
                "event_id": str(envelope.event_id),
                "type": envelope.type.value,
                "schema_version": envelope.schema_version.value,
                "occurred_at": envelope.occurred_at.isoformat(),
                "source": envelope.source.value,
                "actor_id": str(envelope.actor_id),
                "workspace_id": str(envelope.workspace_id),
                "device_id": str(envelope.device_id),
                "idempotency_key": envelope.idempotency_key.value,
                "payload": dict(envelope.payload),
                "store_offset": offset.value,
            }
        )
    return {"events": events, "next_cursor": next_cursor}


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
