from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from mcp_server.app.auth import authenticate_mcp_request, verify_branch_ownership
from backend.app.models.memory import Memory
from backend.app.services.rag.rag_pipeline import rag_pipeline

async def tool_search_memories(
    auth_token: str,
    query: str,
    branch_id: Optional[str] = None,
    scenario_id: Optional[str] = None,
    top_k: int = 5,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Search multiverse memory shards and reflections using KSHAN pgvector RAG pipeline.
    Strictly scoped to the authenticated caller.
    """
    user = await authenticate_mcp_request(auth_token, db)
    if branch_id:
        await verify_branch_ownership(db, user.user_id, branch_id)

    rag_response = await rag_pipeline.search_and_ground(
        db=db,
        query=query,
        user_id=user.user_id,
        branch_id=branch_id,
        scenario_id=scenario_id,
        entity_types=["memory", "timeline_node"],
        top_k=top_k
    )

    return {
        "query": query,
        "results_count": rag_response.results_count,
        "memories": [
            {
                "entity_id": r.entity_id,
                "document_type": r.document_type,
                "title": r.document_title,
                "content": r.content,
                "relevance_score": r.score,
                "metadata": r.metadata
            }
            for r in rag_response.results
        ],
        "grounded_context": rag_response.context
    }

async def tool_create_memory(
    auth_token: str,
    branch_id: str,
    title: str,
    content: str,
    emotional_tone: str = "epiphany",
    memory_type: str = "echo",
    node_id: Optional[str] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Controlled write tool: Persists a new memory shard into PostgreSQL
    and triggers RAG vector store indexing.
    """
    user = await authenticate_mcp_request(auth_token, db)
    branch = await verify_branch_ownership(db, user.user_id, branch_id)

    memory = Memory(
        user_id=user.user_id,
        branch_id=branch.id,
        node_id=node_id,
        title=title,
        content=content,
        emotional_tone=emotional_tone,
        memory_type=memory_type,
        clarity_level=1.0
    )
    db.add(memory)
    await db.flush()

    # Trigger RAG vector indexing
    await rag_pipeline.index_memory(db, memory, user.user_id)
    await db.commit()

    return {
        "success": True,
        "message": "Memory created and indexed into vector store.",
        "memory_id": memory.id,
        "title": memory.title,
        "emotional_tone": memory.emotional_tone
    }
