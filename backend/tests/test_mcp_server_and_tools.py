import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.models.scenario import Scenario, FutureProfile
from backend.app.models.multiverse import RealityBranch, MultiverseState
from backend.app.models.timeline import TimelineNode, Choice, Decision
from backend.app.models.world import World, Character, Location
from backend.app.models.memory import Memory
from backend.app.core.security import create_access_token
from backend.app.services.mcp import (
    mcp_client,
    mcp_manager,
    MCPAuthorizationError,
    MCPToolNotFoundError,
    MCPToolExecutionError
)

@pytest.fixture
async def setup_multiverse_entities(
    db_session: AsyncSession,
    test_user_a: User,
    test_user_b: User
):
    """Seed comprehensive multiverse entities for both User A and User B."""
    # 1. Scenario & Worlds
    scenario_a = Scenario(
        title="Neo-Kashi Cyber-Mythic",
        slug="neo-kashi-a",
        genre="Cyber-Mythic",
        tagline="Where quantum circuits meet ancient sacred rivers.",
        premise="Neo-Kashi floats above subterranean riverbeds.",
        initial_kshan_moment="The metro doors close; a glowing memory crystal drops."
    )
    scenario_b = Scenario(
        title="The Quantum Citadel of User B",
        slug="citadel-b",
        genre="Cosmic Sci-Fi",
        tagline="A dying star powers the central reality gate.",
        premise="Deep stellar forge.",
        initial_kshan_moment="The reactor alarm sounds."
    )
    db_session.add_all([scenario_a, scenario_b])
    await db_session.flush()

    world_a = World(
        scenario_id=scenario_a.id,
        name="Neo-Kashi 2042",
        cosmos_type="Floating Megacity",
        lore_chronicle="Rebuilt after the Great Resonance Shift."
    )
    db_session.add(world_a)
    await db_session.flush()

    char_a = Character(
        world_id=world_a.id,
        name="Aria / The Memory Weaver",
        role="Companion",
        faction="Undercity Guild",
        backstory="Smuggler of forgotten pre-divergence memories.",
        dialogue_style="Cryptic and observant"
    )
    loc_a = Location(
        world_id=world_a.id,
        name="Platform 108 - Varanasi Hub",
        realm_zone="Undercity",
        description="Neon mist cascades over ancient stone ghauts.",
        danger_rating=0.4
    )
    db_session.add_all([char_a, loc_a])

    # 2. User A Profile, Branch, State, Timeline & Decision
    profile_a = FutureProfile(
        user_id=test_user_a.id,
        scenario_id=scenario_a.id,
        title="The Memory Shard Divergence",
        archetype="The Void Walker"
    )
    db_session.add(profile_a)
    await db_session.flush()

    branch_a = RealityBranch(
        user_id=test_user_a.id,
        future_profile_id=profile_a.id,
        branch_name="Branch Prime: The Subterranean Leap",
        branch_code="TL-NK-01",
        entropy_level=0.2,
        resonance_score=0.8
    )
    db_session.add(branch_a)
    await db_session.flush()

    state_a = MultiverseState(
        branch_id=branch_a.id,
        timeline_era="Year 2042",
        world_coherence=0.95
    )
    node_a = TimelineNode(
        user_id=test_user_a.id,
        branch_id=branch_a.id,
        depth_level=0,
        era_year="Year 2042",
        story_text="You pick up the crystal. A surge of cyan energy flows through your fingertips.",
        sensory_cue="Ozone and burning sandalwood incense",
        audio_ambiance="cosmic_drone",
        butterfly_impact="Awakens ancient dormant cyber-conduits"
    )
    db_session.add_all([state_a, node_a])
    await db_session.flush()

    choice_a = Choice(
        node_id=node_a.id,
        choice_label="Sync neural interface with the crystal",
        choice_description="Directly channel the crystal memory into your neural link.",
        risk_level="moderate"
    )
    db_session.add(choice_a)
    await db_session.flush()

    decision_a = Decision(
        user_id=test_user_a.id,
        node_id=node_a.id,
        chosen_choice_id=choice_a.id,
        rationale="Knowledge over fear."
    )
    memory_a = Memory(
        user_id=test_user_a.id,
        branch_id=branch_a.id,
        node_id=node_a.id,
        title="The First Cyan Shard",
        content="A memory of ancient Varanasi bathed in starlight.",
        emotional_tone="epiphany"
    )
    db_session.add_all([decision_a, memory_a])

    # 3. User B Profile, Branch, State, Timeline (Private to User B)
    profile_b = FutureProfile(
        user_id=test_user_b.id,
        scenario_id=scenario_b.id,
        title="User B Secret Protocol",
        archetype="The Citadel Warden"
    )
    db_session.add(profile_b)
    await db_session.flush()

    branch_b = RealityBranch(
        user_id=test_user_b.id,
        future_profile_id=profile_b.id,
        branch_name="Branch Beta: Private Reality",
        branch_code="TL-BETA-99",
        entropy_level=0.7
    )
    db_session.add(branch_b)
    await db_session.flush()

    node_b = TimelineNode(
        user_id=test_user_b.id,
        branch_id=branch_b.id,
        depth_level=0,
        era_year="Year 3099",
        story_text="User B confidential timeline event inside the Citadel Core."
    )
    memory_b = Memory(
        user_id=test_user_b.id,
        branch_id=branch_b.id,
        title="User B Top Secret Memory",
        content="Access code 987654321 for Citadel vault.",
        emotional_tone="dread"
    )
    db_session.add_all([node_b, memory_b])
    await db_session.commit()

    return {
        "scenario_a": scenario_a,
        "world_a": world_a,
        "char_a": char_a,
        "loc_a": loc_a,
        "branch_a": branch_a,
        "node_a": node_a,
        "memory_a": memory_a,
        "scenario_b": scenario_b,
        "branch_b": branch_b,
        "node_b": node_b,
        "memory_b": memory_b
    }

@pytest.mark.asyncio
async def test_mcp_tool_discovery():
    """Verify all 12 KSHAN MCP tools are registered and discoverable."""
    tools = await mcp_client.list_tools()
    tool_names = {t.name for t in tools}
    
    expected_tools = {
        "get_current_world",
        "get_timeline",
        "get_timeline_node",
        "get_character",
        "get_location",
        "search_memories",
        "get_recent_decisions",
        "get_branch_state",
        "get_world_events",
        "get_story_context",
        "create_memory",
        "create_timeline_event"
    }
    for expected in expected_tools:
        assert expected in tool_names, f"Expected tool '{expected}' missing from MCP server."

@pytest.mark.asyncio
async def test_mcp_read_tools(
    setup_multiverse_entities: dict,
    test_user_a: User
):
    """Test read tools: get_current_world, get_timeline, get_character, get_location, get_branch_state."""
    token = create_access_token(test_user_a.id)
    entities = setup_multiverse_entities

    # 1. get_current_world
    res_world = await mcp_client.call_tool(
        "get_current_world",
        {"scenario_id": entities["scenario_a"].id},
        auth_token=token
    )
    assert res_world.success is True
    assert res_world.data["name"] == "Neo-Kashi 2042"

    # 2. get_timeline
    res_tl = await mcp_client.call_tool(
        "get_timeline",
        {"branch_id": entities["branch_a"].id},
        auth_token=token
    )
    assert res_tl.success is True
    assert res_tl.data["nodes_count"] >= 1
    assert res_tl.data["nodes"][0]["era_year"] == "Year 2042"

    # 3. get_character
    res_char = await mcp_client.call_tool(
        "get_character",
        {"character_id": entities["char_a"].id},
        auth_token=token
    )
    assert res_char.success is True
    assert "Aria" in res_char.data["name"]

    # 4. get_location
    res_loc = await mcp_client.call_tool(
        "get_location",
        {"location_id": entities["loc_a"].id},
        auth_token=token
    )
    assert res_loc.success is True
    assert "Varanasi" in res_loc.data["name"]

    # 5. get_branch_state
    res_state = await mcp_client.call_tool(
        "get_branch_state",
        {"branch_id": entities["branch_a"].id},
        auth_token=token
    )
    assert res_state.success is True
    assert res_state.data["branch_code"] == "TL-NK-01"

@pytest.mark.asyncio
async def test_mcp_rag_integration_search_memories(
    db_session: AsyncSession,
    setup_multiverse_entities: dict,
    test_user_a: User
):
    """
    RAG + MCP Integration Test:
    Verify search_memories tool invokes the RAG pipeline and retrieves grounded memories.
    """
    from backend.app.services.rag.rag_pipeline import rag_pipeline
    entities = setup_multiverse_entities
    token = create_access_token(test_user_a.id)

    # Index Memory A into RAG pgvector store
    await rag_pipeline.index_memory(db_session, entities["memory_a"], test_user_a.id)
    await db_session.commit()

    # Call search_memories MCP tool
    res = await mcp_client.call_tool(
        "search_memories",
        {
            "query": "Varanasi starlight cyan shard",
            "branch_id": entities["branch_a"].id,
            "top_k": 3
        },
        auth_token=token
    )
    assert res.success is True
    assert res.data["results_count"] > 0
    assert "Cyan Shard" in res.data["grounded_context"] or "Varanasi" in res.data["grounded_context"]

@pytest.mark.asyncio
async def test_mcp_story_context_aggregator(
    db_session: AsyncSession,
    setup_multiverse_entities: dict,
    test_user_a: User
):
    """Test get_story_context combining timeline, branch state, decisions, and RAG."""
    from backend.app.services.rag.rag_pipeline import rag_pipeline
    entities = setup_multiverse_entities
    token = create_access_token(test_user_a.id)

    await rag_pipeline.index_timeline_node(db_session, entities["node_a"], test_user_a.id)
    await db_session.commit()

    res = await mcp_client.call_tool(
        "get_story_context",
        {
            "branch_id": entities["branch_a"].id,
            "query": "What are my immediate choices and surroundings?"
        },
        auth_token=token
    )
    assert res.success is True
    assert res.data["branch_summary"]["branch_code"] == "TL-NK-01"
    assert res.data["latest_node"]["era_year"] == "Year 2042"
    assert "recent_decisions" in res.data

@pytest.mark.asyncio
async def test_mcp_write_tool_with_rag_indexing(
    setup_multiverse_entities: dict,
    test_user_a: User
):
    """
    Test write tool create_memory:
    1. Calls MCP create_memory
    2. Writes to PostgreSQL
    3. Auto-indexes into RAG pgvector store
    4. Calls search_memories to verify retrieval
    """
    entities = setup_multiverse_entities
    token = create_access_token(test_user_a.id)

    # 1. Create Memory via MCP
    create_res = await mcp_client.call_tool(
        "create_memory",
        {
            "branch_id": entities["branch_a"].id,
            "title": "Quantum Epiphany of the Ganges",
            "content": "Realization that the river connects infinite divergent parallel timelines.",
            "emotional_tone": "triumph"
        },
        auth_token=token
    )
    assert create_res.success is True
    assert create_res.data["success"] is True
    assert "memory_id" in create_res.data

    # 2. Verify search_memories retrieves the newly created and indexed memory
    search_res = await mcp_client.call_tool(
        "search_memories",
        {
            "branch_id": entities["branch_a"].id,
            "query": "river connects infinite divergent parallel timelines"
        },
        auth_token=token
    )
    assert search_res.success is True
    assert search_res.data["results_count"] > 0
    assert any("Quantum Epiphany" in m["title"] for m in search_res.data["memories"])

@pytest.mark.asyncio
async def test_mcp_cross_user_security_isolation(
    setup_multiverse_entities: dict,
    test_user_a: User,
    test_user_b: User
):
    """
    CRITICAL SECURITY TEST:
    Authenticate as User A.
    Attempt to access User B's branch/timeline/memories.
    MUST fail with MCPAuthorizationError or return zero unauthorized data.
    """
    token_a = create_access_token(test_user_a.id)
    entities = setup_multiverse_entities
    user_b_branch_id = entities["branch_b"].id

    # 1. User A tries to get User B's timeline
    with pytest.raises(MCPAuthorizationError):
        await mcp_client.call_tool(
            "get_timeline",
            {"branch_id": user_b_branch_id},
            auth_token=token_a
        )

    # 2. User A tries to get User B's branch state
    with pytest.raises(MCPAuthorizationError):
        await mcp_client.call_tool(
            "get_branch_state",
            {"branch_id": user_b_branch_id},
            auth_token=token_a
        )

    # 3. User A tries to search User B's branch memories
    with pytest.raises(MCPAuthorizationError):
        await mcp_client.call_tool(
            "search_memories",
            {"branch_id": user_b_branch_id, "query": "Citadel vault access code"},
            auth_token=token_a
        )

    # 4. User A tries to create memory in User B's branch
    with pytest.raises(MCPAuthorizationError):
        await mcp_client.call_tool(
            "create_memory",
            {
                "branch_id": user_b_branch_id,
                "title": "Malicious Injected Memory",
                "content": "Compromised content."
            },
            auth_token=token_a
        )

@pytest.mark.asyncio
async def test_mcp_unauthenticated_request_rejected():
    """Verify that requests without an auth_token or with invalid tokens are rejected."""
    with pytest.raises(MCPAuthorizationError):
        await mcp_client.call_tool(
            "get_timeline",
            {"branch_id": "any-branch-id"},
            auth_token=""
        )

    with pytest.raises(MCPAuthorizationError):
        await mcp_client.call_tool(
            "get_timeline",
            {"branch_id": "any-branch-id"},
            auth_token="Bearer invalid_malformed_token"
        )

@pytest.mark.asyncio
async def test_mcp_resources_and_prompts(
    setup_multiverse_entities: dict,
    test_user_a: User
):
    """Test reading MCP resources and retrieving MCP prompt templates."""
    token = create_access_token(test_user_a.id)
    entities = setup_multiverse_entities

    # 1. Read timeline resource
    tl_uri = f"kshan://timeline/{entities['branch_a'].id}"
    tl_text = await mcp_client.read_resource(tl_uri, auth_token=token)
    assert "KSHAN TIMELINE CHRONICLE" in tl_text
    assert "Year 2042" in tl_text

    # 2. Get prompt
    from mcp_server.app.server import mcp_server
    prompt_res = await mcp_server.get_prompt(
        "future_you_context",
        arguments={
            "scenario_id": entities["scenario_a"].id,
            "branch_id": entities["branch_a"].id,
            "query": "What is my next choice?"
        }
    )
    assert prompt_res is not None

@pytest.mark.asyncio
async def test_mcp_client_health_check():
    """Test MCP manager health check diagnostic."""
    health = await mcp_manager.get_health()
    assert health.connected is True
    assert health.server_name == "KSHAN Multiverse Context Server"
    assert health.tools_count >= 12
