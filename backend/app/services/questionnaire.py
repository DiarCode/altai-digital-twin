from app.db import client
from app.api.v1.schemas.questionnaire import QuestionType
from prisma.models import QuestionnaireQuestion, QuestionnaireResponse
from typing import List

async def get_all_questions() -> List[QuestionnaireQuestion]:
    return await client.questionnairequestion.find_many()

async def create_question(text: str, q_type: QuestionType) -> QuestionnaireQuestion:
    return await client.questionnairequestion.create(
        data={
            "text": text,
            "type": q_type
        }
    )

async def save_response(
    user_id: int, 
    question_id: str, 
    likert_value: int | None = None, 
    audio_path: str | None = None,
    transcription: str | None = None
) -> QuestionnaireResponse:
    return await client.questionnaireresponse.upsert(
        where={
            "userId_questionId": {
                "userId": user_id,
                "questionId": question_id
            }
        },
        data={
            "create": {
                "userId": user_id,
                "questionId": question_id,
                "likertValue": likert_value,
                "audioPath": audio_path,
                "transcription": transcription
            },
            "update": {
                "likertValue": likert_value,
                "audioPath": audio_path,
                "transcription": transcription
            }
        }
    )
