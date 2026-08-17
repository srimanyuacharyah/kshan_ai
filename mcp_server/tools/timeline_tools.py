from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from mcp_server.app.auth import authenticate_mcp_request, verify_branch_ownership
from backend.app.models.timeline import TimelineNode, Choice, Consequence, Decision
from backend.app.models.multiverse import RealityBranch, MultiverseState
from backend.app.services.rag.rag_pipeline import rag_pipeline

async def tool_get_timeline(auth_token: str, branch_id: str, limit: int = 10, db: AsyncSession = None) -> Dict[str, Any]:
    """Retrieve ordered sequence of timeline nodes for an authenticated user's branch."""
    user = await authenticate_mcp_request(auth_token, db)
    branch = await verify_branch_ownership(db, user.user_id, branch_id)

    query = select(TimelineNode).where(
        TimelineNode.branch_id == branch.id,
        TimelineNode.user_id == user.user_id
    ).options(selectinload(TimelineNode.choices)).order_by(TimelineNode.depth_level.asc()).limit(limit)

    result = await db.execute(query)
    nodes = result.scalars().all()

    return {
        "branch_id": branch.id,
        "branch_name": branch.branch_name,
        "branch_code": branch.branch_code,
        "entropy_level": branch.entropy_level,
        "resonance_score": branch.resonance_score,
        "nodes_count": len(nodes),
        "nodes": [
            {
                "id": n.id,
                "depth_level": n.depth_level,
                "era_year": n.era_year,
                "story_text": n.story_text,
                "sensory_cue": n.sensory_cue,
                "butterfly_impact": n.butterfly_impact,
                "choices": [
                    {
                        "choice_id": c.id,
                        "label": c.choice_label,
                        "description": c.choice_description,
                        "risk_level": c.risk_level
                    }
                    for c in n.choices
                ]
            }
            for n in nodes
        ]
    }

async def tool_get_timeline_node(auth_token: str, node_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Retrieve full details, choices, and consequence forecast for a single timeline node."""
    user = await authenticate_mcp_request(auth_token, db)

    query = select(TimelineNode).where(
        TimelineNode.id == node_id,
        TimelineNode.user_id == user.user_id
    ).options(selectinload(TimelineNode.choices), selectinload(TimelineNode.decision))

    result = await db.execute(query)
    node = result.scalar_one_or_none()

    if not node:
        return {"error": f"Timeline node '{node_id}' not found or unauthorized."}

    return {
        "id": node.id,
        "branch_id": node.branch_id,
        "depth_level": node.depth_level,
        "era_year": node.era_year,
        "story_text": node.story_text,
        "sensory_cue": node.sensory_cue,
        "audio_ambiance": node.audio_ambiance,
        "butterfly_impact": node.butterfly_impact,
        "has_decision": node.decision is not None,
        "choices": [
            {
                "choice_id": c.id,
                "label": c.choice_label,
                "description": c.choice_description,
                "risk_level": c.risk_level,
                "philosophical_vector": c.philosophical_vector
            }
            for c in node.choices
        ]
    }

async def tool_get_branch_state(auth_token: str, branch_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Retrieve current multiverse metrics, coherence, and state variables for a branch."""
    user = await authenticate_mcp_request(auth_token, db)
    branch = await verify_branch_ownership(db, user.user_id, branch_id)

    query = select(MultiverseState).where(MultiverseState.branch_id == branch.id)
    result = await db.execute(query)
    state = result.scalar_one_or_none()

    return {
        "branch_id": branch.id,
        "branch_name": branch.branch_name,
        "branch_code": branch.branch_code,
        "status": branch.status,
        "metrics": {
            "entropy_level": branch.entropy_level,
            "resonance_score": branch.resonance_score,
            "regret_index": branch.regret_index,
            "destiny_shift": branch.destiny_shift
        },
        "multiverse_state": {
            "timeline_era": state.timeline_era if state else "Genesis",
            "world_coherence": state.world_coherence if state else 1.0,
            "total_nodes_count": state.total_nodes_count if state else 1,
            "state_variables": state.state_variables if state else {}
        }
    }

async def tool_create_timeline_event(
    auth_token: str,
    branch_id: str,
    story_text: str,
    era_year: str = "Year 0",
    sensory_cue: Optional[str] = None,
    audio_ambiance: str = "cosmic_drone",
    butterfly_impact: Optional[str] = None,
    parent_node_id: Optional[str] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Controlled write tool: Creates a new timeline event node in PostgreSQL
    and triggers RAG pgvector indexing.
    """
    user = await authenticate_mcp_request(auth_token, db)
    branch = await verify_branch_ownership(db, user.user_id, branch_id)

    # Determine depth level
    depth = 0
    if parent_node_id:
        parent_query = select(TimelineNode).where(TimelineNode.id == parent_node_id, TimelineNode.user_id == user.user_id)
        parent_res = await db.execute(parent_query)
        parent = parent_res.scalar_one_or_none()
        if parent:
            depth = parent.depth_level + 1

    node = TimelineNode(
        user_id=user.user_id,
        branch_id=branch.id,
        parent_node_id=parent_node_id,
        depth_level=depth,
        era_year=era_year,
        story_text=story_text,
        sensory_cue=sensory_cue,
        audio_ambiance=audio_ambiance,
        butterfly_impact=butterfly_impact
    )
    db.add(node)
    await db.flush()

    # Trigger RAG vector indexing
    await rag_pipeline.index_timeline_node(db, node, user.user_id)
    await db.commit()

    return {
        "success": True,
        "message": "Timeline event created and indexed into vector store.",
        "node_id": node.id,
        "depth_level": node.depth_level,
        "era_year": node.era_year
    }
