.PHONY: test lint typecheck run-api

test:
	pytest -q

lint:
	ruff check packages apps || true

typecheck:
	python -c "import chronicle_domain, chronicle_application, chronicle_adapters, chronicle_api"

run-api:
	uvicorn chronicle_api.main:app --reload --port 8000
