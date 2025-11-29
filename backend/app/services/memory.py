from __future__ import annotations

from typing import Any, Dict, Protocol


class MemoryStore(Protocol):
    async def upsert_memory(
        self,
        user_id: int,
        content: str,
        metadata: Dict[str, Any],
    ) -> str:
        """
        Store a memory item (content + metadata) in the underlying backend.

        Returns an external memory id (e.g., Qdrant point ID).
        """
        ...
