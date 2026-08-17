from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from mcp_server.app.auth import authenticate_mcp_request, verify_branch_ownership
from backend.app.models.timeline import Decision, TimelineNode, Choice

async def tool_get_recent_decisions(auth_token: str, branch_id: str, limit: int = 5, db: AsyncSession = None) -> Dict[str, Any]:
    """Retrieve recent turning points and chosen options for an authenticated user's branch."""
    user = await authenticate_mcp_request(auth_token, db)
    branch = await verify_branch_ownership(db, user.user_id, branch_id)

    query = select(Decision).join(TimelineNode, Decision.node_id == TimelineNode.id).where(
        TimelineNode.branch_id == branch.id,
        Decision.user_id == user.user_id
    ).options(selectinload(Decision.chosen_choice), selectinload(Decision.node)).order_by(Decision.created_at.desc()).limit(limit)

    result = await db.execute(query)
    decisions = result.scalars().all()

    return {
        "branch_id": branch.id,
        "decisions_count": len(decisions),
        "decisions": [
            {
                "decision_id": d.id,
                "node_id": d.node_id,
                "era_year": d.node.era_year if d.node else "Unknown",
                "chosen_action": d.chosen_choice.choice_label if d.chosen_choice else "Custom",
                "action_description": d.chosen_choice.choice_description if d.chosen_choice else "",
                "rationale": d.rationale,
                "divergence_magnitude": d.divergence_magnitude,
                "timestamp": d.created_at.isoformat() if d.created_at else None
            }
            for d in decisions
        ]
    }
