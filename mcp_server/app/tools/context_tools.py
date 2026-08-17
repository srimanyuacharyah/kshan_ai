from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from mcp_server.app.auth import authenticate_mcp_request, verify_branch_ownership
from backend.app.models.multiverse import RealityBranch, MultiverseState
from backend.app.models.world import World, Character
from backend.app.models.timeline import TimelineNode, Decision
from backend.app.services.rag.rag_pipeline import rag_pipeline

async def tool_get_story_context(
    auth_token: str,
    branch_id: str,
    query: str,
    scenario_id: Optional[str] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Primary composite context aggregator:
    Combines active world rules, current branch status, recent turning points,
    characters, and pgvector RAG retrieval into structured context for AI generation.
    """
    user = await authenticate_mcp_request(auth_token, db)
    branch = await verify_branch_ownership(db, user.user_id, branch_id)

    # 1. Branch & Multiverse State
    state_query = select(MultiverseState).where(MultiverseState.branch_id == branch.id)
    state_res = await db.execute(state_query)
    m_state = state_res.scalar_one_or_none()

    # 2. Latest Timeline Node
    latest_node_query = select(TimelineNode).where(
        TimelineNode.branch_id == branch.id,
        TimelineNode.user_id == user.user_id
    ).options(selectinload(TimelineNode.choices)).order_by(TimelineNode.depth_level.desc()).limit(1)
    node_res = await db.execute(latest_node_query)
    latest_node = node_res.scalar_one_or_none()

    # 3. Recent Decisions
    decision_query = select(Decision).join(TimelineNode, Decision.node_id == TimelineNode.id).where(
        TimelineNode.branch_id == branch.id,
        Decision.user_id == user.user_id
    ).options(selectinload(Decision.chosen_choice)).order_by(Decision.created_at.desc()).limit(3)
    dec_res = await db.execute(decision_query)
    recent_decisions = dec_res.scalars().all()

    # 4. RAG Semantic Search
    rag_data = await rag_pipeline.search_and_ground(
        db=db,
        query=query,
        user_id=user.user_id,
        branch_id=branch.id,
        scenario_id=scenario_id,
        top_k=4
    )

    return {
        "branch_summary": {
            "branch_id": branch.id,
            "branch_name": branch.branch_name,
            "branch_code": branch.branch_code,
            "entropy": branch.entropy_level,
            "resonance": branch.resonance_score,
            "regret": branch.regret_index,
            "era": m_state.timeline_era if m_state else "Genesis Era",
            "world_coherence": m_state.world_coherence if m_state else 1.0
        },
        "latest_node": {
            "node_id": latest_node.id if latest_node else None,
            "era_year": latest_node.era_year if latest_node else "Year 0",
            "narrative": latest_node.story_text if latest_node else "Genesis Moment",
            "sensory_cue": latest_node.sensory_cue if latest_node else None,
            "butterfly_impact": latest_node.butterfly_impact if latest_node else None
        } if latest_node else None,
        "recent_decisions": [
            {
                "chosen_action": d.chosen_choice.choice_label if d.chosen_choice else "Pivotal Choice",
                "rationale": d.rationale
            }
            for d in recent_decisions
        ],
        "grounded_rag_context": rag_data.context,
        "retrieved_chunks_count": rag_data.results_count
    }
