from __future__ import annotations

import asyncio
from datetime import datetime
from prisma import Prisma


async def main() -> None:
    db = Prisma()
    await db.connect()

    print("Seeding test data with transcriptions...")

    # Create or get two test users
    users = []
    for username in ("test_user_1", "test_user_2"):
        user = await db.user.find_unique(where={"username": username})
        if not user:
            user = await db.user.create(
                data={
                    "username": username,
                    # Set a placeholder password. Replace with a real password hash
                    # in the DB if you want to authenticate via cookie auth later.
                    "password": "password-placeholder",
                    "gender": "other",
                    "birthdate": datetime(1990, 1, 1),
                }
            )
        users.append(user)

    test_user = users[0]

    # Create questions if missing
    q_defs = [
        ("How do you like working in teams?", "LIKERT"),
        ("Tell me about a project you loved working on.", "AUDIO"),
        ("What are your main personal values?", "AUDIO"),
    ]

    questions = []
    for text, qtype in q_defs:
        q = await db.questionnairequestion.find_first(where={"text": text})
        if not q:
            q = await db.questionnairequestion.create(data={"text": text, "type": qtype})
        questions.append(q)

    # Create responses for the test user
    created_responses = []

    # LIKERT response
    likert_q = next(q for q in questions if q.type == "LIKERT")
    likert_resp = await db.questionnaireresponse.create(
        data={
            "userId": test_user.id,
            "questionId": likert_q.id,
            "likertValue": 4,
        }
    )
    created_responses.append(likert_resp)

    # AUDIO responses (with transcription filled)
    audio_questions = [q for q in questions if q.type == "AUDIO"]
    sample_transcripts = [
        "I loved working on a cross-platform mobile app that helped users build habits. I was the lead on UX and coordinated with designers.",
        "My core values are autonomy, learning, and helping others. I prioritize clarity and small iterative improvements.",
    ]

    for q, transcript in zip(audio_questions, sample_transcripts):
        resp = await db.questionnaireresponse.create(
            data={
                "userId": test_user.id,
                "questionId": q.id,
                "audioPath": f"audio/{test_user.username}_{q.id}.wav",
                "transcription": transcript,
            }
        )
        created_responses.append(resp)

    print("Created test user:")
    print(f"  username: {test_user.username}")
    print(f"  id: {test_user.id}")
    print("\nResponses created:")
    for resp in created_responses:
        # Resolve question type from DB (relation may not be loaded on the response object)
        q = await db.questionnairequestion.find_unique(where={"id": resp.questionId})
        q_type = q.type if q else "unknown"
        print(f"  id: {resp.id}  questionId: {resp.questionId}  type: {q_type}")

    print("\nSample transcripts mapping for ingest (response_id -> transcript):")
    print("{")
    for resp in created_responses:
        # Only print transcripts for audio responses
        if getattr(resp, "transcription", None):
            print(f'  "{resp.id}": "{resp.transcription}"')
    print("}")

    print("\nNote: Passwords are placeholders. If you need to authenticate via cookie, replace the password hash in the DB for the user with a valid hash.")

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
