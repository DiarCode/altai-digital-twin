import pytest
from httpx import AsyncClient
from app.main import app
from datetime import date


@pytest.mark.asyncio
async def test_register_login(monkeypatch):
    # Avoid connecting to a real DB
    async def _noop():
        return None

    from app import db as db_module
    monkeypatch.setattr(db_module.client, "connect", _noop)
    monkeypatch.setattr(db_module.client, "disconnect", _noop)

    # Fake Prisma user create/find
    fake_user = {
        "id": 1,
        "username": "jdoe",
        "password": "$2b$12$fake",
        "gender": "m",
        "birthdate": date(1990, 1, 1),
        "createdAt": "2025-01-01T00:00:00Z",
    }

    async def fake_find_unique(where):
        if where.get("username") == "jdoe":
            return fake_user
        return None

    async def fake_create(data):
        return {**{"id": 2}, **data, "createdAt": "2025-01-01T00:00:00Z"}

    monkeypatch.setattr(db_module.client.user, "find_unique", fake_find_unique)
    monkeypatch.setattr(db_module.client.user, "create", fake_create)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # register a new user
        r = await ac.post("/api/v1/auth/register", json={
            "username": "newuser",
            "password": "s3cr3t",
            "gender": "f",
            "birthdate": "1995-01-01"
        })
        assert r.status_code == 200
        # login - monkeypatch auth_service to avoid actual bcrypt checking
        from app.services import auth as auth_service

        async def fake_auth(username, password):
            return fake_user

        monkeypatch.setattr(auth_service, "authenticate_user", fake_auth)
        r2 = await ac.post("/api/v1/auth/login", json={"username": "jdoe", "password": "s3cr3t"})
        assert r2.status_code == 200
        # Cookie should be set
        assert "access_token" in r2.cookies or "access_token" in ac.cookies
        # Now get /me with the cookie; client reuses cookies
        r3 = await ac.get("/api/v1/auth/me")
        assert r3.status_code == 200
