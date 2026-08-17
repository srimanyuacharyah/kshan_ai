import time
import math
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, and_, or_
from backend.app.models.embedding import EmbeddingRecord
from backend.app.core.logging import logger

class VectorSearchResult:
    """Represents a matched chunk with cosine similarity score and metadata."""
    def __init__(
        self,
        id: str,
        document_content: str,
        document_title: Optional[str],
        entity_type: str,
        entity_id: str,
        user_id: str,
        branch_id: Optional[str],
        score: float,
        metadata: Dict[str, Any]
    ):
        self.id = id
        self.document_content = document_content
        self.document_title = document_title
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.user_id = user_id
        self.branch_id = branch_id
        self.score = score
        self.metadata = metadata

class VectorStore:
    """
    PostgreSQL + pgvector storage interface with strict multi-tenant user isolation.
    """

    async def add_embedding(
        self,
        db: AsyncSession,
        user_id: str,
        entity_type: str,
        entity_id: str,
        document_content: str,
        embedding_vector: List[float],
        branch_id: Optional[str] = None,
        document_title: Optional[str] = None,
        metadata_payload: Optional[Dict[str, Any]] = None
    ) -> EmbeddingRecord:
        """Store a vector embedding record scoped to a specific user and optional branch."""
        record = EmbeddingRecord(
            user_id=user_id,
            branch_id=branch_id,
            entity_type=entity_type,
            entity_id=entity_id,
            document_content=document_content,
            document_title=document_title,
            metadata_payload=metadata_payload or {},
            embedding_vector=embedding_vector
        )
        db.add(record)
        await db.flush()
        logger.info(
            f"Stored embedding for user={user_id}, entity={entity_type}:{entity_id}, chars={len(document_content)}"
        )
        return record

    async def search_similar(
        self,
        db: AsyncSession,
        query_embedding: List[float],
        user_id: str,
        branch_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
        entity_types: Optional[List[str]] = None,
        top_k: int = 6,
        similarity_threshold: float = 0.0
    ) -> List[VectorSearchResult]:
        """
        Execute cosine similarity search over vector store.
        STRICTLY scoped to the authenticated user_id to enforce multi-tenant isolation.
        """
        start = time.perf_counter()

        # Build tenant-isolated filter conditions
        conditions = [EmbeddingRecord.user_id == user_id]

        if branch_id:
            # Match branch-specific items or global items (branch_id is null)
            conditions.append(
                or_(EmbeddingRecord.branch_id == branch_id, EmbeddingRecord.branch_id.is_(None))
            )

        if entity_types:
            conditions.append(EmbeddingRecord.entity_type.in_(entity_types))

        # Check if running against PostgreSQL with pgvector cosine_distance
        bind = db.get_bind()
        is_postgres = "postgresql" in bind.dialect.name

        results: List[VectorSearchResult] = []

        if is_postgres:
            # Use native pgvector cosine distance operator <=>
            # cosine similarity = 1 - cosine distance
            try:
                distance_expr = EmbeddingRecord.embedding_vector.cosine_distance(query_embedding)
                query = (
                    select(
                        EmbeddingRecord,
                        (1.0 - distance_expr).label("similarity_score")
                    )
                    .where(and_(*conditions))
                    .order_by(distance_expr.asc())
                    .limit(top_k * 2) # Fetch candidate pool before thresholding
                )
                db_results = await db.execute(query)
                for row, sim_score in db_results.all():
                    score_val = float(sim_score) if sim_score is not None else 0.0
                    # Filter by scenario_id inside metadata if requested
                    if scenario_id:
                        row_scenario = (row.metadata_payload or {}).get("scenario_id")
                        if row_scenario and row_scenario != scenario_id:
                            continue

                    if score_val >= similarity_threshold:
                        results.append(
                            VectorSearchResult(
                                id=row.id,
                                document_content=row.document_content,
                                document_title=row.document_title,
                                entity_type=row.entity_type,
                                entity_id=row.entity_id,
                                user_id=row.user_id,
                                branch_id=row.branch_id,
                                score=round(score_val, 4),
                                metadata=row.metadata_payload or {}
                            )
                        )
            except Exception as e:
                logger.warning(f"Native pgvector query failed ({e}), falling back to memory cosine math.")
                is_postgres = False

        if not is_postgres or not results:
            # In-memory cosine calculation for tests / fallback environments
            query = select(EmbeddingRecord).where(and_(*conditions))
            db_results = await db.execute(query)
            all_records = db_results.scalars().all()

            scored_records = []
            for rec in all_records:
                if scenario_id:
                    row_scenario = (rec.metadata_payload or {}).get("scenario_id")
                    if row_scenario and row_scenario != scenario_id:
                        continue

                rec_vec = rec.embedding_vector
                if rec_vec is None:
                    continue

                # Ensure vector is a list of floats
                if isinstance(rec_vec, (list, tuple)):
                    v2 = list(rec_vec)
                else:
                    try:
                        v2 = [float(x) for x in rec_vec]
                    except Exception:
                        continue

                # Compute cosine similarity
                dot = sum(a * b for a, b in zip(query_embedding, v2))
                norm_q = math.sqrt(sum(a * a for a in query_embedding)) or 1.0
                norm_v = math.sqrt(sum(b * b for b in v2)) or 1.0
                cosine_sim = dot / (norm_q * norm_v)

                if cosine_sim >= similarity_threshold:
                    scored_records.append((rec, cosine_sim))

            # Sort descending by similarity
            scored_records.sort(key=lambda x: x[1], reverse=True)
            for rec, sim in scored_records[:top_k]:
                results.append(
                    VectorSearchResult(
                        id=rec.id,
                        document_content=rec.document_content,
                        document_title=rec.document_title,
                        entity_type=rec.entity_type,
                        entity_id=rec.entity_id,
                        user_id=rec.user_id,
                        branch_id=rec.branch_id,
                        score=round(float(sim), 4),
                        metadata=rec.metadata_payload or {}
                    )
                )

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            f"RAG vector search complete: user={user_id}, query_top_k={top_k}, matched={len(results)} in {elapsed_ms}ms"
        )
        return results[:top_k]

    async def delete_entity_embeddings(
        self,
        db: AsyncSession,
        user_id: str,
        entity_type: str,
        entity_id: str
    ) -> int:
        """Delete stale embeddings for a specific entity belonging to a user."""
        stmt = delete(EmbeddingRecord).where(
            and_(
                EmbeddingRecord.user_id == user_id,
                EmbeddingRecord.entity_type == entity_type,
                EmbeddingRecord.entity_id == entity_id
            )
        )
        res = await db.execute(stmt)
        return res.rowcount or 0

    async def delete_branch_embeddings(
        self,
        db: AsyncSession,
        user_id: str,
        branch_id: str
    ) -> int:
        """Delete all embeddings associated with a branch belonging to a user."""
        stmt = delete(EmbeddingRecord).where(
            and_(
                EmbeddingRecord.user_id == user_id,
                EmbeddingRecord.branch_id == branch_id
            )
        )
        res = await db.execute(stmt)
        return res.rowcount or 0

    async def delete_user_embeddings(
        self,
        db: AsyncSession,
        user_id: str
    ) -> int:
        """Purge all embeddings for a user upon account deletion."""
        stmt = delete(EmbeddingRecord).where(EmbeddingRecord.user_id == user_id)
        res = await db.execute(stmt)
        return res.rowcount or 0

vector_store = VectorStore()
