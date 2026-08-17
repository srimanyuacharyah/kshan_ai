import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.services.rag.embedding_service import embedding_service
from backend.app.services.rag.vector_store import vector_store

@pytest.mark.asyncio
async def test_rag_api_search_authenticated(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_a: User,
    auth_headers_user_a: dict
):
    """Test protected POST /api/v1/rag/search endpoint with valid JWT."""
    # Seed a document for User A
    vec = await embedding_service.get_embedding("The ancient library beneath Varanasi holds lost star charts.")
    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_a.id,
        entity_type="world",
        entity_id="loc-varanasi-lib",
        document_content="The ancient library beneath Varanasi holds lost star charts.",
        embedding_vector=vec,
        document_title="Varanasi Star Library"
    )
    await db_session.commit()

    # Query API
    payload = {
        "query": "Where are the star charts stored?",
        "top_k": 3
    }
    response = await client.post("/api/v1/rag/search", json=payload, headers=auth_headers_user_a)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["results_count"] > 0
    assert "star charts" in data["data"]["context"]
    assert "retrieval_time_ms" in data["data"]

@pytest.mark.asyncio
async def test_rag_api_search_unauthorized(client: AsyncClient):
    """Test rejection with missing or invalid JWT."""
    payload = {"query": "What happened to my timeline?"}
    
    # Missing JWT
    res1 = await client.post("/api/v1/rag/search", json=payload)
    assert res1.status_code == 401

    # Invalid JWT
    headers = {"Authorization": "Bearer invalid_malformed_token"}
    res2 = await client.post("/api/v1/rag/search", json=payload, headers=headers)
    assert res2.status_code == 401

@pytest.mark.asyncio
async def test_rag_api_search_empty_query(
    client: AsyncClient,
    auth_headers_user_a: dict
):
    """Test 422 Unprocessable Entity on empty query string."""
    payload = {"query": "   "}
    response = await client.post("/api/v1/rag/search", json=payload, headers=auth_headers_user_a)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_rag_api_cross_user_isolation(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_a: User,
    test_user_b: User,
    auth_headers_user_a: dict,
    auth_headers_user_b: dict
):
    """Verify that User A's API request never receives User B's indexed secrets."""
    vec_b = await embedding_service.get_embedding("Classified Secret Code 99482 for User B.")
    await vector_store.add_embedding(
        db=db_session,
        user_id=test_user_b.id,
        entity_type="memory",
        entity_id="mem-secret-b",
        document_content="Classified Secret Code 99482 for User B.",
        embedding_vector=vec_b
    )
    await db_session.commit()

    # User A searches for secret code
    payload = {"query": "Classified Secret Code 99482"}
    res_a = await client.post("/api/v1/rag/search", json=payload, headers=auth_headers_user_a)
    assert res_a.status_code == 200
    data_a = res_a.json()["data"]
    assert data_a["results_count"] == 0
    assert "99482" not in data_a["context"]

    # User B searches for secret code
    res_b = await client.post("/api/v1/rag/search", json=payload, headers=auth_headers_user_b)
    assert res_b.status_code == 200
    data_b = res_b.json()["data"]
    assert data_b["results_count"] > 0
    assert "99482" in data_b["context"]
