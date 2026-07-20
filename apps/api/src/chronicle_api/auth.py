"""HTTP authentication dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status

from chronicle_api.container import AppContainer, get_container


@dataclass(frozen=True, slots=True)
class Principal:
    workspace_id: UUID | None
    actor_id: UUID | None
    credential_id: UUID | None
    auth_mode: str


def container_dep() -> AppContainer:
    return get_container()


def require_principal(
    authorization: str | None = Header(default=None),
    container: AppContainer = Depends(container_dep),
) -> Principal:
    if container.settings.auth_mode == "dev":
        return Principal(
            workspace_id=None,
            actor_id=None,
            credential_id=None,
            auth_mode="dev",
        )
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "unauthorized",
                    "message": "Bearer token required",
                    "correlation_id": "auth",
                }
            },
        )
    raw = authorization.split(" ", 1)[1].strip()
    record = container.resolve_token(raw)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "unauthorized",
                    "message": "Invalid or revoked token",
                    "correlation_id": "auth",
                }
            },
        )
    return Principal(
        workspace_id=record.workspace_id,
        actor_id=record.actor_id,
        credential_id=record.credential_id,
        auth_mode="token",
    )


def enforce_workspace(principal: Principal, workspace_id: UUID) -> None:
    if principal.auth_mode == "dev":
        return
    if principal.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "forbidden",
                    "message": "Token is not scoped to this workspace",
                    "correlation_id": "authz",
                }
            },
        )
