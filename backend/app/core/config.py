from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "KSHAN"
    TAGLINE: str = "One Moment. Infinite Lives. Your choices create worlds that never existed."
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database & Vector Storage
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/kshan_db",
        description="Async PostgreSQL connection string"
    )
    DATABASE_URL_SYNC: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/kshan_db",
        description="Sync PostgreSQL connection string for Alembic"
    )

    # Configurable Embedding Dimension (default 768 for Gemini text-embedding-004)
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSION: int = Field(
        default=768,
        description="Configurable vector dimension for pgvector embeddings"
    )

    # Authentication & JWT
    JWT_SECRET: str = "kshan_multiverse_super_secret_jwt_key_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours

    # AI Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    DEMO_MODE: bool = True

    # Model Context Protocol (MCP)
    MCP_SERVER_URL: str = "http://localhost:8001"
    MCP_TRANSPORT: str = "stdio" # "stdio" or "sse"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
