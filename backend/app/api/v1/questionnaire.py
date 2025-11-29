from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Form
from typing import List
from app.api.v1.schemas.questionnaire import QuestionDTO, QuestionType
from app.services import questionnaire as questionnaire_service
from app.services.s3 import s3_service
from pydantic import BaseModel

router = APIRouter()

def get_current_user(request: Request):
    if not hasattr(request.state, "user") or not request.state.user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.user

class QuestionCreate(BaseModel):
    text: str
    type: QuestionType

@router.post("/questions", response_model=QuestionDTO)
async def create_question(
    question: QuestionCreate,
    user=Depends(get_current_user)
):
    created = await questionnaire_service.create_question(question.text, question.type)
    return QuestionDTO(id=created.id, question=created.text, type=created.type)

@router.get("/questions", response_model=List[QuestionDTO])
async def get_questions(user=Depends(get_current_user)):
    questions = await questionnaire_service.get_all_questions()
    return [QuestionDTO(id=q.id, question=q.text, type=q.type) for q in questions]

@router.post("/questions/{question_id}/answer")
async def answer_question(
    question_id: str,
    answer: Optional[int] = Form(None),
    audio: Optional[UploadFile] = File(None),
    user=Depends(get_current_user)
):
    likert_value = None
    audio_path = None

    if answer is not None:
        likert_value = answer
    
    if audio is not None:
        extension = audio.filename.split(".")[-1] if "." in audio.filename else "wav"
        object_name = f"{user.id}/{question_id}/audio.{extension}"
        s3_path = s3_service.upload_file(audio.file, object_name)
        if not s3_path:
            raise HTTPException(status_code=500, detail="Failed to upload audio")
        audio_path = s3_path

    if likert_value is None and audio_path is None:
        raise HTTPException(status_code=400, detail="Either answer or audio must be provided")

    response = await questionnaire_service.save_response(
        user_id=user.id,
        question_id=question_id,
        likert_value=likert_value,
        audio_path=audio_path
    )
    return {"status": "success", "id": response.id}
