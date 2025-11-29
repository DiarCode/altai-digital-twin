from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "altai-digital-twin"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/altai"
    VECTOR_DB_URL: str = ""
    # Add other settings and secrets here

    class Config:
        env_file = ".env"

settings = Settings()
