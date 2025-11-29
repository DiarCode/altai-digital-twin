import asyncio
from prisma import Prisma
from prisma.enums import QuestionnaireQuestionType

async def main() -> None:
    prisma = Prisma()
    await prisma.connect()

    questions = [
        (0, "When you make a mistake, what do you usually do?"),
        (1, "Do you prefer working alone or with others?"),
        (2, "What frustrates you the most?"),
        (3, "How do you spend your free time?"),
        (4, "What's your biggest strength?"),
    ]

    print("Seeding questions...")
    for order, text in questions:
        await prisma.questionnairequestion.upsert(
            where={
                "order": order
            },
            data={
                "create": {
                    "text": text,
                    "type": QuestionnaireQuestionType.AUDIO,
                    "order": order
                },
                "update": {
                    "text": text,
                    "type": QuestionnaireQuestionType.AUDIO
                }
            }
        )
        print(f"Processed question {order}: {text}")

    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
