import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_liveness_probe(client: AsyncClient):
    """Test health liveness probe."""
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "live"
    assert data["service"] == "KSHAN Multiverse Engine"

@pytest.mark.asyncio
async def test_readiness_probe(client: AsyncClient):
    """Test health readiness probe and configuration validation."""
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ready", "degraded"]
    assert "embedding_dimension" in data
    assert data["embedding_dimension"] == 768
