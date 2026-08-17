from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.api.deps import get_current_active_user
from backend.app.services.multiverse.branch_engine import branch_engine
from backend.app.services.multiverse.reality_engine import reality_engine
from backend.app.core.logging import get_logger

logger = get_logger("kshan.api.multiverse")

router = APIRouter()

# ----------------- SCHEMAS -----------------

class ChooseActionRequest(BaseModel):
    branch_id: str
    timeline_node_id: str
    choice_id: str
    intention: Optional[str] = None
    narrative_consequence_proposal: Optional[str] = None
    custom_branch_name: Optional[str] = None
    idempotency_key: Optional[str] = None

class RewindRequest(BaseModel):
    historical_node_id: str
    rewind_intention: Optional[str] = None

class CreateBranchRequest(BaseModel):
    future_profile_id: Optional[str] = None
    branch_name: str = "Prime Reality Baseline"
    initial_story: Optional[str] = "Genesis moment."
    initial_entropy: float = 0.10
    initial_resonance: float = 0.70

# ----------------- ENDPOINTS -----------------

@router.post("/choose", status_code=status.HTTP_201_CREATED)
async def choose_action(
    req: ChooseActionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes a player choice at a timeline node, spawning an immutable, persistent child reality branch.
    Guarantees parent branch immutability, deterministic state transitions, and 4-tier butterfly effect propagation.
    """
    try:
        res = await branch_engine.create_branch_from_decision(
            db=db,
            user_id=current_user.id,
            parent_branch_id=req.branch_id,
            timeline_node_id=req.timeline_node_id,
            choice_id=req.choice_id,
            intention=req.intention,
            narrative_consequence_proposal=req.narrative_consequence_proposal,
            custom_branch_name=req.custom_branch_name,
            idempotency_key=req.idempotency_key
        )
        await db.commit()

        b = res["branch"]
        n = res["timeline_node"]
        d = res.get("decision")
        sv = res.get("state_vector")
        br = res.get("butterfly_ripple")

        return {
            "status": "success",
            "is_idempotent_replay": res.get("is_idempotent_replay", False),
            "new_branch": {
                "id": b.id,
                "name": b.branch_name,
                "code": b.branch_code,
                "parent_branch_id": b.parent_branch_id,
                "depth": b.branch_metadata.get("depth", 1),
                "entropy": b.entropy_level,
                "resonance": b.resonance_score,
                "regret": b.regret_index,
                "destiny_shift": b.destiny_shift
            },
            "new_timeline_node": {
                "id": n.id,
                "depth_level": n.depth_level,
                "era_year": n.era_year,
                "story_text": n.story_text,
                "butterfly_impact": n.butterfly_impact
            } if n else None,
            "decision_id": d.id if d else None,
            "state_vector": sv.to_dict() if sv else None,
            "butterfly_ripple": br.model_dump() if br else None
        }
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error(f"Multiverse choice execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Multiverse error: {str(e)}")

@router.post("/rewind", status_code=status.HTTP_201_CREATED)
async def rewind_to_node(
    req: RewindRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Time travel / Rewind mechanism:
    Creates a new parallel fork reality branch (Reality A') from an earlier node without deleting history.
    """
    try:
        res = await branch_engine.rewind_to_node(
            db=db,
            user_id=current_user.id,
            historical_node_id=req.historical_node_id,
            rewind_intention=req.rewind_intention
        )
        await db.commit()
        fb = res["fork_branch"]
        an = res["anchor_node"]
        pb = res["parent_branch"]

        return {
            "status": "success",
            "fork_branch": {
                "id": fb.id,
                "name": fb.branch_name,
                "code": fb.branch_code,
                "parent_branch_id": fb.parent_branch_id,
                "entropy": fb.entropy_level,
                "resonance": fb.resonance_score,
                "regret": fb.regret_index,
                "depth": fb.branch_metadata.get("depth", 0)
            },
            "anchor_node": {
                "id": an.id,
                "depth_level": an.depth_level,
                "era_year": an.era_year,
                "story_text": an.story_text
            },
            "parent_branch": {
                "id": pb.id,
                "name": pb.branch_name
            }
        }
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error(f"Multiverse rewind failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/branch", status_code=status.HTTP_201_CREATED)
async def create_branch(
    req: CreateBranchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Explicit creation of a root reality branch for a traveler.
    """
    try:
        root_branch, genesis_node = await branch_engine.create_root_branch(
            db=db,
            user_id=current_user.id,
            future_profile_id=req.future_profile_id,
            branch_name=req.branch_name,
            initial_story=req.initial_story or "Genesis moment.",
            initial_state={
                "entropy": req.initial_entropy,
                "resonance": req.initial_resonance
            }
        )
        await db.commit()
        return {
            "status": "success",
            "branch": {
                "id": root_branch.id,
                "name": root_branch.branch_name,
                "code": root_branch.branch_code,
                "depth": 0,
                "entropy": root_branch.entropy_level,
                "resonance": root_branch.resonance_score
            },
            "genesis_node": {
                "id": genesis_node.id,
                "story_text": genesis_node.story_text
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/tree/{scenario_id}")
async def get_multiverse_tree(
    scenario_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the complete graph topology (nodes + edges) of reality branches for 3D cinematic visualization.
    """
    try:
        tree = await branch_engine.get_branch_tree(
            db=db,
            user_id=current_user.id,
            scenario_id=scenario_id
        )
        return tree
    except Exception as e:
        logger.error(f"Multiverse tree retrieval failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/branch/{branch_id}")
async def get_branch_details(
    branch_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves complete state variables, chronological timeline, and metadata for a specific reality branch.
    """
    try:
        details = await reality_engine.get_branch_details(
            db=db,
            user_id=current_user.id,
            branch_id=branch_id
        )
        return details
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Branch details retrieval failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/compare/{branch_a}/{branch_b}")
async def compare_branches(
    branch_a: str,
    branch_b: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Performs multidimensional differential analysis between two reality branches.
    """
    try:
        diff = await branch_engine.compare_branches(
            db=db,
            user_id=current_user.id,
            branch_a_id=branch_a,
            branch_b_id=branch_b
        )
        return diff
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Branch comparison failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
