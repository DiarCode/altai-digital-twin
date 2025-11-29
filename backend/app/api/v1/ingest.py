from __future__ import annotations

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Depends

from app.db import client
from app.services.ingest import ingest_user_responses_to_memory
from app.services.pipeline import get_llm_and_embeddings, QdrantMemoryStore, QDRANT_COLLECTION_NAME
from qdrant_client import QdrantClient
from app.api.v1.auth import get_current_user
from app.core.config import settings
from urllib.parse import urlparse

router = APIRouter()


@router.post("/")
async def start_ingest(current_user=Depends(get_current_user)):
    """
    Trigger ingestion of all questionnaire responses for `user_id` into the vector memory.

    Accepts optional `transcripts` mapping (response_id -> transcript) to skip STT
    and optional Qdrant connection params.
    """
    # Use the authenticated user as the source of data
    user_id = current_user.id

    # Ensure DB is connected (startup should have connected but be defensive)
    try:
        await client.connect()
    except Exception:
        # if connection already established, Prisma wrapper prevents re-connect issues
        pass

    # Prepare LLM and embedder (factory reads settings.LLM_API_KEY)
    llm, embedder = get_llm_and_embeddings()

    # Vector DB config must be provided via environment/config.
    # Do not fall back to hard-coded defaults — fail fast if missing.
    if not settings.VECTOR_DB_URL:
        raise HTTPException(status_code=500, detail="VECTOR_DB_URL is required in configuration")

    parsed = urlparse(settings.VECTOR_DB_URL)
    if not parsed.hostname or not parsed.port:
        raise HTTPException(
            status_code=500,
            detail=(
                "VECTOR_DB_URL must include host and port, e.g. 'http://host:6333'"
            ),
        )

    qdrant_host = parsed.hostname
    qdrant_port = parsed.port

    if not settings.VECTOR_SIZE:
        raise HTTPException(status_code=500, detail="VECTOR_SIZE is required in configuration")

    vector_size = settings.VECTOR_SIZE

    # Create Qdrant client and memory store
    try:
        qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
        memory_store = QdrantMemoryStore(
            client=qdrant,
            collection_name=QDRANT_COLLECTION_NAME,
            embedder=embedder,
            vector_size=vector_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize vector store: {e}")

    # Run ingestion
    try:
        # We intentionally do NOT require the caller to pass transcripts because
        # we will prefer the `transcription` column from DB. Callers cannot
        # override transcriptions here; supply them to the DB if needed.
        result = await ingest_user_responses_to_memory(
            db=client,
            user_id=user_id,
            memory_store=memory_store,
            llm=llm,
        )
    except NotImplementedError as e:
        # transcribe_audio is not implemented by default; propagate helpful message
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "ingestion completed",
        "audio_items": len(result.get("audio_items", [])),
        "likert_items": len(result.get("likert_items", [])),
    }
