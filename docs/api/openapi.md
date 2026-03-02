# OpenAPI Strategy

- Source of truth: FastAPI route definitions + Pydantic models
- Published artifact: `openapi.json` per major version in releases
- CI: schema diff check against previous release for unexpected breaks
- Examples: synthetic only; no real user data

Until the API package exists, [overview.md](overview.md) is the design contract.
