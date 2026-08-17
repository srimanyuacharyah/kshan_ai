import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.core.database import get_db
from backend.app.models.base import Base
import backend.app.models  # Ensure all model tables are registered in Base.metadata
from backend.app.core.security import create_access_token, get_password_hash
from backend.app.models.user import User, UserProfile
from mcp_server.app.db import set_mcp_session_factory

# SQLite in-memory async engine with shared cache for fast, isolated unit and integration testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///file:test_kshan_db?mode=memory&cache=shared&uri=true"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Connect MCP tools to test engine
set_mcp_session_factory(TestingSessionLocal)

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database schema for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
        
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """FastAPI test client with database override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def test_user_a(db_session: AsyncSession) -> User:
    """Create test User A."""
    user = User(
        email="voyager.a@kshan.ai",
        username="voyager_alpha",
        hashed_password=get_password_hash("Password123!"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.flush()
    
    profile = UserProfile(
        user_id=user.id,
        display_name="Voyager Alpha",
        bio="First alternate reality traveler",
        sound_enabled=True,
        preferences={"theme": "obsidian"}
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function")
async def test_user_b(db_session: AsyncSession) -> User:
    """Create test User B."""
    user = User(
        email="voyager.b@kshan.ai",
        username="voyager_beta",
        hashed_password=get_password_hash("Password123!"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.flush()
    
    profile = UserProfile(
        user_id=user.id,
        display_name="Voyager Beta",
        bio="Second alternate reality traveler",
        sound_enabled=False,
        preferences={"theme": "starlight"}
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers_user_a(test_user_a: User) -> dict:
    """Bearer JWT header for User A."""
    token = create_access_token(test_user_a.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_user_b(test_user_b: User) -> dict:
    """Bearer JWT header for User B."""
    token = create_access_token(test_user_b.id)
    return {"Authorization": f"Bearer {token}"}
