"""Application settings loaded from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    env: str = "local"
    store_mode: str = "memory"  # memory | postgres
    database_url: str = "postgresql+psycopg://chronicle:chronicle@localhost:5432/chronicle"
    redis_url: str = "redis://localhost:6379/0"
    sync_project: bool = True
    auth_mode: str = "dev"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> Settings:
        store = os.getenv("CHRONICLE_STORE", "memory").lower()
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://chronicle:chronicle@localhost:5432/chronicle",
        )
        if os.getenv("CHRONICLE_STORE") is None and os.getenv("DATABASE_URL"):
            store = "postgres"
        return cls(
            env=os.getenv("CHRONICLE_ENV", "local"),
            store_mode=store,
            database_url=database_url,
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            sync_project=os.getenv("CHRONICLE_SYNC_PROJECT", "true").lower() == "true",
            auth_mode=os.getenv("CHRONICLE_AUTH_MODE", "dev"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
