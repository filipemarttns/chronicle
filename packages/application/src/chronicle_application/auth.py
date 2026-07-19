"""Credential issuance and token verification."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


def hash_token(raw_token: str, *, pepper: str = "") -> str:
    """Return a hex digest for storage. Never store raw bearer tokens."""

    material = f"{pepper}{raw_token}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def generate_token() -> str:
    return secrets.token_urlsafe(32)


@dataclass(frozen=True, slots=True)
class IssuedCredential:
    credential_id: UUID
    workspace_id: UUID
    actor_id: UUID
    token: str
    token_hash: str
    label: str
    created_at: datetime


@dataclass
class CredentialRecord:
    credential_id: UUID
    workspace_id: UUID
    actor_id: UUID
    token_hash: str
    label: str
    created_at: datetime
    revoked_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None


class CredentialService:
    """Issue and verify API credentials."""

    def __init__(self, pepper: str = "") -> None:
        self._pepper = pepper

    def issue(
        self,
        *,
        workspace_id: UUID,
        actor_id: UUID,
        label: str = "default",
    ) -> IssuedCredential:
        token = generate_token()
        now = datetime.now(timezone.utc)
        return IssuedCredential(
            credential_id=uuid4(),
            workspace_id=workspace_id,
            actor_id=actor_id,
            token=token,
            token_hash=hash_token(token, pepper=self._pepper),
            label=label,
            created_at=now,
        )

    def verify_hash(self, raw_token: str, stored_hash: str) -> bool:
        digest = hash_token(raw_token, pepper=self._pepper)
        return hmac.compare_digest(digest, stored_hash)
