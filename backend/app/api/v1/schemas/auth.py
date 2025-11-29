from pydantic import BaseModel, Field
from datetime import date


class UserCreate(BaseModel):
    username: str = Field(..., example="jdoe")
    password: str
    gender: str | None
    birthdate: date | None


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    gender: str | None
    birthdate: date | None
    createdAt: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
