from __future__ import annotations

import json
from typing import Any, Dict, Optional

from prisma import Prisma
from qdrant_client import QdrantClient

from .ingest import ingest_user_responses_to_memory
from .llm import get_llm_and_embeddings
from .vector_db import QdrantMemoryStore, QDRANT_COLLECTION_NAME


async def build_personality_portrait_for_user(
    db: Prisma,
    user_id: int,
    memory_store,
    llm,
) -> Dict[str, Any]:
    """
    High-level orchestration for building a personality portrait:

    - Ensures all questionnaire responses for the user are ingested into the memory store.
    - Produces structured audio_items and likert_items.
    - Calls summarization to get a final persona JSON.

    Returns:
        persona: Dict[str, Any]
    """
    items = await ingest_user_responses_to_memory(
        db=db,
        user_id=user_id,
        memory_store=memory_store,
        llm=llm,
    )

    audio_items = items["audio_items"]
    likert_items = items["likert_items"]

    # Import summarize_user_themes lazily to avoid import cycles
    from .summarization import summarize_user_themes

    persona = await summarize_user_themes(
        llm=llm,
        audio_items=audio_items,
        likert_items=likert_items,
    )

    # Optional: upsert the persona summary itself as a memory
    content = (
        f"Persona core identity: {persona.get('core_identity', '')}\n\n"
        f"Persona summary:\n{persona.get('summary', '')}"
    )
    metadata = {
        "source": "persona_portrait",
        "user_id": user_id,
        "traits": persona.get("traits", {}),
        "values": persona.get("values", []),
        "motivations": persona.get("motivations", []),
        "stressors": persona.get("stressors", []),
        "communication_style": persona.get("communication_style", {}),
    }

    await memory_store.upsert_memory(
        user_id=user_id,
        content=content,
        metadata=metadata,
    )

    return persona


async def example_run(user_id: int) -> None:
    """
    Example orchestration function.

    You can adapt this into a FastAPI endpoint or CLI task.
    """
    db = Prisma()
    await db.connect()

    llm, embedder = get_llm_and_embeddings()
    # IMPORTANT: you'll need to know embedding dimension (e.g., 768 or 1024 depending on the model).
    # For text-embedding-004 at the time of writing, it's 768, but check docs.
    vector_size = 768

    qdrant_client = QdrantClient(host="localhost", port=6333)
    memory_store = QdrantMemoryStore(
        client=qdrant_client,
        collection_name=QDRANT_COLLECTION_NAME,
        embedder=embedder,
        vector_size=vector_size,
    )

    persona = await build_personality_portrait_for_user(
        db=db,
        user_id=user_id,
        memory_store=memory_store,
        llm=llm,
    )

    print(json.dumps(persona, ensure_ascii=False, indent=2))

    await db.disconnect()
