# Backend Layout Changes

This file documents the layout changes created by the Copilot assistant.

Folders created:
- `app/` - FastAPI app package
- `app/api/v1/` - API endpoints
- `app/core/` - application configuration
- `app/db/` - Prisma database client
- `app/models/` - pydantic models
- `app/services/` - services for ML and vector DB integrations
- `prisma/` - Prisma schema and migrations
- `tests/` - tests and test helpers
- `scripts/` - helper scripts (migrate.ps1, migrate.sh)

Files added:
- `.gitignore`, `.env.example`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `requirements.txt`
- `README.md` with quick start steps
- `prisma/schema.prisma` generating `prisma-client-py` and example models
- `app/main.py` FastAPI application entry
- `app/api/v1/routes.py` health endpoint
- `app/db/__init__.py` prisma client
- `app/services/ml.py` placeholder service
- `app/services/vector_db.py` placeholder service
- `tests/test_health.py` simple health endpoint test

Next steps and recommendations:
- Install `prisma` and generate client: `pip install prisma && prisma generate`.
- Choose your vector DB (pgvector, Milvus, Weaviate) and update `docker-compose.yml` accordingly.
- Add CI pipeline to run tests, format, lint, and run migrations.
- Add real model invocation for MLService and Vector DB implementations.
