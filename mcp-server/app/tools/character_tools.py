from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mcp_server.app.auth import authenticate_mcp_request
from backend.app.models.world import Character

async def tool_get_character(auth_token: str, character_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Retrieve full character dossier, psychological profile, role, and dialogue style."""
    user = await authenticate_mcp_request(auth_token, db)
    
    query = select(Character).where(Character.id == character_id)
    result = await db.execute(query)
    char = result.scalar_one_or_none()
    
    if not char:
        return {"error": f"Character with id '{character_id}' not found."}
        
    return {
        "character_id": char.id,
        "name": char.name,
        "role": char.role,
        "faction": char.faction,
        "backstory": char.backstory,
        "psychological_profile": char.psychological_profile,
        "dialogue_style": char.dialogue_style
    }
