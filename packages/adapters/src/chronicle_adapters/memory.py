"""In-memory adapters for tests and local development without Postgres."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from chronicle_domain.capture.envelope import EventEnvelope
from chronicle_domain.identity.consent import ConsentCategory, ConsentPolicy
from chronicle_domain.ports import AppendResult
from chronicle_domain.session.session import Session
from chronicle_domain.shared.ids import (
    DeviceId,
    EventId,
    SessionId,
    StoreOffset,
    WorkspaceId,
)


@dataclass
class InMemoryEventStore:
    _events: dict[str, tuple[EventEnvelope, str, StoreOffset]] = field(default_factory=dict)
    _by_id: dict[str, EventEnvelope] = field(default_factory=dict)
    _order: list[tuple[str, StoreOffset]] = field(default_factory=list)
    _offset: int = 0

    def append(self, envelope: EventEnvelope) -> AppendResult:
        key = f"{envelope.workspace_id}:{envelope.idempotency_key.value}"
        if key in self._events:
            existing, _fp, offset = self._events[key]
            return AppendResult(event_id=existing.event_id, store_offset=offset, created=False)
        self._offset += 1
        offset = StoreOffset(self._offset)
        fingerprint = envelope.payload_fingerprint()
        self._events[key] = (envelope, fingerprint, offset)
        self._by_id[str(envelope.event_id)] = envelope
        self._order.append((str(envelope.workspace_id), offset))
        return AppendResult(event_id=envelope.event_id, store_offset=offset, created=True)

    def get(self, event_id: EventId) -> EventEnvelope | None:
        return self._by_id.get(str(event_id))

    def get_by_idempotency(
        self, workspace_id: WorkspaceId, key: str
    ) -> tuple[EventEnvelope, str, StoreOffset] | None:
        return self._events.get(f"{workspace_id}:{key}")

    def read_from(
        self, workspace_id: WorkspaceId, offset: StoreOffset, limit: int
    ) -> list[tuple[EventEnvelope, StoreOffset]]:
        results: list[tuple[EventEnvelope, StoreOffset]] = []
        for ws, off in self._order:
            if ws != str(workspace_id) or off.value <= offset.value:
                continue
            env = next(e for e, _fp, o in self._events.values() if o == off)
            results.append((env, off))
            if len(results) >= limit:
                break
        return results


@dataclass
class InMemoryOutbox:
    jobs: list[tuple[EventId, str]] = field(default_factory=list)

    def enqueue(self, event_id: EventId, job_type: str = "project_event") -> None:
        self.jobs.append((event_id, job_type))


@dataclass
class InMemoryConsentPolicyStore:
    _policies: dict[str, ConsentPolicy] = field(default_factory=dict)

    def get(self, workspace_id: WorkspaceId) -> ConsentPolicy:
        key = str(workspace_id)
        if key not in self._policies:
            self._policies[key] = ConsentPolicy(workspace_id=workspace_id)
        return self._policies[key]

    def save(self, policy: ConsentPolicy) -> None:
        self._policies[str(policy.workspace_id)] = policy

    def enable_all(self, workspace_id: WorkspaceId) -> ConsentPolicy:
        policy = self.get(workspace_id)
        for category in ConsentCategory:
            policy.set_category(category, True)
        self.save(policy)
        return policy


@dataclass
class InMemorySessionRepository:
    _sessions: dict[str, Session] = field(default_factory=dict)

    def save(self, session: Session) -> None:
        self._sessions[str(session.id)] = session

    def get(self, session_id: SessionId) -> Session | None:
        return self._sessions.get(str(session_id))

    def find_open(self, workspace_id: WorkspaceId, device_id: DeviceId) -> Session | None:
        for session in self._sessions.values():
            if (
                session.is_open
                and session.workspace_id == workspace_id
                and session.device_id == device_id
            ):
                return session
        return None

    def list_for_workspace(self, workspace_id: WorkspaceId) -> list[Session]:
        return [
            session
            for session in self._sessions.values()
            if session.workspace_id == workspace_id
        ]


@dataclass
class InMemoryCredentialStore:
    _by_hash: dict[str, Any] = field(default_factory=dict)

    def save_issued(self, issued: Any) -> None:
        self._by_hash[issued.token_hash] = issued

    def find_by_raw_token(self, raw_token: str, service: Any) -> Any | None:
        from chronicle_application.auth import CredentialRecord, hash_token

        token_hash = hash_token(raw_token, pepper=service._pepper)
        issued = self._by_hash.get(token_hash)
        if issued is None:
            return None
        return CredentialRecord(
            credential_id=issued.credential_id,
            workspace_id=issued.workspace_id,
            actor_id=issued.actor_id,
            token_hash=issued.token_hash,
            label=issued.label,
            created_at=issued.created_at,
            revoked_at=None,
        )


@dataclass
class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


@dataclass
class UuidGenerator:
    def new_uuid(self) -> Any:
        return uuid4()
