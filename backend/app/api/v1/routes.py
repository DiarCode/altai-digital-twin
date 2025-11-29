from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

# Add other API routes here
