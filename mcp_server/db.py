from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from mcp_server.app.config import mcp_settings

mcp_engine = create_async_engine(
    mcp_settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

MCPAsyncSessionLocal = async_sessionmaker(
    bind=mcp_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_mcp_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency / context provider for database sessions in MCP server."""
    async with MCPAsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
