from typing import Optional
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mcp_server.app.config import mcp_settings
from backend.app.models.user import User
from backend.app.models.multiverse import RealityBranch
from backend.app.models.scenario import FutureProfile

class MCPAuthError(Exception):
    """Raised when an MCP request fails authentication or authorization."""
    pass

class AuthenticatedUserContext:
    def __init__(self, user_id: str, email: str, username: str):
        self.user_id = user_id
        self.email = email
        self.username = username

async def authenticate_mcp_request(auth_token: str, db: AsyncSession) -> AuthenticatedUserContext:
    """
    Validate the caller's JWT auth token and return the verified user identity.
    Raises MCPAuthError if token is missing, invalid, expired, or user is inactive.
    """
    if not auth_token or not auth_token.strip():
        raise MCPAuthError("Authentication required: Missing or empty auth_token.")

    try:
        token_clean = auth_token.replace("Bearer ", "").strip()
        payload = jwt.decode(
            token_clean,
            mcp_settings.JWT_SECRET,
            algorithms=[mcp_settings.JWT_ALGORITHM]
        )
    except JWTError as e:
        raise MCPAuthError(f"Invalid or expired auth_token: {str(e)}")

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise MCPAuthError("Auth token missing subject identifier (user_id).")

    # Verify user exists in DB and is active
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise MCPAuthError(f"User with id '{user_id}' not found.")
    if not user.is_active:
        raise MCPAuthError(f"User account '{user.username}' is deactivated.")

    return AuthenticatedUserContext(
        user_id=user.id,
        email=user.email,
        username=user.username
    )

async def verify_branch_ownership(db: AsyncSession, user_id: str, branch_id: str) -> RealityBranch:
    """Verify that the given branch_id belongs strictly to the authenticated user."""
    query = select(RealityBranch).where(
        RealityBranch.id == branch_id,
        RealityBranch.user_id == user_id
    )
    result = await db.execute(query)
    branch = result.scalar_one_or_none()
    if not branch:
        raise MCPAuthError(
            f"Unauthorized: Reality branch '{branch_id}' does not exist or does not belong to the authenticated user."
        )
    return branch
