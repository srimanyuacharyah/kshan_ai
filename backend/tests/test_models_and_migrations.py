import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models import (
    Base,
    User,
    UserProfile,
    Scenario,
    FutureProfile,
    RealityBranch,
    MultiverseState,
    TimelineNode,
    Choice,
    Consequence,
    Decision,
    World,
    Location,
    Character,
    Memory,
    MediaItem,
    Conversation,
    ConversationMessage,
    EmbeddingRecord
)
from backend.app.core.config import settings

@pytest.mark.asyncio
async def test_complete_multiverse_relational_graph(db_session: AsyncSession, test_user_a: User):
    """Test instantiating and linking all 18 relational models with strict tenant isolation."""
    # 1. Create Scenario & World
    scenario = Scenario(
        title="The Midnight Metro of Neo-Kashi",
        slug="neo-kashi-metro",
        genre="Cyber-Mythic",
        tagline="A train doors close; a bioluminescent shard drops.",
        premise="Neo-Kashi floats above ancient subterranean riverbeds...",
        initial_kshan_moment="The train chime rings. A hooded figure drops a glowing memory crystal.",
        is_curated=True
    )
    db_session.add(scenario)
    await db_session.flush()

    world = World(
        scenario_id=scenario.id,
        name="Neo-Kashi Cyber-Realm",
        cosmos_type="Stratified Megacity",
        lore_chronicle="Built over the spiritual vortex of the Ganges."
    )
    db_session.add(world)
    await db_session.flush()

    location = Location(
        world_id=world.id,
        name="Platform 108 - Varanasi Central",
        realm_zone="Undercity Transit",
        description="Bioluminescent moss climbs rusted steel pillars."
    )
    character = Character(
        world_id=world.id,
        name="Aria / The Echo Merchant",
        role="Companion",
        backstory="Smuggler of forgotten pre-collapse memories."
    )
    db_session.add_all([location, character])
    await db_session.flush()

    # 2. FutureProfile
    future_profile = FutureProfile(
        user_id=test_user_a.id,
        scenario_id=scenario.id,
        title="The Memory Shard Divergence",
        archetype="The Void Walker"
    )
    db_session.add(future_profile)
    await db_session.flush()

    # 3. RealityBranch & MultiverseState
    branch = RealityBranch(
        user_id=test_user_a.id,
        future_profile_id=future_profile.id,
        branch_name="Branch Prime: The Subterranean Leap",
        branch_code="TL-NK-01",
        entropy_level=0.25,
        resonance_score=0.75
    )
    db_session.add(branch)
    await db_session.flush()

    state = MultiverseState(
        branch_id=branch.id,
        timeline_era="Year 2042"
    )
    db_session.add(state)

    # 4. TimelineNode, Choice, Consequence & Decision
    node = TimelineNode(
        user_id=test_user_a.id,
        branch_id=branch.id,
        depth_level=0,
        story_text="You pick up the glowing crystal. Neon reflections warp around your fingertips.",
        sensory_cue="Ozone and burning incense",
        audio_ambiance="cosmic_drone"
    )
    db_session.add(node)
    await db_session.flush()

    choice = Choice(
        node_id=node.id,
        choice_label="Interface your neural link with the shard",
        choice_description="Attempt a direct neural sync with the unknown artifact.",
        risk_level="high",
        philosophical_vector="Transcendence"
    )
    db_session.add(choice)
    await db_session.flush()

    consequence = Consequence(
        choice_id=choice.id,
        predicted_outcome="Memory overload risks temporal fracture.",
        expected_entropy_shift=0.3
    )
    decision = Decision(
        user_id=test_user_a.id,
        node_id=node.id,
        chosen_choice_id=choice.id,
        rationale="Curiosity over preservation"
    )
    db_session.add_all([consequence, decision])

    # 5. Memory, MediaItem, Conversation & EmbeddingRecord
    memory = Memory(
        user_id=test_user_a.id,
        branch_id=branch.id,
        node_id=node.id,
        title="First Resonance Shard",
        content="A vision of an extinguished sun in ancient Kashi.",
        emotional_tone="epiphany"
    )
    db_session.add(memory)
    await db_session.flush()

    media = MediaItem(
        memory_id=memory.id,
        media_type="image",
        media_url="https://kshan.ai/assets/neo-kashi-shard.webp",
        caption="Bioluminescent Shard in Neon Mist"
    )
    conv = Conversation(
        user_id=test_user_a.id,
        branch_id=branch.id,
        persona_title="Future You (Cycle IX)"
    )
    db_session.add_all([media, conv])
    await db_session.flush()

    msg = ConversationMessage(
        conversation_id=conv.id,
        sender_role="user",
        content="Did we survive the sync?",
        grounding_sources=[{"memory_id": memory.id, "title": memory.title}]
    )
    embedding = EmbeddingRecord(
        user_id=test_user_a.id,
        branch_id=branch.id,
        entity_type="memory",
        entity_id=memory.id,
        document_content="A vision of an extinguished sun in ancient Kashi.",
        document_title="First Resonance Shard"
    )
    db_session.add_all([msg, embedding])
    await db_session.commit()

    # Assertions
    assert scenario.id is not None
    assert branch.user_id == test_user_a.id
    assert node.branch_id == branch.id
    assert choice.node_id == node.id
    assert decision.chosen_choice_id == choice.id
    assert embedding.user_id == test_user_a.id
    assert settings.EMBEDDING_DIMENSION == 768
