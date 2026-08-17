import pytest
from httpx import AsyncClient
from backend.app.models.user import User

@pytest.mark.asyncio
async def test_user_tenant_isolation(
    client: AsyncClient,
    test_user_a: User,
    test_user_b: User,
    auth_headers_user_a: dict,
    auth_headers_user_b: dict
):
    """Verify that User A cannot access or mutate User B's identity or private records."""
    # 1. User A checks their profile
    res_a = await client.get("/api/v1/auth/me", headers=auth_headers_user_a)
    assert res_a.status_code == 200
    data_a = res_a.json()["data"]
    assert data_a["id"] == test_user_a.id
    assert data_a["email"] == "voyager.a@kshan.ai"

    # 2. User B checks their profile
    res_b = await client.get("/api/v1/auth/me", headers=auth_headers_user_b)
    assert res_b.status_code == 200
    data_b = res_b.json()["data"]
    assert data_b["id"] == test_user_b.id
    assert data_b["email"] == "voyager.b@kshan.ai"

    # 3. User A updates their profile
    update_payload = {"display_name": "Updated Alpha Commander"}
    update_res = await client.put("/api/v1/auth/me/profile", json=update_payload, headers=auth_headers_user_a)
    assert update_res.status_code == 200
    assert update_res.json()["data"]["profile"]["display_name"] == "Updated Alpha Commander"

    # 4. Verify User B's profile was not affected
    res_b_check = await client.get("/api/v1/auth/me", headers=auth_headers_user_b)
    assert res_b_check.json()["data"]["profile"]["display_name"] == "Voyager Beta"

@pytest.mark.asyncio
async def test_unauthenticated_requests_are_rejected(client: AsyncClient):
    """Ensure protected endpoints return 401 Unauthorized without a valid Bearer token."""
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401
    
    invalid_headers = {"Authorization": "Bearer invalid_malformed_token_multiverse"}
    res_invalid = await client.get("/api/v1/auth/me", headers=invalid_headers)
    assert res_invalid.status_code == 401
