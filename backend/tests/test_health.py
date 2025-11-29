import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint(monkeypatch):
    # Avoid connecting to a real DB during this simple test
    async def _noop():
        return None

    from app import db as db_module
    monkeypatch.setattr(db_module.client, "connect", _noop)
    monkeypatch.setattr(db_module.client, "disconnect", _noop)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
