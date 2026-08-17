from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mcp_server.app.auth import authenticate_mcp_request, verify_branch_ownership
from backend.app.models.memory import Memory

async def resource_read_memories(auth_token: str, branch_id: str, db: AsyncSession) -> str:
    """Resource provider for kshan://memories/{branch_id}."""
    user = await authenticate_mcp_request(auth_token, db)
    branch = await verify_branch_ownership(db, user.user_id, branch_id)

    query = select(Memory).where(
        Memory.branch_id == branch.id,
        Memory.user_id == user.user_id
    ).order_by(Memory.created_at.desc())

    result = await db.execute(query)
    memories = result.scalars().all()

    lines = [f"# KSHAN MEMORY VAULT: {branch.branch_name}"]
    for m in memories:
        lines.append(f"\n### {m.title} ({m.emotional_tone.upper()} | Clarity {m.clarity_level})")
        lines.append(m.content)

    return "\n".join(lines)
