"""Celery worker for outbox projection jobs."""

from __future__ import annotations

import os

from celery import Celery

from chronicle_adapters.persistence import OutboxProjector, create_db_engine, create_session_factory

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://chronicle:chronicle@localhost:5432/chronicle",
)

celery_app = Celery("chronicle", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.task_default_queue = "chronicle.default"
celery_app.conf.timezone = "UTC"


def _projector() -> OutboxProjector:
    engine = create_db_engine(DATABASE_URL)
    factory = create_session_factory(engine)
    return OutboxProjector(factory)


@celery_app.task(name="chronicle.project_outbox_batch")
def project_outbox_batch(limit: int = 50) -> dict[str, int]:
    processed = _projector().process_batch(limit=limit)
    return {"processed": processed}


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs: object) -> None:
    sender.add_periodic_task(5.0, project_outbox_batch.s(50), name="drain-outbox-every-5s")
