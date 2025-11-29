r"""Simple Qdrant inspection helper.

Usage (PowerShell):
    $env:VECTOR_DB_URL = 'http://localhost:6333'
    python .\scripts\inspect_qdrant.py --collection user_questionnaire_memories --user 1 --sample 20

This will connect to Qdrant, print collection info and sample points for the given user id.
The script will attempt to load a `.env` file from the project root automatically
if one exists (no extra packages required).
"""
from __future__ import annotations

import os
import argparse
from urllib.parse import urlparse
from qdrant_client import QdrantClient
from pathlib import Path


def main():
    # Try to load a .env file from the repository root (one level above scripts/)
    # This is a small helper so you don't need to export env vars manually for local testing.
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        try:
            with env_path.open("r", encoding="utf-8") as fh:
                for raw in fh:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    # Only set if not already present in environment to allow overrides
                    os.environ.setdefault(key, val)
        except Exception:
            # Non-fatal: proceed without .env if parsing fails
            pass

    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="user_questionnaire_memories")
    parser.add_argument("--user", type=int, required=False)
    parser.add_argument("--sample", type=int, default=10)
    args = parser.parse_args()

    url = os.environ.get("VECTOR_DB_URL")
    if not url:
        raise SystemExit("Please set VECTOR_DB_URL environment variable (e.g. http://localhost:6333)")

    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port
    if not host or not port:
        raise SystemExit("VECTOR_DB_URL must include host and port")

    client = QdrantClient(host=host, port=port)

    try:
        coll = client.get_collection(args.collection)
        print(f"Collection '{args.collection}': {coll}")
    except Exception as e:
        print(f"Failed to get collection info: {e}")

    print("Scrolling sample points...")
    try:
        # scroll returns points; we request payloads
        resp = client.scroll(collection_name=args.collection, limit=args.sample, with_payload=True)
    except Exception as e:
        print(f"Scroll failed: {e}")
        return

    points = resp.points if hasattr(resp, "points") else resp
    for p in points:
        # Support both object-like and dict-like point representations
        if isinstance(p, dict):
            pid = p.get("id") or p.get("point_id")
            payload = p.get("payload") or {}
        else:
            pid = getattr(p, "id", None) or getattr(p, "point_id", None)
            payload = getattr(p, "payload", None) or getattr(p, "payload", {})

        print("---")
        print(f"id: {pid}")
        try:
            print(f"payload keys: {list(payload.keys())}")
        except Exception:
            print(f"payload keys: (unreadable) {type(payload)}")

        if args.user is not None:
            print(f"user_id in payload: {payload.get('user_id')!r} (type: {type(payload.get('user_id'))})")
        else:
            print(f"user_id: {payload.get('user_id')!r}")

        # print a short preview
        cp = payload.get("content_preview") or payload.get("transcript")
        if cp:
            print(f"preview: {str(cp)[:200]}")


if __name__ == "__main__":
    main()
