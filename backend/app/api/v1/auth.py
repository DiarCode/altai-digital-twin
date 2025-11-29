from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from datetime import timedelta
from app.api.v1.schemas.auth import UserCreate, UserOut, UserLogin, Token
from app.services import auth as auth_service
from app.core.config import settings
from app.db import client

router = APIRouter()
from app.core.config import settings


@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate):
    try:
        user = await auth_service.register_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Use model_validate to handle alias mapping (snake_case -> camelCase) automatically
    return UserOut.model_validate(user)


@router.post("/login")
async def login(form_data: UserLogin, response: Response):
    user = await auth_service.authenticate_user(form_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = auth_service.create_token_for_user(user, expires_delta=access_token_expires)
    # set cookie
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=int(settings.COOKIE_EXPIRE_MINUTES * 60),
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    return {"message": "ok"}


async def get_current_user(request: Request):
    user = await auth_service.get_user_from_request(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.get("/me", response_model=UserOut)
async def me(current_user=Depends(get_current_user)):
    return UserOut.model_validate(current_user)


@router.post("/logout")
async def logout(response: Response):
    # Clear the cookie
    response.delete_cookie(key=settings.COOKIE_NAME, path="/", domain=settings.COOKIE_DOMAIN)
    return {"message": "logged out"}
