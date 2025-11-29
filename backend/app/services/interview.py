from __future__ import annotations
from typing import Any
from app.db import client


class InterviewService:
    """
    Service to operate on Interview questions/answers. This is a light placeholder —
    implement concrete retrieval, creation, and analysis methods.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    async def list_questions(self, limit: int = 10) -> list[dict]:
        # Example implementation using Prisma client; the model name is InterviewQuestion
        # return await client.interview_question.find_many(take=limit)
        raise NotImplementedError("list_questions is not implemented")

    async def create_question(self, question_text: str) -> Any:
        # return await client.interview_question.create(data={"question": question_text})
        raise NotImplementedError("create_question is not implemented")

    async def create_answer(self, question_id: int, answer_text: str, user_id: int) -> Any:
        # Implement creation and linking of an answer
        raise NotImplementedError("create_answer is not implemented")

    async def analyze_answer(self, answer_id: int) -> Any:
        # Placeholder for analysis using LLM or ML models
        raise NotImplementedError("analyze_answer is not implemented")
