from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.v1.auth import get_current_user
from app.db import client
from app.core.config import settings
from app.services.llm import get_llm_and_embeddings
from app.services.pipeline import QdrantMemoryStore, QDRANT_COLLECTION_NAME
from qdrant_client import QdrantClient
from urllib.parse import urlparse
from langchain_core.prompts import ChatPromptTemplate
import asyncio

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    top_k: int = 5


class ChatResponse(BaseModel):
    response: str
    sources: List[dict]


@router.post("/", response_model=ChatResponse)
async def chat_with_user(req: ChatRequest, current_user=Depends(get_current_user)):
    user_id = current_user.id

    # Ensure DB connected
    try:
        await client.connect()
    except Exception:
        pass

    # Validate vector config
    if not settings.VECTOR_DB_URL:
        raise HTTPException(status_code=500, detail="VECTOR_DB_URL is required in configuration")
    if not settings.VECTOR_SIZE:
        raise HTTPException(status_code=500, detail="VECTOR_SIZE is required in configuration")

    parsed = urlparse(settings.VECTOR_DB_URL)
    if not parsed.hostname or not parsed.port:
        raise HTTPException(status_code=500, detail="VECTOR_DB_URL must include host and port")

    qdrant = QdrantClient(host=parsed.hostname, port=parsed.port)

    # Prepare LLM and embedder
    llm, embedder = get_llm_and_embeddings()

    memory_store = QdrantMemoryStore(
        client=qdrant,
        collection_name=QDRANT_COLLECTION_NAME,
        embedder=embedder,
        vector_size=settings.VECTOR_SIZE,
    )

    # Query RAG
    try:
        results = await memory_store.query_memories(user_id=user_id, query=req.message, limit=req.top_k)
        print(f"RAG query returned {len(results)} results")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

    # Build context from retrieved memories
    memories_text_parts = []
    sources = []
    for r in results:
        payload = r.get("payload", {}) or {}
        preview = payload.get("content_preview") or payload.get("transcript") or ""
        facts = payload.get("facts", [])
        preferences = payload.get("preferences", [])
        signals = payload.get("signals", {})
        part = f"- Preview: {preview}\n  Facts: {facts}\n  Preferences: {preferences}\n  Signals: {signals}"
        memories_text_parts.append(part)
        sources.append({"id": r.get("id"), "score": r.get("score"), "payload": payload})

    memories_text = "\n\n".join(memories_text_parts) or "(no relevant memories found)"

    print("Memories used for RAG context:")
    print(memories_text)
    # Create prompt instructing the model to respond as the user's digital twin
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are an assistant that impersonates a specific user based on their memories. "
                    "Use the provided memories to answer in the user's voice, adopting the user's tone and preferred words. "
                    "When using memories, cite them if helpful. Do not invent private facts."
                ),
            ),
            (
                "human",
                (
                    "User identity id: {user_id}\n"
                    "Relevant memories:\n{memories}\n\n"
                    "Question: {question}\n\n"
                    "Answer as the user, in 1-3 short paragraphs."
                ),
            ),
        ]
    )

    chain = prompt | llm

    try:
        raw = await chain.ainvoke({"user_id": str(user_id), "memories": memories_text, "question": req.message})
    except Exception as e:
        msg = str(e).lower()
        if ("quota" in msg) or ("resourceexhausted" in msg) or ("429" in msg):
            # Try fallbacks if configured
            fallbacks = []
            if settings.CHAT_MODEL_FALLBACKS:
                fallbacks = [m.strip() for m in settings.CHAT_MODEL_FALLBACKS.split(",") if m.strip()]
            if not fallbacks:
                fallbacks = ["gemini-mini"]

            raw = None
            for fb in fallbacks:
                try:
                    fb_llm, _ = get_llm_and_embeddings(chat_model=fb)
                    fb_chain = prompt | fb_llm
                    await asyncio.sleep(1)
                    raw = await fb_chain.ainvoke({"user_id": str(user_id), "memories": memories_text, "question": req.message})
                    break
                except Exception:
                    raw = None
                    continue

            if raw is None:
                raise HTTPException(status_code=503, detail="LLM quota exceeded and fallbacks failed")
        else:
            raise HTTPException(status_code=500, detail=str(e))

    # raw may be a ChatResult or string; convert to text
    response_text = raw if isinstance(raw, str) else str(raw)

    return {"response": response_text, "sources": sources}


@router.get("/debug")
async def chat_debug(current_user=Depends(get_current_user)):
    """Dev-only: return number of memories stored for the current user and a small sample of payloads."""
    # Basic env validation
    if not settings.VECTOR_DB_URL:
        raise HTTPException(status_code=500, detail="VECTOR_DB_URL is required in configuration")

    parsed = urlparse(settings.VECTOR_DB_URL)
    if not parsed.hostname or not parsed.port:
        raise HTTPException(status_code=500, detail="VECTOR_DB_URL must include host and port")

    qdrant = QdrantClient(host=parsed.hostname, port=parsed.port)
    _, embedder = get_llm_and_embeddings()
    memory_store = QdrantMemoryStore(
        client=qdrant,
        collection_name=QDRANT_COLLECTION_NAME,
        embedder=embedder,
        vector_size=settings.VECTOR_SIZE or 0,
    )

    # We'll perform a small unfiltered search and count payloads matching this user
    try:
        raw = qdrant.scroll(collection_name=QDRANT_COLLECTION_NAME, limit=200, with_payload=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Qdrant scroll failed: {e}")

    points = getattr(raw, "points", raw) or []
    matched = []
    for p in points:
        # Support both dict and object representations returned by the client
        if isinstance(p, dict):
            payload = p.get("payload") or {}
            pid = p.get("id") or p.get("point_id")
        else:
            payload = getattr(p, "payload", None) or getattr(p, "payload", {})
            pid = getattr(p, "id", None) or getattr(p, "point_id", None)

        if not payload:
            continue

        uid = payload.get("user_id")
        if uid is None:
            uid = payload.get("userId")
        if uid is None:
            continue

        if str(uid) == str(current_user.id):
            matched.append({"id": pid, "payload": payload})

    return {"user_id": current_user.id, "matches": len(matched), "sample": matched[:10]}
