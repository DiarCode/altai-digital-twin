from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
import jwt
from app.core.config import settings
from app.db import client
from fastapi import HTTPException


class CookieAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract token from cookie
        token = request.cookies.get(settings.COOKIE_NAME)
        if token:
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                user_id = payload.get("user_id")
                if user_id is not None:
                    user = await client.user.find_unique(where={"id": int(user_id)})
                    # attach user to request state
                    request.state.user = user
            except jwt.ExpiredSignatureError:
                # token expired, ignore (user remains None)
                request.state.user = None
            except jwt.PyJWTError:
                request.state.user = None
        else:
            request.state.user = None

        response = await call_next(request)
        return response
