import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_and_get_scenarios(client: AsyncClient):
    # 1. List scenarios (should auto-seed if empty)
    res = await client.get("/api/v1/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) >= 3

    # Check structure
    first = scenarios[0]
    assert "id" in first
    assert "slug" in first
    assert "title" in first
    assert "premise" in first
    assert "initial_kshan_moment" in first

    # 2. Get scenario by ID and slug
    res_id = await client.get(f"/api/v1/scenarios/{first['id']}")
    assert res_id.status_code == 200
    assert res_id.json()["title"] == first["title"]

    res_slug = await client.get(f"/api/v1/scenarios/{first['slug']}")
    assert res_slug.status_code == 200
    assert res_slug.json()["id"] == first["id"]
