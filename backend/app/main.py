from fastapi import FastAPI
from app.api.v1.routes import router as v1_router
from app.db import client
from app.middleware.cookie_auth import CookieAuthMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title="Altai Digital Twin - Backend")
app.add_middleware(CORSMiddleware, allow_origins=[settings.CLIENT_URL], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(CookieAuthMiddleware)

app.include_router(v1_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    # connect Prisma client
    await client.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await client.disconnect()


@app.get("/")
async def root():
    return {"message": "Altai Digital Twin backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.SERVER_PORT)
