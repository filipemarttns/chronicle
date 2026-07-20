.PHONY: test lint typecheck run-api run-worker migrate smoke

test:
	python -m pytest -q

lint:
	ruff check packages apps || true

typecheck:
	python -c "import chronicle_domain, chronicle_application, chronicle_adapters, chronicle_api"

run-api:
	CHRONICLE_STORE=memory uvicorn chronicle_api.main:app --reload --port 8000

run-api-postgres:
	CHRONICLE_STORE=postgres uvicorn chronicle_api.main:app --reload --port 8000

run-worker:
	celery -A chronicle_worker.celery_app.celery_app worker -B -l INFO

migrate:
	alembic upgrade head

smoke:
	python scripts/smoke_api.py
