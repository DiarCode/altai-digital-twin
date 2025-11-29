from __future__ import annotations

from typing import Any, Dict, List, Optional

from prisma import Prisma

from .memory import MemoryStore
from .summarization import summarize_audio_answer


async def transcribe_audio(audio_path: str) -> str:
    """
    Stub for STT integration.

    In production, replace this with your provider (e.g. Whisper, Google STT, etc.).
    For now, this is just a placeholder.
    """
    raise NotImplementedError(
        "transcribe_audio() is not implemented. "
        "Either pass transcripts into ingest_user_responses_to_memory() "
        "or implement STT here."
    )


async def ingest_user_responses_to_memory(
    db: Prisma,
    user_id: int,
    memory_store: MemoryStore,
    llm,
    transcripts_by_response_id: Optional[Dict[str, str]] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Ingests all QuestionnaireResponse rows for a user into the memory store
    and produces structured per-item data for later persona building.

    Steps:
    - Load all responses (with questions).
    - For AUDIO:
        - use provided transcript if available, else call transcribe_audio().
        - summarize with summarize_audio_answer().
        - upsert into memory_store.
    - For LIKERT:
        - build simple content + metadata and upsert as well.

    Returns:
        {
          "audio_items": [...],
          "likert_items": [...]
        }
    """
    transcripts_by_response_id = transcripts_by_response_id or {}

    # Load all responses for the user
    responses = await db.questionnaireresponse.find_many(
        where={"userId": user_id},
        include={"question": True},
        order={"createdAt": "asc"},
    )

    audio_items: List[Dict[str, Any]] = []
    likert_items: List[Dict[str, Any]] = []

    for resp in responses:
        question = resp.question
        q_type = question.type  # "AUDIO" or "LIKERT"

        if q_type == "AUDIO":
            transcript = transcripts_by_response_id.get(resp.id)
            if transcript is None:
                if not resp.audioPath:
                    # No audio and no transcript — skip
                    continue
                # Fallback to STT; will raise NotImplementedError unless you implement it
                transcript = await transcribe_audio(resp.audioPath)

            summary_data = await summarize_audio_answer(
                llm=llm,
                transcript=transcript,
                question_text=question.text,
            )

            audio_item = {
                "response_id": resp.id,
                "question_id": question.id,
                "question_text": question.text,
                "transcript": transcript,
                "summary": summary_data.get("summary", ""),
                "facts": summary_data.get("facts", []),
                "preferences": summary_data.get("preferences", []),
                "signals": summary_data.get("signals", {}),
                "created_at": resp.createdAt.isoformat(),
            }
            audio_items.append(audio_item)

            # Build memory content
            content = (
                f"Question: {question.text}\n"
                f"Type: AUDIO\n\n"
                f"Transcript:\n{transcript}\n\n"
                f"Summary:\n{audio_item['summary']}"
            )

            metadata: Dict[str, Any] = {
                "source": "questionnaire_audio",
                "user_id": user_id,
                "response_id": resp.id,
                "question_id": question.id,
                "question_type": "AUDIO",
                "created_at": resp.createdAt.isoformat(),
                "facts": audio_item["facts"],
                "preferences": audio_item["preferences"],
                "signals": audio_item["signals"],
            }

            await memory_store.upsert_memory(
                user_id=user_id,
                content=content,
                metadata=metadata,
            )

        elif q_type == "LIKERT":
            value = resp.likertValue
            if value is None:
                # Nothing to store
                continue

            # You can change the max scale if needed
            max_scale = 5
            normalized = value / max_scale

            likert_item = {
                "response_id": resp.id,
                "question_id": question.id,
                "question_text": question.text,
                "value": value,
                "normalized_value": normalized,
                "created_at": resp.createdAt.isoformat(),
            }
            likert_items.append(likert_item)

            content = (
                f"Question: {question.text}\n"
                f"Type: LIKERT\n"
                f"Answer (raw): {value}\n"
                f"Answer (normalized 0–1): {normalized:.3f}"
            )

            metadata = {
                "source": "questionnaire_likert",
                "user_id": user_id,
                "response_id": resp.id,
                "question_id": question.id,
                "question_type": "LIKERT",
                "created_at": resp.createdAt.isoformat(),
                "value": value,
                "normalized_value": normalized,
            }

            await memory_store.upsert_memory(
                user_id=user_id,
                content=content,
                metadata=metadata,
            )

        else:
            # Unknown type; ignore gracefully (or log)
            continue

    return {
        "audio_items": audio_items,
        "likert_items": likert_items,
    }
