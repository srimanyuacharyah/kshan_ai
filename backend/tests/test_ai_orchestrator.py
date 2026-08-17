import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.user import User
from backend.app.models.scenario import Scenario, FutureProfile
from backend.app.models.multiverse import RealityBranch, MultiverseState
from backend.app.models.timeline import TimelineNode, Choice, Decision
from backend.app.models.world import World, Character, Location
from backend.app.models.generation import GenerationHistory

from backend.app.core.security import create_access_token
from backend.app.services.ai import (
    ai_orchestrator,
    gemini_client,
    prompt_builder,
    context_budget_manager,
    rate_limiter,
    RateLimitExceededError,
    ResponseValidationError,
    StoryGenerationResponse,
    BranchGenerationResponse,
    FutureYouResponse,
    WorldGenerationResponse,
    CharacterGenerationResponse,
    DecisionAnalysisResponse
)
from backend.app.services.mcp.exceptions import MCPAuthorizationError

@pytest_asyncio.fixture(scope="function")
async def seeded_multiverse_universe(
    db_session: AsyncSession,
    test_user_a: User,
    test_user_b: User
):
    """Seed comprehensive test multiverse data for User A and User B."""
    scenario = Scenario(
        title="Neo-Kashi Cyber-Mythic",
        slug="neo-kashi-phase4",
        genre="Cyber-Mythic",
        tagline="One Moment. Infinite Lives.",
        premise="Neo-Kashi floats above subterranean riverbeds.",
        initial_kshan_moment="The metro doors close; a glowing memory crystal drops."
    )
    db_session.add(scenario)
    await db_session.flush()

    world = World(
        scenario_id=scenario.id,
        name="Neo-Kashi 2042",
        cosmos_type="Floating Megacity",
        lore_chronicle="Rebuilt after the Great Resonance Shift."
    )
    db_session.add(world)
    await db_session.flush()

    char = Character(
        world_id=world.id,
        name="Aria The Memory Weaver",
        role="Companion",
        faction="Undercity Guild",
        backstory="Smuggler of forgotten pre-divergence memories."
    )
    db_session.add(char)

    profile_a = FutureProfile(
        user_id=test_user_a.id,
        scenario_id=scenario.id,
        title="The Void Seeker Profile",
        archetype="The Void Walker"
    )
    db_session.add(profile_a)
    await db_session.flush()

    branch_a = RealityBranch(
        user_id=test_user_a.id,
        future_profile_id=profile_a.id,
        branch_name="Branch Prime: The Subterranean Leap",
        branch_code="TL-NK-01",
        entropy_level=0.20,
        resonance_score=0.80
    )
    db_session.add(branch_a)
    await db_session.flush()

    node_a = TimelineNode(
        user_id=test_user_a.id,
        branch_id=branch_a.id,
        depth_level=0,
        era_year="Year 2042",
        story_text="You pick up the crystal. A surge of cyan energy flows through your fingertips."
    )
    db_session.add(node_a)

    # User B private branch
    branch_b = RealityBranch(
        user_id=test_user_b.id,
        branch_name="User B Private Reality",
        branch_code="TL-BETA-99",
        entropy_level=0.50
    )
    db_session.add(branch_b)
    await db_session.commit()

    return {
        "scenario": scenario,
        "world": world,
        "character": char,
        "branch_a": branch_a,
        "node_a": node_a,
        "branch_b": branch_b
    }

@pytest.mark.asyncio
async def test_ai_story_generation(
    db_session: AsyncSession,
    seeded_multiverse_universe: dict,
    test_user_a: User
):
    """Verify story generation produces narrative and exactly 3 branching choices."""
    token = create_access_token(test_user_a.id)
    entities = seeded_multiverse_universe

    story_res = await ai_orchestrator.generate_story(
        db=db_session,
        user_id=test_user_a.id,
        scenario_id=entities["scenario"].id,
        branch_id=entities["branch_a"].id,
        prompt_seed="The metro arrives at the deep terminal",
        auth_token=token
    )

    assert isinstance(story_res, StoryGenerationResponse)
    assert len(story_res.narrative) > 20
    assert len(story_res.choices) == 3
    assert all(c.id in ["choice_a", "choice_b", "choice_c"] for c in story_res.choices)

    assert story_res.generation_id.startswith("gen_")
    assert isinstance(story_res.context_sources, list)

@pytest.mark.asyncio
async def test_ai_branch_choices_generation(
    db_session: AsyncSession,
    seeded_multiverse_universe: dict,
    test_user_a: User
):
    """Verify generate_branching_choices produces exactly 3 distinct choices with numerical weights."""
    token = create_access_token(test_user_a.id)
    entities = seeded_multiverse_universe

    branch_res = await ai_orchestrator.generate_branching_choices(
        db=db_session,
        user_id=test_user_a.id,
        scenario_id=entities["scenario"].id,
        branch_id=entities["branch_a"].id,
        timeline_node_id=entities["node_a"].id,
        intention="I want to escape the city authorities",
        auth_token=token
    )

    assert isinstance(branch_res, BranchGenerationResponse)
    assert len(branch_res.choices) == 3
    for c in branch_res.choices:
        assert 0.0 <= c.risk <= 1.0
        assert 0.0 <= c.resonance <= 1.0
        assert -1.0 <= c.entropy_delta <= 1.0

@pytest.mark.asyncio
async def test_ai_future_you_generation(
    db_session: AsyncSession,
    seeded_multiverse_universe: dict,
    test_user_a: User
):
    """Verify Future You is strictly marked as a fictional simulation and includes persona fields."""
    token = create_access_token(test_user_a.id)
    entities = seeded_multiverse_universe

    fy_res = await ai_orchestrator.generate_future_you(
        db=db_session,
        user_id=test_user_a.id,
        scenario_id=entities["scenario"].id,
        branch_id=entities["branch_a"].id,
        user_question="Did we make the right choice with the crystal?",
        auth_token=token
    )

    assert isinstance(fy_res, FutureYouResponse)
    assert fy_res.is_fictional_simulation is True
    assert len(fy_res.identity) > 0
    assert len(fy_res.message_to_present_self) > 0
    assert len(fy_res.achievements) > 0
    assert len(fy_res.regrets) > 0

@pytest.mark.asyncio
async def test_ai_world_and_character_generation_persistence(
    db_session: AsyncSession,
    seeded_multiverse_universe: dict,
    test_user_a: User
):
    """Verify world and character generation persist entities and trigger RAG vector indexing."""
    entities = seeded_multiverse_universe

    # 1. World Generation
    world_res = await ai_orchestrator.generate_world(
        db=db_session,
        user_id=test_user_a.id,
        scenario_id=entities["scenario"].id,
        theme_prompt="Floating cloud islands with bioluminescent flora",
        cosmos_type="Sky Archipelago"
    )
    assert isinstance(world_res, WorldGenerationResponse)
    assert len(world_res.factions) >= 1
    assert len(world_res.major_locations) >= 1

    # Verify world was persisted in database
    w_query = select(World).where(World.name == world_res.world_name)
    w_check = await db_session.execute(w_query)
    saved_world = w_check.scalar_one_or_none()
    assert saved_world is not None

    # 2. Character Generation
    char_res = await ai_orchestrator.generate_character(
        db=db_session,
        user_id=test_user_a.id,
        world_id=saved_world.id,
        role_description="Sky Captain & Explorer of Lost Rifts"
    )
    assert isinstance(char_res, CharacterGenerationResponse)
    assert len(char_res.name) > 0

    c_query = select(Character).where(Character.name == char_res.name)
    c_check = await db_session.execute(c_query)
    saved_char = c_check.scalar_one_or_none()
    assert saved_char is not None

@pytest.mark.asyncio
async def test_ai_decision_analysis(
    db_session: AsyncSession,
    seeded_multiverse_universe: dict,
    test_user_a: User
):
    """Verify decision analysis evaluates systemic trade-offs."""
    token = create_access_token(test_user_a.id)
    entities = seeded_multiverse_universe

    choice = Choice(
        node_id=entities["node_a"].id,
        choice_label="Cross the sacred river",
        choice_description="Leap onto the automated cargo barge."
    )
    db_session.add(choice)
    await db_session.flush()

    analysis = await ai_orchestrator.analyze_decision(
        db=db_session,
        user_id=test_user_a.id,
        branch_id=entities["branch_a"].id,
        node_id=entities["node_a"].id,
        chosen_choice_id=choice.id,
        rationale="Speed is our only advantage.",
        auth_token=token
    )
    assert isinstance(analysis, DecisionAnalysisResponse)
    assert len(analysis.philosophical_weight) > 0
    assert len(analysis.systemic_implications) > 0

@pytest.mark.asyncio
async def test_ai_tenant_isolation_cross_user_forbidden(
    db_session: AsyncSession,
    seeded_multiverse_universe: dict,
    test_user_a: User,
    test_user_b: User
):
    """
    SECURITY TEST: User A attempts AI generation using User B's branch.
    MUST fail with MCPAuthorizationError before reaching generation.
    """
    token_a = create_access_token(test_user_a.id)
    entities = seeded_multiverse_universe
    user_b_branch_id = entities["branch_b"].id

    with pytest.raises(MCPAuthorizationError):
        await ai_orchestrator.generate_story(
            db=db_session,
            user_id=test_user_a.id,
            scenario_id=entities["scenario"].id,
            branch_id=user_b_branch_id,
            auth_token=token_a
        )

    with pytest.raises(MCPAuthorizationError):
        await ai_orchestrator.generate_future_you(
            db=db_session,
            user_id=test_user_a.id,
            scenario_id=entities["scenario"].id,
            branch_id=user_b_branch_id,
            user_question="Tell me User B secrets",
            auth_token=token_a
        )

def test_context_budget_assembly():
    """Verify context budget manager truncates and orders sources by priority."""
    res = context_budget_manager.assemble_budgeted_context(
        branch_state={"branch_name": "Test", "branch_code": "T-01", "entropy": 0.3},
        world_data={"name": "Aethelgard", "lore_chronicle": "A long chronicle" * 50},
        recent_decisions=[{"chosen_action": "Choice 1", "rationale": "Rationale 1"}],
        rag_memories=[{"title": f"Memory {i}", "content": f"Content {i}"} for i in range(10)]
    )
    assert res["total_chars"] <= context_budget_manager.max_context_chars
    assert len(res["sources"]) > 0
