from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
import jwt
from app.core.config import settings
from app.db import client
from app.services import auth as auth_service
from fastapi import HTTPException


class CookieAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract token from cookie
        token = request.cookies.get(settings.COOKIE_NAME)
        if token:
                user = await auth_service.get_user_from_token(token)
                request.state.user = user
        else:
            request.state.user = None

        response = await call_next(request)
        return response
