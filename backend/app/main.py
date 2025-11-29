from fastapi import FastAPI
from app.api.v1.routes import router as v1_router
from app.db import client

app = FastAPI(title="Altai Digital Twin - Backend")

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
