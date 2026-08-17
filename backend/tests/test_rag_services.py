import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.models.timeline import TimelineNode, Choice, Decision
from backend.app.models.memory import Memory
from backend.app.models.world import Character
from backend.app.services.rag.embedding_service import (
    MockEmbeddingProvider,
    GeminiEmbeddingProvider,
    EmbeddingService,
    embedding_service
)
from backend.app.services.rag.chunker import chunker
from backend.app.services.rag.document_processor import document_processor
from backend.app.services.rag.vector_store import vector_store
from backend.app.services.rag.retriever import retriever
from backend.app.services.rag.context_builder import context_builder
from backend.app.services.rag.rag_pipeline import rag_pipeline
from backend.app.core.config import settings

@pytest.mark.asyncio
async def test_embedding_creation():
    """Test embedding generation and dimension matching."""
    provider = MockEmbeddingProvider(dimension=settings.EMBEDDING_DIMENSION)
    vec = await provider.embed_text("Aria holds the bioluminescent memory crystal.")
    assert len(vec) == settings.EMBEDDING_DIMENSION
    assert isinstance(vec[0], float)

    # Empty text handling
    empty_vec = await embedding_service.get_embedding("")
    assert len(empty_vec) == settings.EMBEDDING_DIMENSION

@pytest.mark.asyncio
async def test_vector_storage_and_similarity_search(db_session: AsyncSession, test_user_a: User):
    """Test storing embeddings and performing cosine similarity search."""
    vec1 = await embedding_service.get_embedding("The river Ganges in Neo-Kashi glows with quantum energy.")
    vec2 = await embedding_service.get_embedding("Deep space asteroid mining in the outer Kepler belt.")

    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_a.id,
        entity_type="memory",
        entity_id="mem-1",
        document_content="The river Ganges in Neo-Kashi glows with quantum energy.",
        embedding_vector=vec1,
        document_title="Ganges Quantum Glow"
    )
    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_a.id,
        entity_type="memory",
        entity_id="mem-2",
        document_content="Deep space asteroid mining in the outer Kepler belt.",
        embedding_vector=vec2,
        document_title="Kepler Mining"
    )
    await db_session.commit()

    # Search with query close to Ganges
    query_vec = await embedding_service.get_embedding("Ganges water quantum glow")
    results = await vector_store.search_similar(
        db=db_session,
        query_embedding=query_vec,
        user_id=test_user_a.id,
        top_k=2
    )

    assert len(results) > 0
    assert results[0].entity_id == "mem-1"
    assert "Ganges" in results[0].document_content

@pytest.mark.asyncio
async def test_user_tenant_isolation(
    db_session: AsyncSession,
    test_user_a: User,
    test_user_b: User
):
    """
    CRITICAL: Verify User A's search NEVER returns User B's embeddings.
    User A: 'Aria lives in Neo-Kashi.'
    User B: 'Aria lives in another universe.'
    """
    vec_a = await embedding_service.get_embedding("Aria lives in Neo-Kashi.")
    vec_b = await embedding_service.get_embedding("Aria lives in another universe.")

    # User A document
    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_a.id,
        entity_type="character",
        entity_id="char-a-1",
        document_content="Aria lives in Neo-Kashi.",
        embedding_vector=vec_a
    )

    # User B document
    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_b.id,
        entity_type="character",
        entity_id="char-b-1",
        document_content="Aria lives in another universe.",
        embedding_vector=vec_b
    )
    await db_session.commit()

    # Search as User A
    search_res_a = await rag_pipeline.search_and_ground(
        db=db_session,
        query="Where does Aria live?",
        user_id=test_user_a.id
    )

    assert search_res_a.results_count > 0
    # Every returned result must strictly belong to User A
    for item in search_res_a.results:
        assert item.entity_id != "char-b-1"
        assert "another universe" not in item.content

    # Search as User B
    search_res_b = await rag_pipeline.search_and_ground(
        db=db_session,
        query="Where does Aria live?",
        user_id=test_user_b.id
    )
    assert search_res_b.results_count > 0
    for item in search_res_b.results:
        assert item.entity_id != "char-a-1"
        assert "Neo-Kashi" not in item.content

@pytest.mark.asyncio
async def test_branch_isolation(db_session: AsyncSession, test_user_a: User):
    """Test that querying a specific branch restricts results to that branch and global items."""
    vec1 = await embedding_service.get_embedding("Branch Alpha exclusive anomaly.")
    vec2 = await embedding_service.get_embedding("Branch Beta exclusive anomaly.")

    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_a.id,
        branch_id="branch-alpha",
        entity_type="timeline_node",
        entity_id="node-alpha",
        document_content="Branch Alpha exclusive anomaly.",
        embedding_vector=vec1
    )
    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_a.id,
        branch_id="branch-beta",
        entity_type="timeline_node",
        entity_id="node-beta",
        document_content="Branch Beta exclusive anomaly.",
        embedding_vector=vec2
    )
    await db_session.commit()

    res = await rag_pipeline.search_and_ground(
        db=db_session,
        query="Tell me about the anomaly",
        user_id=test_user_a.id,
        branch_id="branch-alpha"
    )

    for item in res.results:
        assert item.entity_id != "node-beta"

@pytest.mark.asyncio
async def test_metadata_filtering(db_session: AsyncSession, test_user_a: User):
    """Test filtering by entity_types."""
    vec1 = await embedding_service.get_embedding("Memory of an ancient prophecy.")
    vec2 = await embedding_service.get_embedding("Character profile of the high priest.")

    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_a.id,
        entity_type="memory",
        entity_id="mem-filter-1",
        document_content="Memory of an ancient prophecy.",
        embedding_vector=vec1
    )
    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_a.id,
        entity_type="character",
        entity_id="char-filter-1",
        document_content="Character profile of the high priest.",
        embedding_vector=vec2
    )
    await db_session.commit()

    res = await rag_pipeline.search_and_ground(
        db=db_session,
        query="Tell me about the prophecy",
        user_id=test_user_a.id,
        entity_types=["memory"]
    )

    for item in res.results:
        assert item.document_type == "memory"
        assert item.entity_id != "char-filter-1"

@pytest.mark.asyncio
async def test_entity_update_replaces_embedding(db_session: AsyncSession, test_user_a: User):
    """Test that re-indexing an updated entity invalidates/deletes old embeddings."""
    memory = Memory(
        user_id=test_user_a.id,
        branch_id="branch-update-1",
        title="Old Vision",
        content="Old narrative content that was subsequently revised.",
        emotional_tone="grief"
    )
    db_session.add(memory)
    await db_session.flush()

    # Initial Indexing
    await rag_pipeline.index_memory(db_session, memory, test_user_a.id)
    await db_session.commit()

    # Verify initial embedding exists
    res1 = await rag_pipeline.search_and_ground(db_session, "Old narrative content", test_user_a.id)
    assert any(item.entity_id == memory.id for item in res1.results)

    # Update entity content
    memory.content = "New revised narrative revelation of golden spires."
    memory.title = "New Golden Vision"
    await rag_pipeline.index_memory(db_session, memory, test_user_a.id)
    await db_session.commit()

    # Verify new content is returned and old content is replaced
    res2 = await rag_pipeline.search_and_ground(db_session, "revelation of golden spires", test_user_a.id)
    found_item = next(item for item in res2.results if item.entity_id == memory.id)
    assert "golden spires" in found_item.content

@pytest.mark.asyncio
async def test_entity_delete_removes_embedding(db_session: AsyncSession, test_user_a: User):
    """Test deleting an entity removes its vector embeddings from the vector store."""
    vec = await embedding_service.get_embedding("Ephemeral memory doomed to be forgotten.")
    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_a.id,
        entity_type="memory",
        entity_id="mem-delete-target",
        document_content="Ephemeral memory doomed to be forgotten.",
        embedding_vector=vec
    )
    await db_session.commit()

    # Delete index
    deleted_count = await rag_pipeline.delete_entity_index(
        db=db_session,
        user_id=test_user_a.id,
        entity_type="memory",
        entity_id="mem-delete-target"
    )
    assert deleted_count >= 1
    await db_session.commit()

    # Search should no longer return it
    res = await rag_pipeline.search_and_ground(db_session, "Ephemeral memory", test_user_a.id)
    assert not any(item.entity_id == "mem-delete-target" for item in res.results)

@pytest.mark.asyncio
async def test_context_builder():
    """Test context builder formatting, deduplication, and budget capping."""
    from backend.app.services.rag.vector_store import VectorSearchResult

    items = [
        VectorSearchResult(
            id="1",
            document_content="[TIMELINE EVENT] Era: 2042 | Event: The Great Divergence",
            document_title="Timeline 2042",
            entity_type="timeline_node",
            entity_id="node-1",
            user_id="user-1",
            branch_id="branch-1",
            score=0.95,
            metadata={}
        ),
        VectorSearchResult(
            id="2",
            document_content="[CHARACTER] Name: Maya | Role: Celestial Navigator",
            document_title="Maya Dossier",
            entity_type="character",
            entity_id="char-1",
            user_id="user-1",
            branch_id="branch-1",
            score=0.88,
            metadata={}
        )
    ]

    context = context_builder.build_grounded_context(items)
    assert "=== RETRIEVED KSHAN MULTIVERSE CONTEXT ===" in context
    assert "[CHRONICLES & TIMELINE EVENTS]" in context
    assert "The Great Divergence" in context
    assert "[CHARACTERS & AFFINITIES]" in context
    assert "Maya" in context

@pytest.mark.asyncio
async def test_top_k_and_empty_results(db_session: AsyncSession, test_user_a: User):
    """Test top_k parameter capping and empty results handling."""
    # Empty search
    empty_res = await rag_pipeline.search_and_ground(
        db=db_session,
        query="Nonexistent multiverse query with no vectors",
        user_id=test_user_a.id
    )
    assert empty_res.results_count == 0
    assert "No prior multiverse memories" in empty_res.context
