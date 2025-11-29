# Altai Digital Twin — Backend

This is the Python backend for the Altai Digital Twin project. It uses a modular architecture and Prisma for data access to PostgreSQL. The workspace includes placeholders for vector DB integration and ML model interactions.

## What’s included
- FastAPI app in `backend/app/main.py`
- Prisma schema in `backend/prisma/schema.prisma`
- `app/api`, `app/services`, and `app/db` folders for modular structure
- `docker-compose.yml` for local dev (Postgres + Qdrant vector DB)
- `.env.example`, `.gitignore`

## Quick start (dev)
1. Copy `.env.example` -> `.env` and edit values.
2. Start services:

```powershell
cd backend
docker-compose up -d
```

3. Install local dependencies then run the app:
### Environment variables
Set the following environment variables in a `.env` file or your environment before running the app:

```
DATABASE_URL=postgresql://altai:altai@localhost:5432/altai
VECTOR_DB_URL=http://localhost:6333
JWT_SECRET_KEY=change-me-to-a-secure-random-key
CLIENT_URL=http://localhost:3000
COOKIE_NAME=access_token
COOKIE_SECURE=false
COOKIE_HTTPONLY=true
COOKIE_SAMESITE=lax
COOKIE_EXPIRE_MINUTES=1440
```


```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install uv
# Add dependencies using uv (helpful to manage new additions)
# Example: uv add fastapi uvicorn prisma psycopg[binary] bcrypt pyjwt qdrant-client python-dotenv
uv add fastapi uvicorn prisma psycopg[binary] bcrypt pyjwt qdrant-client python-dotenv
# Or install from requirements.txt
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Notes
- Prisma client is configured for Python; run `prisma generate` followed by `prisma migrate dev` to apply migrations.
- Vector DB integration is a placeholder — choose Postgres+pgvector, Milvus, or Weaviate as your production vector store.
 - Vector DB integration uses Qdrant in this project; repository includes qdrant in `docker-compose.yml` and a Qdrant-backed abstraction in `app/services/vector_db.py`.
 - Authentication uses HTTP-only cookies for session JWT token; login sets cookie at the client origin. See env options `CLIENT_URL` and cookie settings in `.env`.
 - Authentication uses HTTP-only cookies for session JWT token; login sets cookie at the client origin. Make sure `CLIENT_URL` is configured in `.env` and your browser sets cookies for that domain (CORS allow_credentials is enabled by default in the FastAPI app). A sample login from a front-end will look like:

```
fetch('http://localhost:8000/api/v1/auth/login', {
	method: 'POST',
	credentials: 'include',
	headers: {'Content-Type': 'application/json'},
	body: JSON.stringify({ username: 'jdoe', password: 's3cr3t' }),
})
```

The cookie will be HTTP-only, so it can't be read from JS. The backend will use the cookie to determine the current authenticated user.
