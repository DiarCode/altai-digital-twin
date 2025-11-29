from __future__ import annotations

import os
from app.core.config import settings

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

# Default model names (can be overridden via settings)
DEFAULT_CHAT_MODEL = "gemini-3-pro-preview"
DEFAULT_EMBEDDING_MODEL = "text-embedding-004"


def get_llm_and_embeddings(
    chat_model: str | None = None, embedding_model: str | None = None
) -> tuple[ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings]:
    """
    Returns a configured chat model and embedding model.

    Requires GOOGLE_API_KEY (and related config) in the environment.
    """
    # Prefer the LLM API key from our config. For compatibility with the
    # underlying provider library we export it to the expected env var
    # name `GOOGLE_API_KEY` here so callers only need to set `settings.LLM_API_KEY`.
    if settings.LLM_API_KEY:
        os.environ.setdefault("GOOGLE_API_KEY", settings.LLM_API_KEY)

    # Allow explicit overrides in the call; otherwise prefer settings or defaults
    chat_model = (
        chat_model
        or getattr(settings, "CHAT_MODEL", None)
        or DEFAULT_CHAT_MODEL
    )
    embedding_model = (
        embedding_model
        or getattr(settings, "EMBEDDING_MODEL", None)
        or DEFAULT_EMBEDDING_MODEL
    )

    llm = ChatGoogleGenerativeAI(
        model=chat_model,
        temperature=0.3,
    )
    embedder = GoogleGenerativeAIEmbeddings(
        model=embedding_model,
    )
    return llm, embedder