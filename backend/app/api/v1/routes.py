from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.questionnaire import router as questionnaire_router

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(questionnaire_router, prefix="/questionnaire", tags=["questionnaire"])

# Add other API routes here
