from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mcp_server.app.auth import authenticate_mcp_request, verify_branch_ownership
from backend.app.models.timeline import TimelineNode

async def resource_read_timeline(auth_token: str, branch_id: str, db: AsyncSession) -> str:
    """Resource provider for kshan://timeline/{branch_id}."""
    user = await authenticate_mcp_request(auth_token, db)
    branch = await verify_branch_ownership(db, user.user_id, branch_id)

    query = select(TimelineNode).where(
        TimelineNode.branch_id == branch.id,
        TimelineNode.user_id == user.user_id
    ).order_by(TimelineNode.depth_level.asc())

    result = await db.execute(query)
    nodes = result.scalars().all()

    lines = [f"# KSHAN TIMELINE CHRONICLE: {branch.branch_name} ({branch.branch_code})"]
    for n in nodes:
        lines.append(f"\n## [{n.era_year}] Depth {n.depth_level}")
        lines.append(n.story_text)
        if n.sensory_cue:
            lines.append(f"*Sensory Ambiance: {n.sensory_cue}*")

    return "\n".join(lines)
