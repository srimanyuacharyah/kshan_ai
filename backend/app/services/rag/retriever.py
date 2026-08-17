import time
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.services.rag.embedding_service import embedding_service
from backend.app.services.rag.vector_store import vector_store, VectorSearchResult
from backend.app.schemas.rag import RetrievalResultItem
from backend.app.core.logging import logger

class RAGRetriever:
    """
    Coordinates query embedding generation, tenant-isolated vector search,
    and ranking of grounded multiverse records.
    """

    async def retrieve(
        self,
        db: AsyncSession,
        query: str,
        user_id: str,
        branch_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
        entity_types: Optional[List[str]] = None,
        top_k: int = 6,
        similarity_threshold: float = 0.0
    ) -> List[VectorSearchResult]:
        """
        Execute full retrieval pipeline for a natural language user query.
        Guarantees strict tenant isolation by scoping down to authenticated user_id.
        """
        start = time.perf_counter()
        
        # 1. Generate query embedding vector
        query_vector = await embedding_service.get_embedding(query)

        # 2. Query pgvector store with tenant isolation
        results = await vector_store.search_similar(
            db=db,
            query_embedding=query_vector,
            user_id=user_id,
            branch_id=branch_id,
            scenario_id=scenario_id,
            entity_types=entity_types,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            f"RAG Retriever executed query for user={user_id}, matched={len(results)} chunks in {elapsed_ms}ms"
        )
        return results

retriever = RAGRetriever()
