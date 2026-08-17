from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.memory import Memory
from backend.app.models.multiverse import RealityBranch

async def resource_read_memories(branch_id: str, db: AsyncSession) -> str:
    """Resource provider for kshan://memories/{branch_id}."""
    branch_query = select(RealityBranch).where(RealityBranch.id == branch_id)
    branch_res = await db.execute(branch_query)
    branch = branch_res.scalar_one_or_none()

    if not branch:
        return f"# Memory branch '{branch_id}' not found."

    query = select(Memory).where(
        Memory.branch_id == branch.id
    ).order_by(Memory.created_at.desc())

    result = await db.execute(query)
    memories = result.scalars().all()

    lines = [f"# KSHAN MEMORY VAULT: {branch.branch_name}"]
    for m in memories:
        lines.append(f"\n### {m.title} ({m.emotional_tone.upper()} | Clarity {m.clarity_level})")
        lines.append(m.content)

    return "\n".join(lines)
