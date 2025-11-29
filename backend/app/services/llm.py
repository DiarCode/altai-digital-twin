from __future__ import annotations

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

# Models configurable here
GEMINI_CHAT_MODEL = "gemini-3-pro-preview"
GEMINI_EMBEDDING_MODEL = "text-embedding-004"


def get_llm_and_embeddings() -> tuple[ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings]:
    """
    Returns a configured chat model and embedding model.

    Requires GOOGLE_API_KEY (and related config) in the environment.
    """
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_CHAT_MODEL,
        temperature=0.3,
    )
    embedder = GoogleGenerativeAIEmbeddings(
        model=GEMINI_EMBEDDING_MODEL,
    )
    return llm, embedder