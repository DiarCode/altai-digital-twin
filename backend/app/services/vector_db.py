from typing import Any, Optional
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance
from app.core.config import settings


class VectorDB:
    """
    Qdrant-backed vector DB wrapper
    Expects vectors in format: [{"id": <int|str>, "vector": [float], "payload": {...}}]
    """

    def __init__(self, url: Optional[str] = None, collection_name: str = "altai_vectors", vector_size: int = 1536):
        self.url = url or settings.VECTOR_DB_URL
        self.collection_name = collection_name
        self.vector_size = vector_size
        # Qdrant client is synchronous; use to_thread when in async code
        self.client = QdrantClient(url=self.url) if self.url else QdrantClient()
        # Ensure collection exists
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # create collection with default cosine distance
            self.client.recreate_collection(collection_name=self.collection_name, vectors={"size": self.vector_size, "distance": Distance.COSINE})

    async def upsert_vectors(self, vectors: list[dict]):
        points = [PointStruct(id=v["id"], vector=v["vector"], payload=v.get("payload")) for v in vectors]
        await asyncio.to_thread(self.client.upsert, collection_name=self.collection_name, points=points)

    async def query(self, query_vector: list[float], top_k: int = 10) -> list[dict]:
        results = await asyncio.to_thread(self.client.search, collection_name=self.collection_name, query_vector=query_vector, limit=top_k)
        # Convert results to simple dicts
        out = []
        for r in results:
            item = {"id": r.id, "score": r.score, "payload": r.payload}
            out.append(item)
        return out

