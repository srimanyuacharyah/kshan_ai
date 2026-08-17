from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from mcp_server.app.auth import authenticate_mcp_request, verify_branch_ownership
from backend.app.models.world import World, Location
from backend.app.models.scenario import Scenario
from backend.app.models.multiverse import RealityBranch
from backend.app.models.timeline import TimelineNode

async def tool_get_current_world(auth_token: str, scenario_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Retrieve world lore, physics rules, and factions for a scenario."""
    user = await authenticate_mcp_request(auth_token, db)
    
    query = select(World).where(World.scenario_id == scenario_id).options(selectinload(World.locations), selectinload(World.characters))
    result = await db.execute(query)
    world = result.scalar_one_or_none()
    
    if not world:
        return {"error": f"World for scenario '{scenario_id}' not found."}
        
    return {
        "world_id": world.id,
        "name": world.name,
        "cosmos_type": world.cosmos_type,
        "laws_of_physics": world.laws_of_physics,
        "factions_overview": world.factions_overview,
        "lore_chronicle": world.lore_chronicle,
        "total_locations": len(world.locations),
        "total_characters": len(world.characters)
    }

async def tool_get_location(auth_token: str, location_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Retrieve detailed description and danger rating of a specific realm location."""
    user = await authenticate_mcp_request(auth_token, db)
    
    query = select(Location).where(Location.id == location_id)
    result = await db.execute(query)
    location = result.scalar_one_or_none()
    
    if not location:
        return {"error": f"Location '{location_id}' not found."}
        
    return {
        "location_id": location.id,
        "name": location.name,
        "realm_zone": location.realm_zone,
        "description": location.description,
        "atmosphere": location.atmosphere,
        "danger_rating": location.danger_rating
    }

async def tool_get_world_events(auth_token: str, branch_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Retrieve historical timeline events for a user's branch."""
    user = await authenticate_mcp_request(auth_token, db)
    await verify_branch_ownership(db, user.user_id, branch_id)
    
    query = select(TimelineNode).where(
        TimelineNode.branch_id == branch_id,
        TimelineNode.user_id == user.user_id
    ).order_by(TimelineNode.depth_level.asc())
    
    result = await db.execute(query)
    nodes = result.scalars().all()
    
    return {
        "branch_id": branch_id,
        "events_count": len(nodes),
        "events": [
            {
                "node_id": n.id,
                "era_year": n.era_year,
                "depth_level": n.depth_level,
                "narrative_summary": n.story_text[:120] + "...",
                "sensory_cue": n.sensory_cue,
                "butterfly_impact": n.butterfly_impact
            }
            for n in nodes
        ]
    }
