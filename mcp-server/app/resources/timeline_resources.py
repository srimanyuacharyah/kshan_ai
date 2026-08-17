from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.timeline import TimelineNode
from backend.app.models.multiverse import RealityBranch

async def resource_read_timeline(branch_id: str, db: AsyncSession) -> str:
    """Resource provider for kshan://timeline/{branch_id}."""
    branch_query = select(RealityBranch).where(RealityBranch.id == branch_id)
    branch_res = await db.execute(branch_query)
    branch = branch_res.scalar_one_or_none()

    if not branch:
        return f"# Timeline branch '{branch_id}' not found."

    query = select(TimelineNode).where(
        TimelineNode.branch_id == branch.id
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
