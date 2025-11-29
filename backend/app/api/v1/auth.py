from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from datetime import timedelta
import jwt
from app.api.v1.schemas.auth import UserCreate, UserOut, UserLogin, Token
from app.services import auth as auth_service
from app.core.config import settings
from app.db import client

router = APIRouter()
from app.core.config import settings


@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate):
    # validate uniqueness via prisma
    existing = await client.user.find_unique(where={"username": user_in.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = await auth_service.create_user(
        username=user_in.username,
        password=user_in.password,
        gender=user_in.gender or "",
        birthdate=user_in.birthdate.isoformat() if user_in.birthdate else None,
    )
    return UserOut(**user.dict())


@router.post("/login")
async def login(form_data: UserLogin, response: Response):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = auth_service.create_access_token({"user_id": user.id}, expires_delta=access_token_expires)
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
    # Middleware should have set request.state.user; if not, try cookie fallback
    user = getattr(request.state, "user", None)
    if user is not None:
        return user
    # Try manual cookie parsing as fallback
    token = request.cookies.get(settings.COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await client.user.find_unique(where={"id": int(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid user")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me", response_model=UserOut)
async def me(current_user=Depends(get_current_user)):
    return UserOut(**current_user.dict())


@router.post("/logout")
async def logout(response: Response):
    # Clear the cookie
    response.delete_cookie(key=settings.COOKIE_NAME, path="/", domain=settings.COOKIE_DOMAIN)
    return {"message": "logged out"}
