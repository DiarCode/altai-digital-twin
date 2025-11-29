from __future__ import annotations

import uuid
from typing import Any, Dict

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from langchain_google_genai import GoogleGenerativeAIEmbeddings
import logging

logger = logging.getLogger(__name__)
import json

# Collection name used for storing questionnaire memories
QDRANT_COLLECTION_NAME = "user_questionnaire_memories"


class QdrantMemoryStore:
    """
    Simple Qdrant-backed memory store.

    - Uses text embeddings for content.
    - Stores metadata in payload.
    """

    def __init__(
        self,
        client: QdrantClient,
        collection_name: str,
        embedder: GoogleGenerativeAIEmbeddings,
        vector_size: int,
    ) -> None:
        self.client = client
        self.collection_name = collection_name
        self.embedder = embedder
        self.vector_size = vector_size
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """
        Ensure the Qdrant collection exists with the expected vector size.
        Creates it if missing.
        """
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert_memory(
        self,
        user_id: int,
        content: str,
        metadata: Dict[str, Any],
    ) -> str:
        # Embedding call is synchronous in most LangChain embedding impls;
        # it's OK to call it directly inside async for now.
        vector = self.embedder.embed_query(content)
        point_id = str(uuid.uuid4())

        payload = {
            **metadata,
            "user_id": user_id,
            "content_preview": content[:256],
        }

        # Ensure payload is JSON-serializable (convert strange objects to strings)
        try:
            safe_payload = json.loads(json.dumps(payload, default=str))
        except Exception:
            safe_payload = payload

        # Print debug info so it's visible in the uvicorn console during development.
        try:
            print(
                f"Qdrant upsert -> point_id={point_id} user_id={user_id} payload_keys={list(safe_payload.keys())} preview={str(safe_payload.get('content_preview',''))[:200]}"
            )
        except Exception:
            pass

        res = self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=safe_payload,
                )
            ],
        )

        try:
            print(f"Qdrant upsert result: {res}")
        except Exception:
            pass
        return point_id

    async def query_memories(
        self, user_id: int, query: str, limit: int = 5
    ) -> list[Dict[str, Any]]:
        """
        Query the vector store for the most relevant memories to `query`, filtered by `user_id`.

        Returns a list of dicts with keys: `id`, `score`, `payload`.
        """
        # Create embedding (synchronous call on embedder)
        vector = self.embedder.embed_query(query)

        # Attempt a filtered search by `user_id` first. Some Qdrant client
        # payload-matchers can be brittle across versions/types, so if the
        # filtered search fails or returns nothing we fall back to an
        # unfiltered search and filter results in-python by payload.user_id.
        try:
            query_filter = Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            )

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=limit,
                with_payload=True,
                query_filter=query_filter,
            )
        except Exception:
            # If the filtered search failed for any reason, try an unfiltered
            # search and post-filter by payload. This is more tolerant.
            try:
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=vector,
                    limit=limit * 5,
                    with_payload=True,
                )
            except Exception:
                # If even an unfiltered search fails (collection missing, etc.)
                # return empty list to keep upstream code stable.
                return []

            # Post-filter in Python to only include this user's payloads.
            filtered = []
            for r in results:
                payload = getattr(r, "payload", None) or getattr(r, "payload", {})
                if payload and (
                    payload.get("user_id") == user_id
                    or str(payload.get("user_id")) == str(user_id)
                ):
                    filtered.append(r)

            # Limit and assign
            results = filtered[:limit]

        else:
            # If filtered search succeeded but returned no results, also try
            # the unfiltered fallback to handle potential type-mismatch issues.
            if not results:
                try:
                    results = self.client.search(
                        collection_name=self.collection_name,
                        query_vector=vector,
                        limit=limit * 5,
                        with_payload=True,
                    )
                except Exception:
                    return []

                filtered = []
                for r in results:
                    payload = getattr(r, "payload", None) or getattr(r, "payload", {})
                    if payload and (
                        payload.get("user_id") == user_id
                        or str(payload.get("user_id")) == str(user_id)
                    ):
                        filtered.append(r)

                results = filtered[:limit]

        out: list[Dict[str, Any]] = []
        for r in results:
            # r may be a ScoredPoint or similar; be defensive accessing attributes
            rid = getattr(r, "id", None) or getattr(r, "point_id", None) or None
            score = getattr(r, "score", None)
            payload = getattr(r, "payload", None) or getattr(r, "payload", {})

            out.append({"id": rid, "score": score, "payload": payload})

        return out

