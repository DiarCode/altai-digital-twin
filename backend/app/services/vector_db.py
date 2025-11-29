from __future__ import annotations

import uuid
from typing import Any, Dict

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from langchain_google_genai import GoogleGenerativeAIEmbeddings

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

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        return point_id

