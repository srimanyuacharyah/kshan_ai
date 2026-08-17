from typing import AsyncGenerator, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import AsyncSessionLocal

_session_factory: Callable[[], AsyncSession] = AsyncSessionLocal

def set_mcp_session_factory(factory: Callable[[], AsyncSession]):
    """Allow overriding session factory during testing."""
    global _session_factory
    _session_factory = factory

async def get_mcp_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency / context provider for database sessions in MCP server."""
    global _session_factory
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
