from enum import Enum
from pydantic import BaseModel

class QuestionType(str, Enum):
    LIKERT = "LIKERT"
    AUDIO = "AUDIO"

class QuestionDTO(BaseModel):
    id: str
    question: str
    type: QuestionType
    order: int

    class Config:
        from_attributes = True

class LikertAnswerCreate(BaseModel):
    question_id: str
    likert_value: int
