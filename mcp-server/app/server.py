import asyncio
from typing import Dict, Any, Optional, List
from mcp.server.mcpserver import MCPServer
from mcp_server.app.config import mcp_settings
from mcp_server.app.db import get_mcp_db

from mcp_server.app.tools.world_tools import (
    tool_get_current_world,
    tool_get_location,
    tool_get_world_events
)
from mcp_server.app.tools.timeline_tools import (
    tool_get_timeline,
    tool_get_timeline_node,
    tool_get_branch_state,
    tool_create_timeline_event
)
from mcp_server.app.tools.character_tools import tool_get_character
from mcp_server.app.tools.memory_tools import (
    tool_search_memories,
    tool_create_memory
)
from mcp_server.app.tools.decision_tools import tool_get_recent_decisions
from mcp_server.app.tools.context_tools import tool_get_story_context

from mcp_server.app.resources.world_resources import resource_read_world
from mcp_server.app.resources.timeline_resources import resource_read_timeline
from mcp_server.app.resources.memory_resources import resource_read_memories
from mcp_server.app.prompts.narrative_prompts import prompt_future_you_context

# Initialize Official MCP Server
mcp_server = MCPServer(
    name=mcp_settings.SERVER_NAME,
    instructions=mcp_settings.SERVER_DESCRIPTION,
    version=mcp_settings.VERSION
)

# ----------------- MCP TOOLS -----------------

@mcp_server.tool()
async def get_current_world(auth_token: str, scenario_id: str) -> Dict[str, Any]:
    """Retrieve world lore, physics rules, and factions for a scenario."""
    async for db in get_mcp_db():
        return await tool_get_current_world(auth_token=auth_token, scenario_id=scenario_id, db=db)

@mcp_server.tool()
async def get_location(auth_token: str, location_id: str) -> Dict[str, Any]:
    """Retrieve detailed description and danger rating of a specific realm location."""
    async for db in get_mcp_db():
        return await tool_get_location(auth_token=auth_token, location_id=location_id, db=db)

@mcp_server.tool()
async def get_world_events(auth_token: str, branch_id: str) -> Dict[str, Any]:
    """Retrieve historical timeline events for a user's branch."""
    async for db in get_mcp_db():
        return await tool_get_world_events(auth_token=auth_token, branch_id=branch_id, db=db)

@mcp_server.tool()
async def get_character(auth_token: str, character_id: str) -> Dict[str, Any]:
    """Retrieve character dossier, psychological profile, and dialogue style."""
    async for db in get_mcp_db():
        return await tool_get_character(auth_token=auth_token, character_id=character_id, db=db)

@mcp_server.tool()
async def get_timeline(auth_token: str, branch_id: str, limit: int = 10) -> Dict[str, Any]:
    """Retrieve ordered sequence of timeline nodes for an authenticated branch."""
    async for db in get_mcp_db():
        return await tool_get_timeline(auth_token=auth_token, branch_id=branch_id, limit=limit, db=db)

@mcp_server.tool()
async def get_timeline_node(auth_token: str, node_id: str) -> Dict[str, Any]:
    """Retrieve full details, choices, and consequence forecast for a single timeline node."""
    async for db in get_mcp_db():
        return await tool_get_timeline_node(auth_token=auth_token, node_id=node_id, db=db)

@mcp_server.tool()
async def get_branch_state(auth_token: str, branch_id: str) -> Dict[str, Any]:
    """Retrieve current multiverse metrics (entropy, resonance, regret) and coherence for a branch."""
    async for db in get_mcp_db():
        return await tool_get_branch_state(auth_token=auth_token, branch_id=branch_id, db=db)

@mcp_server.tool()
async def search_memories(
    auth_token: str,
    query: str,
    branch_id: Optional[str] = None,
    scenario_id: Optional[str] = None,
    top_k: int = 5
) -> Dict[str, Any]:
    """Search multiverse memory shards and reflections using KSHAN pgvector RAG pipeline."""
    async for db in get_mcp_db():
        return await tool_search_memories(
            auth_token=auth_token,
            query=query,
            branch_id=branch_id,
            scenario_id=scenario_id,
            top_k=top_k,
            db=db
        )

@mcp_server.tool()
async def get_recent_decisions(auth_token: str, branch_id: str, limit: int = 5) -> Dict[str, Any]:
    """Retrieve recent turning points and chosen options for an authenticated branch."""
    async for db in get_mcp_db():
        return await tool_get_recent_decisions(auth_token=auth_token, branch_id=branch_id, limit=limit, db=db)

@mcp_server.tool()
async def get_story_context(
    auth_token: str,
    branch_id: str,
    query: str,
    scenario_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Composite context aggregator:
    Combines active world rules, current branch status, recent turning points,
    characters, and pgvector RAG retrieval into structured context for AI generation.
    """
    async for db in get_mcp_db():
        return await tool_get_story_context(
            auth_token=auth_token,
            branch_id=branch_id,
            query=query,
            scenario_id=scenario_id,
            db=db
        )

@mcp_server.tool()
async def create_memory(
    auth_token: str,
    branch_id: str,
    title: str,
    content: str,
    emotional_tone: str = "epiphany",
    memory_type: str = "echo",
    node_id: Optional[str] = None
) -> Dict[str, Any]:
    """Write tool: Creates and indexes a new memory shard into PostgreSQL and pgvector."""
    async for db in get_mcp_db():
        return await tool_create_memory(
            auth_token=auth_token,
            branch_id=branch_id,
            title=title,
            content=content,
            emotional_tone=emotional_tone,
            memory_type=memory_type,
            node_id=node_id,
            db=db
        )

@mcp_server.tool()
async def create_timeline_event(
    auth_token: str,
    branch_id: str,
    story_text: str,
    era_year: str = "Year 0",
    sensory_cue: Optional[str] = None,
    audio_ambiance: str = "cosmic_drone",
    butterfly_impact: Optional[str] = None,
    parent_node_id: Optional[str] = None
) -> Dict[str, Any]:
    """Write tool: Creates and indexes a new timeline event node into PostgreSQL and pgvector."""
    async for db in get_mcp_db():
        return await tool_create_timeline_event(
            auth_token=auth_token,
            branch_id=branch_id,
            story_text=story_text,
            era_year=era_year,
            sensory_cue=sensory_cue,
            audio_ambiance=audio_ambiance,
            butterfly_impact=butterfly_impact,
            parent_node_id=parent_node_id,
            db=db
        )

# ----------------- MCP RESOURCES -----------------

@mcp_server.resource("kshan://world/{scenario_id}")
async def get_world_resource(scenario_id: str) -> str:
    """Read-only resource for world chronicle and realm topology."""
    async for db in get_mcp_db():
        return await resource_read_world(scenario_id=scenario_id, db=db)

@mcp_server.resource("kshan://timeline/{branch_id}")
async def get_timeline_resource(branch_id: str) -> str:
    """Read-only resource for full timeline chronicle of a branch."""
    async for db in get_mcp_db():
        return await resource_read_timeline(branch_id=branch_id, db=db)

@mcp_server.resource("kshan://memories/{branch_id}")
async def get_memories_resource(branch_id: str) -> str:
    """Read-only resource for all memory shards unlocked in a branch."""
    async for db in get_mcp_db():
        return await resource_read_memories(branch_id=branch_id, db=db)

# ----------------- MCP PROMPTS -----------------

@mcp_server.prompt("future_you_context")
def get_future_you_prompt(scenario_id: str, branch_id: str, query: str) -> List[Dict[str, Any]]:
    """Grounding prompt for conversational interaction with Future You."""
    return prompt_future_you_context(scenario_id=scenario_id, branch_id=branch_id, query=query)

# ASGI Application for Streamable HTTP
app = mcp_server.streamable_http_app()
