import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.models.scenario import Scenario, FutureProfile
from backend.app.models.multiverse import RealityBranch
from backend.app.models.timeline import TimelineNode, Choice
from backend.app.models.world import World
from backend.app.core.security import create_access_token

@pytest_asyncio.fixture(scope="function")
async def setup_api_multiverse(
    db_session: AsyncSession,
    test_user_a: User,
    test_user_b: User
):
    """Seed test multiverse entities for API tests."""
    scenario = Scenario(
        title="Neo-Kashi Cyber-Mythic API",
        slug="neo-kashi-api",
        genre="Cyber-Mythic",
        tagline="One Moment. Infinite Lives.",
        premise="Neo-Kashi floating megacity.",
        initial_kshan_moment="Memory crystal drops."
    )
    db_session.add(scenario)
    await db_session.flush()

    world = World(
        scenario_id=scenario.id,
        name="Neo-Kashi 2042 API",
        cosmos_type="Floating Megacity",
        lore_chronicle="Lore chronicle details."
    )
    db_session.add(world)
    await db_session.flush()

    profile_a = FutureProfile(
        user_id=test_user_a.id,
        scenario_id=scenario.id,
        title="User A API Profile",
        archetype="The Void Walker"
    )
    db_session.add(profile_a)
    await db_session.flush()

    branch_a = RealityBranch(
        user_id=test_user_a.id,
        future_profile_id=profile_a.id,
        branch_name="Branch Prime API",
        branch_code="TL-API-01"
    )
    db_session.add(branch_a)
    await db_session.flush()

    node_a = TimelineNode(
        user_id=test_user_a.id,
        branch_id=branch_a.id,
        depth_level=0,
        era_year="Year 2042",
        story_text="API test node content."
    )
    db_session.add(node_a)
    await db_session.flush()

    choice_a = Choice(
        node_id=node_a.id,
        choice_label="Option 1",
        choice_description="Option 1 description"
    )
    db_session.add(choice_a)

    # User B branch
    branch_b = RealityBranch(
        user_id=test_user_b.id,
        branch_name="User B Private Branch",
        branch_code="TL-API-99"
    )
    db_session.add(branch_b)
    await db_session.commit()

    return {
        "scenario": scenario,
        "world": world,
        "branch_a": branch_a,
        "node_a": node_a,
        "choice_a": choice_a,
        "branch_b": branch_b
    }

@pytest.mark.asyncio
async def test_api_generate_story(
    client: AsyncClient,
    auth_headers_user_a: dict,
    setup_api_multiverse: dict
):
    """Test POST /api/v1/ai/story endpoint."""
    entities = setup_api_multiverse
    payload = {
        "scenario_id": entities["scenario"].id,
        "branch_id": entities["branch_a"].id,
        "prompt_seed": "The rain begins to fall on the neon ghauts."
    }
    response = await client.post("/api/v1/ai/story", json=payload, headers=auth_headers_user_a)
    assert response.status_code == 200
    data = response.json()
    assert "narrative" in data
    assert len(data["choices"]) == 3

@pytest.mark.asyncio
async def test_api_generate_branch(
    client: AsyncClient,
    auth_headers_user_a: dict,
    setup_api_multiverse: dict
):
    """Test POST /api/v1/ai/branch endpoint."""
    entities = setup_api_multiverse
    payload = {
        "scenario_id": entities["scenario"].id,
        "branch_id": entities["branch_a"].id,
        "timeline_node_id": entities["node_a"].id,
        "intention": "Survive the ambush"
    }
    response = await client.post("/api/v1/ai/branch", json=payload, headers=auth_headers_user_a)
    assert response.status_code == 200
    data = response.json()
    assert len(data["choices"]) == 3

@pytest.mark.asyncio
async def test_api_generate_future_you(
    client: AsyncClient,
    auth_headers_user_a: dict,
    setup_api_multiverse: dict
):
    """Test POST /api/v1/ai/future-you endpoint."""
    entities = setup_api_multiverse
    payload = {
        "scenario_id": entities["scenario"].id,
        "branch_id": entities["branch_a"].id,
        "user_question": "What becomes of our quest in the upper spires?"
    }
    response = await client.post("/api/v1/ai/future-you", json=payload, headers=auth_headers_user_a)
    assert response.status_code == 200
    data = response.json()
    assert data["is_fictional_simulation"] is True
    assert "identity" in data
    assert "message_to_present_self" in data

@pytest.mark.asyncio
async def test_api_cross_user_isolation_rejected(
    client: AsyncClient,
    auth_headers_user_a: dict,
    setup_api_multiverse: dict
):
    """
    SECURITY TEST: User A attempts AI generation using User B's branch.
    Must return 403 Forbidden.
    """
    entities = setup_api_multiverse
    payload = {
        "scenario_id": entities["scenario"].id,
        "branch_id": entities["branch_b"].id, # User B's branch!
        "prompt_seed": "Infiltrate"
    }
    response = await client.post("/api/v1/ai/story", json=payload, headers=auth_headers_user_a)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_api_unauthenticated_request_rejected(
    client: AsyncClient,
    setup_api_multiverse: dict
):
    """Verify requests lacking Authorization header are rejected."""
    entities = setup_api_multiverse
    payload = {
        "scenario_id": entities["scenario"].id,
        "branch_id": entities["branch_a"].id
    }
    response = await client.post("/api/v1/ai/story", json=payload)
    assert response.status_code in [401, 403, 422]
