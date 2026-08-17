from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.services.ai.orchestrator import ai_orchestrator
from backend.app.services.ai.exceptions import (
    AIGenerationError,
    ResponseValidationError,
    RateLimitExceededError,
    GeminiAPIError
)
from backend.app.services.mcp.exceptions import MCPAuthorizationError
from backend.app.services.ai.schemas import (
    StoryGenerationRequest,
    StoryGenerationResponse,
    BranchGenerationRequest,
    BranchGenerationResponse,
    FutureYouRequest,
    FutureYouResponse,
    WorldGenerationRequest,
    WorldGenerationResponse,
    CharacterGenerationRequest,
    CharacterGenerationResponse,
    DecisionAnalysisRequest,
    DecisionAnalysisResponse
)

router = APIRouter(prefix="/ai", tags=["AI Orchestrator & Generative Multiverse"])

@router.post("/story", response_model=StoryGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_story(
    req: StoryGenerationRequest,
    authorization: str = Header(..., description="Bearer JWT token"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate the next immersive timeline event and 3 branching choices."""
    token = authorization.replace("Bearer ", "").strip()
    try:
        return await ai_orchestrator.generate_story(
            db=db,
            user_id=current_user.id,
            scenario_id=req.scenario_id,
            branch_id=req.branch_id,
            prompt_seed=req.prompt_seed,
            custom_intention=req.custom_intention,
            auth_token=token
        )
    except MCPAuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RateLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/branch", response_model=BranchGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_branch(
    req: BranchGenerationRequest,
    authorization: str = Header(..., description="Bearer JWT token"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate exactly 3 divergent narrative choices from the current node."""
    token = authorization.replace("Bearer ", "").strip()
    try:
        return await ai_orchestrator.generate_branching_choices(
            db=db,
            user_id=current_user.id,
            scenario_id=req.scenario_id,
            branch_id=req.branch_id,
            timeline_node_id=req.timeline_node_id,
            intention=req.intention,
            auth_token=token
        )
    except MCPAuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RateLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/future-you", response_model=FutureYouResponse, status_code=status.HTTP_200_OK)
async def generate_future_you(
    req: FutureYouRequest,
    authorization: str = Header(..., description="Bearer JWT token"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Manifest the traveler's alternate future self grounded in reality branch memories."""
    token = authorization.replace("Bearer ", "").strip()
    try:
        return await ai_orchestrator.generate_future_you(
            db=db,
            user_id=current_user.id,
            scenario_id=req.scenario_id,
            branch_id=req.branch_id,
            user_question=req.user_question,
            auth_token=token
        )
    except MCPAuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RateLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/world", response_model=WorldGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_world(
    req: WorldGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate and persist a new multiverse world, indexing lore into pgvector RAG."""
    try:
        return await ai_orchestrator.generate_world(
            db=db,
            user_id=current_user.id,
            scenario_id=req.scenario_id,
            theme_prompt=req.theme_prompt,
            cosmos_type=req.cosmos_type
        )
    except RateLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/character", response_model=CharacterGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_character(
    req: CharacterGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate and persist a character or companion, indexing profile into pgvector RAG."""
    try:
        return await ai_orchestrator.generate_character(
            db=db,
            user_id=current_user.id,
            world_id=req.world_id,
            role_description=req.role_description,
            faction_preference=req.faction_preference
        )
    except RateLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/analyze-decision", response_model=DecisionAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_decision(
    req: DecisionAnalysisRequest,
    authorization: str = Header(..., description="Bearer JWT token"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze the systemic and philosophical ramifications of a turning point decision."""
    token = authorization.replace("Bearer ", "").strip()
    try:
        return await ai_orchestrator.analyze_decision(
            db=db,
            user_id=current_user.id,
            branch_id=req.branch_id,
            node_id=req.node_id,
            chosen_choice_id=req.chosen_choice_id,
            rationale=req.rationale,
            auth_token=token
        )
    except MCPAuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RateLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
