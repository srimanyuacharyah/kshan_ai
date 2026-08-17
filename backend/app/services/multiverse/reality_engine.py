from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.multiverse import RealityBranch, MultiverseState
from backend.app.models.timeline import TimelineNode
from backend.app.services.multiverse.branch_engine import branch_engine
from backend.app.core.logging import get_logger

logger = get_logger("kshan.multiverse.reality")

class RealityEngine:
    """
    High-level coordinator for active reality states, cosmos initialization, and branch traversal.
    """

    async def initialize_scenario_reality(
        self,
        db: AsyncSession,
        user_id: str,
        future_profile_id: Optional[str] = None,
        world_name: str = "Neo-Kashi Prime",
        scenario_theme: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bootstraps a brand new scenario reality baseline.
        """
        root_branch, genesis_node = await branch_engine.create_root_branch(
            db=db,
            user_id=user_id,
            future_profile_id=future_profile_id,
            branch_name=f"Prime Reality: {world_name}",
            initial_story=f"You materialize on the precipice of {world_name}. The timeline awaits your first choice.",
            initial_state={
                "entropy": 0.10,
                "resonance": 0.75,
                "regret": 0.00,
                "world_stability": 0.90,
                "social_stability": 0.80,
                "technology_level": 0.50
            }
        )
        return {
            "root_branch": root_branch,
            "genesis_node": genesis_node
        }

    async def get_branch_details(
        self,
        db: AsyncSession,
        user_id: str,
        branch_id: str
    ) -> Dict[str, Any]:
        """
        Returns full detailed snapshot of a branch including its state, timeline, and parentage.
        """
        stmt = select(RealityBranch).where(
            RealityBranch.id == branch_id,
            RealityBranch.user_id == user_id
        )
        res = await db.execute(stmt)
        branch = res.scalar_one_or_none()
        if not branch:
            raise ValueError(f"Reality branch '{branch_id}' not found or access forbidden.")

        # Load multiverse state
        state_stmt = select(MultiverseState).where(MultiverseState.branch_id == branch_id)
        s_res = await db.execute(state_stmt)
        m_state = s_res.scalar_one_or_none()

        # Load timeline nodes
        nodes_stmt = (
            select(TimelineNode)
            .where(TimelineNode.branch_id == branch_id)
            .order_by(TimelineNode.depth_level.asc())
        )
        n_res = await db.execute(nodes_stmt)
        nodes = n_res.scalars().all()

        return {
            "branch": {
                "id": branch.id,
                "name": branch.branch_name,
                "code": branch.branch_code,
                "status": branch.status,
                "parent_branch_id": branch.parent_branch_id,
                "fork_node_id": branch.fork_node_id,
                "depth": branch.branch_metadata.get("depth", 0),
                "entropy": branch.entropy_level,
                "resonance": branch.resonance_score,
                "regret": branch.regret_index,
                "destiny_shift": branch.destiny_shift,
                "metadata": branch.branch_metadata
            },
            "state": {
                "world_coherence": m_state.world_coherence if m_state else 1.0,
                "timeline_era": m_state.timeline_era if m_state else "Unknown Era",
                "state_variables": m_state.state_variables if m_state else {}
            },
            "timeline": [
                {
                    "id": n.id,
                    "depth_level": n.depth_level,
                    "era_year": n.era_year,
                    "story_text": n.story_text,
                    "sensory_cue": n.sensory_cue,
                    "entropy_delta": n.entropy_delta,
                    "resonance_delta": n.resonance_delta,
                    "regret_delta": n.regret_delta,
                    "butterfly_impact": n.butterfly_impact
                }
                for n in nodes
            ]
        }

reality_engine = RealityEngine()
