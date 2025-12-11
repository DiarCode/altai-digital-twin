from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "altai-digital-twin"
    DEBUG: bool = True
    SERVER_PORT: int = 8080
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/altai"
    VECTOR_DB_URL: str | None = None
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
    # Security: optional pepper for password hashing
    PASSWORD_PEPPER: str | None = None

    # LLM / Avatar / Interview service endpoints and credentials
    LLM_API_URL: str | None = None
    LLM_API_KEY: str | None = None
    AVATAR_API_URL: str | None = None
    AVATAR_API_KEY: str | None = None
    ELEVENLABS_API_KEY: str | None = None
    # Model configuration (override defaults). CHAT_MODEL_FALLBACKS is a
    # comma-separated list of model names to try when the primary model
    # hits quota or other model-specific errors.
    CHAT_MODEL: str | None = None
    EMBEDDING_MODEL: str | None = None
    CHAT_MODEL_FALLBACKS: str | None = None

    # S3 Settings
    S3_BUCKET_NAME: str = "altai-digital-twin-audio"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"

    # MinIO / .env compatibility
    S3_ENDPOINT: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_REGION: str | None = None

    # Add other settings and secrets here
    # Qdrant / vector DB settings
    VECTOR_SIZE: int | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
