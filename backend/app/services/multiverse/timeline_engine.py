import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.timeline import TimelineNode, Choice
from backend.app.core.logging import get_logger

logger = get_logger("kshan.multiverse.timeline")

class TimelineEngine:
    """
    Manages append-only, immutable timeline node chains for reality branches.
    """

    async def append_timeline_node(
        self,
        db: AsyncSession,
        user_id: str,
        branch_id: str,
        parent_node_id: Optional[str],
        depth_level: int,
        story_text: str,
        era_year: str = "Year 0",
        sensory_cue: Optional[str] = None,
        audio_ambiance: str = "cosmic_drone",
        entropy_delta: float = 0.0,
        resonance_delta: float = 0.0,
        regret_delta: float = 0.0,
        butterfly_impact: Optional[str] = None,
        node_metadata: Optional[Dict[str, Any]] = None
    ) -> TimelineNode:
        """
        Creates and appends an immutable timeline node to a reality branch.
        """
        node = TimelineNode(
            id=str(uuid.uuid4()),
            user_id=user_id,
            branch_id=branch_id,
            parent_node_id=parent_node_id,
            depth_level=depth_level,
            era_year=era_year,
            story_text=story_text,
            sensory_cue=sensory_cue or "Electrostatic hum; shifting shadows",
            audio_ambiance=audio_ambiance,
            entropy_delta=entropy_delta,
            resonance_delta=resonance_delta,
            regret_delta=regret_delta,
            butterfly_impact=butterfly_impact or "A ripple formed in the local reality continuum.",
            node_metadata=node_metadata or {}
        )
        db.add(node)
        await db.flush()
        logger.info(f"Appended timeline node: id={node.id}, branch_id={branch_id}, depth={depth_level}")
        return node

    async def get_timeline_nodes(
        self,
        db: AsyncSession,
        branch_id: str,
        user_id: str
    ) -> List[TimelineNode]:
        """
        Retrieves all timeline nodes for a branch ordered chronologically.
        """
        stmt = (
            select(TimelineNode)
            .where(
                TimelineNode.branch_id == branch_id,
                TimelineNode.user_id == user_id
            )
            .order_by(TimelineNode.depth_level.asc(), TimelineNode.created_at.asc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_node_by_id(
        self,
        db: AsyncSession,
        node_id: str,
        user_id: str
    ) -> Optional[TimelineNode]:
        """
        Retrieves a single timeline node ensuring tenant isolation.
        """
        stmt = select(TimelineNode).where(
            TimelineNode.id == node_id,
            TimelineNode.user_id == user_id
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

timeline_engine = TimelineEngine()
