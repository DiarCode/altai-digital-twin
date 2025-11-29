from __future__ import annotations

import json
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.services.llm import get_llm_and_embeddings
import asyncio


async def summarize_audio_answer(
    llm: ChatGoogleGenerativeAI,
    transcript: str,
    question_text: str,
) -> Dict[str, Any]:
    """
    Summarize a single audio answer into a compact, structured JSON.

    Returns dict with:
        - summary: str
        - facts: List[str]
        - preferences: List[str]
        - signals: Dict[str, float]
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are building a personality model of a real person "
                    "based on their answers to interview questions.\n"
                    "Given a question and a transcript, extract:\n"
                    "- a concise summary (2–3 sentences) of what this answer says about the person\n"
                    "- explicit facts about them (short bullet-style statements)\n"
                    "- preferences/values implied by the answer\n"
                    "- a few trait signals with scores between 0 and 1 "
                    "(for example: introversion, risk_tolerance, conscientiousness).\n\n"
                    "Return ONLY valid JSON with keys: "
                    "summary, facts, preferences, signals.\n"
                    "Example format:\n"
                    "{{\n"
                    "  \"summary\": \"...\",\n"
                    "  \"facts\": [\"...\"],\n"
                    "  \"preferences\": [\"...\"],\n"
                    "  \"signals\": {{\"introversion\": 0.7, \"risk_tolerance\": 0.3}}\n"
                    "}}\n"
                ),
            ),
            (
                "human",
                (
                    "Question: {question_text}\n\n"
                    "Transcript:\n{transcript}\n\n"
                    "Return ONLY JSON, no extra text."
                ),
            ),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    try:
        raw = await chain.ainvoke(
            {"question_text": question_text, "transcript": transcript}
        )
    except Exception as e:
        # Detect quota / resource errors and attempt fallbacks if configured.
        msg = str(e).lower()
        if ("quota" in msg) or ("resourceexhausted" in msg) or ("429" in msg):
            fallbacks = []
            if settings.CHAT_MODEL_FALLBACKS:
                fallbacks = [m.strip() for m in settings.CHAT_MODEL_FALLBACKS.split(",") if m.strip()]

            # Append a small default fallback if none configured
            if not fallbacks:
                fallbacks = ["gemini-mini"]

            # Try fallbacks sequentially (one retry per fallback)
            for fb_model in fallbacks:
                try:
                    # create a fresh llm with the fallback model and retry
                    fb_llm, _ = get_llm_and_embeddings(chat_model=fb_model)
                    fb_chain = prompt | fb_llm | StrOutputParser()
                    # small backoff to avoid immediate throttling
                    await asyncio.sleep(1)
                    raw = await fb_chain.ainvoke({"question_text": question_text, "transcript": transcript})
                    # if successful, break out
                    break
                except Exception:
                    # try next fallback
                    raw = None
                    continue

            if raw is None:
                # All fallbacks failed; re-raise original exception
                raise
        else:
            # Not a quota-like error — propagate
            raise

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Very defensive: if model misbehaves, wrap in a minimal structure.
        data = {
            "summary": raw.strip(),
            "facts": [],
            "preferences": [],
            "signals": {},
        }
    # Basic shape sanity
    data.setdefault("summary", "")
    data.setdefault("facts", [])
    data.setdefault("preferences", [])
    data.setdefault("signals", {})
    return data


async def summarize_user_themes(
    llm: ChatGoogleGenerativeAI,
    audio_items: List[Dict[str, Any]],
    likert_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a high-level personality portrait from all questionnaire data.

    Returns JSON with fields like:
        - core_identity: str
        - summary: str
        - traits: Dict[str, float]
        - values: List[str]
        - motivations: List[str]
        - stressors: List[str]
        - communication_style: { tone: str, do: List[str], dont: List[str] }
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are creating a high-level personality portrait of a real person.\n"
                    "You are given two datasets in JSON:\n"
                    "- audio_items: per-question analysis of open-ended audio answers\n"
                    "- likert_items: numeric answers to Likert questions\n\n"
                    "Use them to infer:\n"
                    "- core identity tagline (one sentence)\n"
                    "- an overall summary (2–3 paragraphs)\n"
                    "- a small set of traits with scores 0–1 (for example: introversion, openness, "
                    "conscientiousness, emotional_stability, agreeableness, risk_tolerance)\n"
                    "- key values (e.g., autonomy, family, achievement, creativity)\n"
                    "- main motivations\n"
                    "- main stressors or fears\n"
                    "- communication style: tone, do (things that work well), dont (things to avoid)\n\n"
                    "Return ONLY valid JSON with keys:\n"
                    "core_identity, summary, traits, values, motivations, stressors, communication_style.\n"
                    "communication_style must be an object with keys: tone, do, dont.\n"
                ),
            ),
            (
                "human",
                (
                    "Here are the audio_items (JSON list):\n"
                    "{audio_items_json}\n\n"
                    "Here are the likert_items (JSON list):\n"
                    "{likert_items_json}\n\n"
                    "Return ONLY JSON, no explanation."
                ),
            ),
        ]
    )

    chain = prompt | llm | StrOutputParser()
    raw = await chain.ainvoke(
        {
            "audio_items_json": json.dumps(audio_items, ensure_ascii=False),
            "likert_items_json": json.dumps(likert_items, ensure_ascii=False),
        }
    )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "core_identity": "",
            "summary": raw.strip(),
            "traits": {},
            "values": [],
            "motivations": [],
            "stressors": [],
            "communication_style": {
                "tone": "",
                "do": [],
                "dont": [],
            },
        }

    # Fill defaults if missing
    data.setdefault("core_identity", "")
    data.setdefault("summary", "")
    data.setdefault("traits", {})
    data.setdefault("values", [])
    data.setdefault("motivations", [])
    data.setdefault("stressors", [])
    data.setdefault(
        "communication_style",
        {"tone": "", "do": [], "dont": []},
    )
    return data
