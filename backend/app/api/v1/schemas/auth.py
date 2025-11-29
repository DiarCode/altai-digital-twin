from pydantic import BaseModel, Field
from datetime import date
from ._base import CamelModel


class UserCreate(CamelModel):
    username: str = Field(..., example="jdoe")
    password: str
    gender: str | None = None
    birthdate: date | None = None


class UserLogin(CamelModel):
    username: str
    password: str


class UserOut(CamelModel):
    id: int
    username: str
    gender: str | None
    birthdate: date | None
    created_at: str


class Token(CamelModel):
    access_token: str
    token_type: str = "bearer"
