from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from mcp_server.app.auth import authenticate_mcp_request
from backend.app.models.world import World

async def resource_read_world(auth_token: str, scenario_id: str, db: AsyncSession) -> str:
    """Resource provider for kshan://world/{scenario_id}."""
    user = await authenticate_mcp_request(auth_token, db)

    query = select(World).where(World.scenario_id == scenario_id).options(selectinload(World.locations), selectinload(World.characters))
    result = await db.execute(query)
    world = result.scalar_one_or_none()

    if not world:
        return f"# World for scenario {scenario_id} not found."

    lines = [
        f"# WORLD CHRONICLE: {world.name} ({world.cosmos_type})",
        f"**Cosmology**: {world.lore_chronicle}",
        f"**Physics / Metaphysics**: {world.laws_of_physics or 'Standard Multiverse Laws'}",
        "\n## Key Locations:"
    ]
    for loc in world.locations:
        lines.append(f"- **{loc.name}** ({loc.realm_zone}): {loc.description}")

    lines.append("\n## Characters & Figures:")
    for c in world.characters:
        lines.append(f"- **{c.name}** ({c.role} - {c.faction or 'Independent'}): {c.backstory}")

    return "\n".join(lines)
