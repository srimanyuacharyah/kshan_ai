import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    """Test full registration and login flow with JWT token issuance."""
    # 1. Register
    register_payload = {
        "email": "traveler@kshan.ai",
        "username": "traveler_one",
        "password": "SecurePassword123!",
        "display_name": "Multiverse Traveler"
    }
    response = await client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == "traveler@kshan.ai"
    assert data["data"]["user"]["username"] == "traveler_one"
    assert "access_token" in data["data"]["token"]
    
    # 2. Duplicate registration rejection
    dup_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert dup_response.status_code == 400

    # 3. Login
    login_payload = {
        "email": "traveler@kshan.ai",
        "password": "SecurePassword123!"
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["success"] is True
    token = login_data["data"]["token"]["access_token"]
    
    # 4. Access protected /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_response = await client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["data"]["username"] == "traveler_one"
    assert me_data["data"]["profile"]["display_name"] == "Multiverse Traveler"

@pytest.mark.asyncio
async def test_invalid_login_credentials(client: AsyncClient):
    """Test rejection on incorrect password or nonexistent user."""
    login_payload = {
        "email": "nonexistent@kshan.ai",
        "password": "WrongPassword!"
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
