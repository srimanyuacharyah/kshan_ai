import uuid
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.timeline import Decision, Choice, TimelineNode
from backend.app.core.logging import get_logger

logger = get_logger("kshan.multiverse.decision")

class DecisionEngine:
    """
    Manages recording and validation of immutable player decisions with idempotency support.
    """

    async def record_decision(
        self,
        db: AsyncSession,
        user_id: str,
        node_id: str,
        choice_id: str,
        rationale: Optional[str] = None,
        intention: Optional[str] = None,
        divergence_magnitude: float = 0.1,
        ai_generation_id: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> Decision:
        """
        Records an immutable decision. If one already exists for this node/choice/idempotency key,
        returns the existing decision to ensure idempotency.
        """
        # 1. Check if decision already recorded for this node
        existing_stmt = select(Decision).where(
            Decision.node_id == node_id,
            Decision.user_id == user_id
        )
        existing_res = await db.execute(existing_stmt)
        existing_decision = existing_res.scalar_one_or_none()

        if existing_decision:
            logger.info(f"Idempotent decision retrieval: node_id={node_id}, decision_id={existing_decision.id}")
            return existing_decision

        # 2. Check choice validity
        choice_stmt = select(Choice).where(Choice.id == choice_id)
        choice_res = await db.execute(choice_stmt)
        choice = choice_res.scalar_one_or_none()
        if not choice:
            raise ValueError(f"Choice with ID '{choice_id}' not found.")

        # 3. Create new immutable decision
        decision = Decision(
            id=str(uuid.uuid4()),
            user_id=user_id,
            node_id=node_id,
            chosen_choice_id=choice_id,
            rationale=rationale or f"Chose: {choice.choice_label}",
            divergence_magnitude=divergence_magnitude,
            decision_metadata={
                "intention": intention,
                "ai_generation_id": ai_generation_id,
                "idempotency_key": idempotency_key,
                "choice_label": choice.choice_label,
                "philosophical_vector": choice.philosophical_vector,
                "risk_level": choice.risk_level
            }
        )
        db.add(decision)
        await db.flush()
        logger.info(f"Recorded new decision: id={decision.id}, user_id={user_id}, choice_id={choice_id}")
        return decision

decision_engine = DecisionEngine()
