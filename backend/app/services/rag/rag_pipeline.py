import time
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.services.rag.retriever import retriever
from backend.app.services.rag.context_builder import context_builder
from backend.app.services.rag.document_processor import document_processor, ProcessedDocument
from backend.app.services.rag.embedding_service import embedding_service
from backend.app.services.rag.vector_store import vector_store
from backend.app.schemas.rag import RAGSearchResponse, RetrievalResultItem
from backend.app.models.timeline import TimelineNode, Decision, Choice
from backend.app.models.memory import Memory
from backend.app.models.world import World, Character, Location
from backend.app.core.logging import logger

class RAGPipeline:
    """
    End-to-end RAG orchestrator for KSHAN:
    Handles indexing of multiverse entities, stale vector invalidation,
    query embedding, tenant-isolated vector search, and grounded context construction.
    """

    async def search_and_ground(
        self,
        db: AsyncSession,
        query: str,
        user_id: str,
        branch_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
        entity_types: Optional[List[str]] = None,
        top_k: int = 6,
        similarity_threshold: float = 0.0
    ) -> RAGSearchResponse:
        """Execute full RAG retrieval and return structured grounded response."""
        start_time = time.perf_counter()

        search_results = await retriever.retrieve(
            db=db,
            query=query,
            user_id=user_id,
            branch_id=branch_id,
            scenario_id=scenario_id,
            entity_types=entity_types,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )

        context_str = context_builder.build_grounded_context(search_results)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        items = [
            RetrievalResultItem(
                content=r.document_content,
                score=r.score,
                document_type=r.entity_type,
                entity_id=r.entity_id,
                document_title=r.document_title,
                metadata=r.metadata
            )
            for r in search_results
        ]

        return RAGSearchResponse(
            query=query,
            results_count=len(items),
            results=items,
            context=context_str,
            retrieval_time_ms=elapsed_ms
        )

    async def index_processed_document(self, db: AsyncSession, doc: ProcessedDocument) -> int:
        """
        Index a ProcessedDocument:
        1. Invalidate/delete existing stale embeddings for this entity.
        2. Generate vector embeddings for each chunk.
        3. Insert new embedding records into pgvector.
        """
        # Delete old embeddings for this entity
        await vector_store.delete_entity_embeddings(
            db=db,
            user_id=doc.user_id,
            entity_type=doc.entity_type,
            entity_id=doc.entity_id
        )

        indexed_count = 0
        for chunk in doc.chunks:
            # Generate embedding vector
            vec = await embedding_service.get_embedding(chunk.content)
            await vector_store.add_embedding(
                db=db,
                user_id=doc.user_id,
                entity_type=doc.entity_type,
                entity_id=doc.entity_id,
                document_content=chunk.content,
                embedding_vector=vec,
                branch_id=doc.branch_id,
                document_title=doc.title,
                metadata_payload=chunk.metadata
            )
            indexed_count += 1

        logger.info(
            f"Indexed {indexed_count} chunks for entity={doc.entity_type}:{doc.entity_id}, user={doc.user_id}"
        )
        return indexed_count

    async def index_timeline_node(self, db: AsyncSession, node: TimelineNode, user_id: str) -> int:
        doc = document_processor.process_timeline_node(node, user_id)
        return await self.index_processed_document(db, doc)

    async def index_memory(self, db: AsyncSession, memory: Memory, user_id: str) -> int:
        doc = document_processor.process_memory(memory, user_id)
        return await self.index_processed_document(db, doc)

    async def index_decision(self, db: AsyncSession, decision: Decision, user_id: str, choice: Optional[Choice] = None) -> int:
        doc = document_processor.process_decision(decision, user_id, choice)
        return await self.index_processed_document(db, doc)

    async def index_character(self, db: AsyncSession, character: Character, user_id: str, branch_id: Optional[str] = None) -> int:
        doc = document_processor.process_character(character, user_id, branch_id)
        return await self.index_processed_document(db, doc)

    async def index_world(self, db: AsyncSession, world: World, user_id: str, branch_id: Optional[str] = None) -> int:
        doc = document_processor.process_world(world, user_id, branch_id)
        return await self.index_processed_document(db, doc)

    async def index_location(self, db: AsyncSession, location: Location, user_id: str, branch_id: Optional[str] = None) -> int:
        doc = document_processor.process_location(location, user_id, branch_id)
        return await self.index_processed_document(db, doc)

    async def delete_entity_index(self, db: AsyncSession, user_id: str, entity_type: str, entity_id: str) -> int:
        return await vector_store.delete_entity_embeddings(db, user_id, entity_type, entity_id)

    async def delete_branch_index(self, db: AsyncSession, user_id: str, branch_id: str) -> int:
        return await vector_store.delete_branch_embeddings(db, user_id, branch_id)

rag_pipeline = RAGPipeline()
