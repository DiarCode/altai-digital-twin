from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "altai-digital-twin"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/altai"
    VECTOR_DB_URL: str = ""
    JWT_SECRET_KEY: str = "super-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day by default
    # Cookie-based auth settings
    CLIENT_URL: str = "http://localhost:3000"
    COOKIE_NAME: str = "access_token"
    COOKIE_DOMAIN: str | None = None
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"
    COOKIE_EXPIRE_MINUTES: int = 60 * 24
    # Add other settings and secrets here

    class Config:
        env_file = ".env"

settings = Settings()
