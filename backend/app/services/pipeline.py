"""
Lightweight umbrella for the pipeline convenience imports.

The heavy lifting has been split into focused modules:
- `memory.py` (MemoryStore protocol)
- `vector_db.py` (QdrantMemoryStore)
- `llm.py` (LLM + embeddings factory)
- `summarization.py` (LLM-based summarizers)
- `ingest.py` (ingestion pipeline)
- `portrait.py` (persona builder + example runner)

Use the submodules directly for finer-grained imports.
"""

from .memory import MemoryStore
from .vector_db import QDRANT_COLLECTION_NAME, QdrantMemoryStore
from .llm import get_llm_and_embeddings
from .summarization import summarize_audio_answer, summarize_user_themes
from .ingest import ingest_user_responses_to_memory, transcribe_audio
from .portrait import build_personality_portrait_for_user, example_run

__all__ = [
    "MemoryStore",
    "QDRANT_COLLECTION_NAME",
    "QdrantMemoryStore",
    "get_llm_and_embeddings",
    "summarize_audio_answer",
    "summarize_user_themes",
    "ingest_user_responses_to_memory",
    "transcribe_audio",
    "build_personality_portrait_for_user",
    "example_run",
]
