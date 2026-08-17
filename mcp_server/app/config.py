from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class MCPSettings(BaseSettings):
    SERVER_NAME: str = "KSHAN Multiverse Context Server"
    SERVER_DESCRIPTION: str = "Provides secure, user-scoped access to KSHAN multiverse timelines, worlds, characters, memories, decisions and narrative context."
    VERSION: str = "1.0.0"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/kshan_db",
        description="Async PostgreSQL connection string"
    )
    
    # Security
    JWT_SECRET: str = "kshan_multiverse_super_secret_jwt_key_2026"
    JWT_ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

mcp_settings = MCPSettings()
