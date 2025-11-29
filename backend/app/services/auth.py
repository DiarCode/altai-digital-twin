from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional
from datetime import datetime as _dt, time as _time
from app.core.utils.dates import date_to_datetime_min
from app.api.v1.schemas.auth import UserCreate, UserLogin
from app.core.utils import hash_password, verify_password, create_access_token, decode_access_token
from app.core.config import settings
from app.db import client


# password and jwt helpers have been moved to `app.core.utils`


async def create_user(user_in: UserCreate):
    hashed = hash_password(user_in.password)
    # convert birthdate (date) to datetime to satisfy prisma DateTime if needed
    birthdate_val = None
    if user_in.birthdate:
        birthdate_val = date_to_datetime_min(user_in.birthdate)
    user = await client.user.create(data={
        "username": user_in.username,
        "password": hashed,
        "gender": user_in.gender or "",
        "birthdate": birthdate_val,
    })
    return user


async def register_user(user_in: UserCreate):
    # Check for existing username
    existing = await client.user.find_unique(where={"username": user_in.username})
    if existing:
        raise ValueError("Username already registered")
    return await create_user(user_in)


async def authenticate_user(login_in: UserLogin):
    user = await client.user.find_unique(where={"username": login_in.username})
    if not user:
        return None
    if not verify_password(login_in.password, user.password):
        return None
    return user


def create_token_for_user(user, expires_delta: Optional[timedelta] = None):
    return create_access_token({"user_id": int(user.id)}, expires_delta=expires_delta)


async def get_user_from_token(token: Optional[str]):
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            return None
        user = await client.user.find_unique(where={"id": int(user_id)})
        return user
    except Exception:
        return None


async def get_user_from_request(request):
    # Middleware may have set user
    user = getattr(request.state, "user", None)
    if user:
        return user
    # fallback to token cookie
    token = request.cookies.get(settings.COOKIE_NAME)
    return await get_user_from_token(token)
