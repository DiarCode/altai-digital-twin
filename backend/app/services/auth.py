from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt
from app.core.config import settings
from app.db import client


def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def create_user(username: str, password: str, gender: str, birthdate: str):
    hashed = hash_password(password)
    user = await client.user.create(data={
        "username": username,
        "password": hashed,
        "gender": gender,
        "birthdate": birthdate,
    })
    return user


async def authenticate_user(username: str, password: str):
    user = await client.user.find_unique(where={"username": username})
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
