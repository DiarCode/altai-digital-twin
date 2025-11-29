# Altai Digital Twin — Backend

This is the Python backend for the Altai Digital Twin project. It uses a modular architecture and Prisma for data access to PostgreSQL. The workspace includes placeholders for vector DB integration and ML model interactions.

## What’s included
- FastAPI app in `backend/app/main.py`
- Prisma schema in `backend/prisma/schema.prisma`
- `app/api`, `app/services`, and `app/db` folders for modular structure
- `docker-compose.yml` for local dev (Postgres + pgvector)
- `.env.example`, `.gitignore`

## Quick start (dev)
1. Copy `.env.example` -> `.env` and edit values.
2. Start services:

```powershell
cd backend
docker-compose up -d
```

3. Install local dependencies then run the app:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Notes
- Prisma client is configured for Python; run `prisma generate` followed by `prisma migrate dev` to apply migrations.
- Vector DB integration is a placeholder — choose Postgres+pgvector, Milvus, or Weaviate as your production vector store.
