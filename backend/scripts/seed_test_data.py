from __future__ import annotations

import asyncio
from datetime import datetime
from prisma import Prisma


async def main() -> None:
    db = Prisma()
    await db.connect()

    # Create or get a test user
    username = "test_ingest_user"
    user = await db.user.find_unique(where={"username": username})
    if not user:
        user = await db.user.create(
            data={
                "username": username,
                "password": "password123",
                "gender": "other",
                "birthdate": datetime(1990, 1, 1),
            }
        )

    # Create two questions (LIKERT and AUDIO)
    likert_q = await db.questionnairequestion.create(
        data={"text": "I enjoy working in teams.", "type": "LIKERT"}
    )

    audio_q = await db.questionnairequestion.create(
        data={"text": "Tell me about a project you loved working on.", "type": "AUDIO"}
    )

    # Create responses for the user
    likert_resp = await db.questionnaireresponse.create(
        data={
            "userId": user.id,
            "questionId": likert_q.id,
            "likertValue": 4,
        }
    )

    audio_resp = await db.questionnaireresponse.create(
        data={
            "userId": user.id,
            "questionId": audio_q.id,
            "audioPath": "audio/test_user_project.wav",
        }
    )

    print("Created test data:")
    print(f"  user.id = {user.id} (username={username})")
    print(f"  likert_question.id = {likert_q.id}")
    print(f"  audio_question.id  = {audio_q.id}")
    print(f"  likert_response.id = {likert_resp.id}")
    print(f"  audio_response.id  = {audio_resp.id}")

    print("\nSample transcripts mapping (use this when calling the ingest endpoint):")
    print("{" )
    print(f'  "{audio_resp.id}": "I loved working on a team building a mobile app that helped people track habits."')
    print("}")

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
