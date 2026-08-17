from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_active_user
from backend.app.models.user import User
from backend.app.schemas.rag import RAGSearchRequest, RAGSearchResponse
from backend.app.schemas.common import StandardResponse
from backend.app.services.rag.rag_pipeline import rag_pipeline
from backend.app.core.logging import logger

router = APIRouter(prefix="/rag", tags=["Retrieval-Augmented Generation (RAG)"])

@router.post("/search", response_model=StandardResponse[RAGSearchResponse])
async def search_grounded_context(
    request: RAGSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search grounded multiverse memories, timeline events, character lore, and decisions.
    Strictly isolated to the authenticated user's reality branches.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=422,
            detail="Search query cannot be empty"
        )

    logger.info(
        f"Executing RAG search for user={current_user.id} ({current_user.username}): '{request.query[:50]}...'"
    )

    try:
        response = await rag_pipeline.search_and_ground(
            db=db,
            query=request.query,
            user_id=current_user.id,
            branch_id=request.branch_id,
            scenario_id=request.scenario_id,
            entity_types=request.entity_types,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        return StandardResponse(
            message="Multiverse context retrieved successfully",
            data=response
        )
    except Exception as e:
        logger.error(f"RAG search error for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve multiverse memory context"
        )
