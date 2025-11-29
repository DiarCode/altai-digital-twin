from __future__ import annotations
import bcrypt
from app.core.config import settings


def hash_password(plain_password: str) -> str:
    pepper = settings.PASSWORD_PEPPER or ""
    to_hash = (plain_password + pepper).encode("utf-8")
    hashed = bcrypt.hashpw(to_hash, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pepper = settings.PASSWORD_PEPPER or ""
    to_verify = (plain_password + pepper).encode("utf-8")
    return bcrypt.checkpw(to_verify, hashed_password.encode("utf-8"))
