"""Shared domain identifiers and validation errors."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


class DomainError(Exception):
    """Base class for domain-layer failures."""


class DomainValidationError(DomainError):
    """Raised when a value object or command fails validation."""


class InvariantViolation(DomainError):
    """Raised when an aggregate invariant would be broken."""


class ConsentDenied(DomainError):
    """Raised when capture is blocked by consent policy."""


@dataclass(frozen=True, slots=True)
class WorkspaceId:
    value: UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ActorId:
    value: UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class DeviceId:
    value: UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class EventId:
    value: UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class SessionId:
    value: UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class StoreOffset:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise DomainValidationError("store offset must be >= 0")
