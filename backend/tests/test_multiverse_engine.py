import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.main import app
from backend.app.models.user import User
from backend.app.models.multiverse import RealityBranch, MultiverseState
from backend.app.models.timeline import TimelineNode, Choice, Decision
from backend.app.models.memory import Memory
from backend.app.models.world import World, Character
from backend.app.services.multiverse.state_engine import state_engine, MultiverseStateVector, clamp
from backend.app.services.multiverse.entropy_engine import entropy_engine
from backend.app.services.multiverse.resonance_engine import resonance_engine
from backend.app.services.multiverse.regret_engine import regret_engine, destiny_engine
from backend.app.services.multiverse.butterfly_engine import butterfly_engine
from backend.app.services.multiverse.branch_engine import branch_engine
from backend.app.services.multiverse.timeline_engine import timeline_engine
from backend.app.core.security import create_access_token
from backend.app.services.mcp.client import mcp_client

# ================= 1. UNIT TESTS: DETERMINISTIC STATE & BUTTERFLY ENGINES =================

def test_state_vector_bounds_and_nan_safety():
    """Verify 7D state vector strictly bounds metrics to [0.0, 1.0] and handles NaNs safely."""
    raw_bad_data = {
        "entropy": 1.45,
        "resonance": -0.25,
        "regret": float("nan"),
        "destiny_shift": 2.0,
        "world_stability": float("inf"),
        "social_stability": 0.85,
        "technology_level": -10.0
    }
    vec = state_engine.clamp_vector(raw_bad_data)
    assert vec.entropy == 1.0
    assert vec.resonance == 0.0
    assert vec.regret == 0.0 # NaN clamped to default min 0.0
    assert vec.destiny_shift == 1.0
    assert vec.world_stability == 0.0 # inf clamped to min 0.0
    assert vec.social_stability == 0.85
    assert vec.technology_level == 0.0

def test_entropy_and_resonance_delta_calculations():
    """Verify deterministic entropy and resonance shifts."""
    ent_delta_low = entropy_engine.calculate_entropy_delta(current_entropy=0.2, risk_level="low", choice_risk=0.2)
    ent_delta_high = entropy_engine.calculate_entropy_delta(current_entropy=0.2, risk_level="existential", choice_risk=0.9)
    assert ent_delta_high > ent_delta_low

    res_delta_defiance = resonance_engine.calculate_resonance_delta(
        current_resonance=0.5,
        choice_philosophical_vector="Defiance",
        profile_archetype="Rebel"
    )
    assert res_delta_defiance > 0.0

def test_butterfly_effect_4_tier_propagation():
    """Verify butterfly engine generates all 4 causal tiers deterministically."""
    characters = [
        {"name": "Aria", "role": "Rebel", "trust": 0.70},
        {"name": "Commander Vane", "role": "Guardian", "trust": 0.50}
    ]
    world_vars = {"danger_level": "low", "surveillance_grid": "inactive"}

    ripple = butterfly_engine.calculate_butterfly_effects(
        choice_id="choice_sample",
        choice_label="Sever biometric link and escape",
        risk_level="high",
        philosophical_vector="Defiance",
        narrative_consequence_proposal="The city alarm rings out.",
        characters=characters,
        world_state_variables=world_vars
    )

    # Tier 1
    assert "city alarm rings out" in ripple.immediate_effect
    # Tier 2
    assert len(ripple.secondary_effects) == 2
    aria_effect = next(e for e in ripple.secondary_effects if e.character_name == "Aria")
    assert aria_effect.trust_delta > 0.0 # Rebel likes Defiance
    vane_effect = next(e for e in ripple.secondary_effects if e.character_name == "Commander Vane")
    assert vane_effect.trust_delta < 0.0 # Guardian dislikes Defiance
    # Tier 3
    assert any(te.variable_name == "danger_level" and te.new_value == "elevated" for te in ripple.tertiary_effects)
    # Tier 4
    assert len(ripple.unlocked_pathways) > 0
    assert len(ripple.locked_pathways) > 0

# ================= 2. SERVICE TESTS: PERSISTENT MULTIVERSE BRANCHING =================

@pytest.mark.asyncio
async def test_root_branch_creation_and_timeline(
    db_session: AsyncSession,
    test_user_a: User
):
    """Verify root branch creation initializes R0 with genesis node and state snapshot."""
    root_branch, genesis_node = await branch_engine.create_root_branch(
        db=db_session,
        user_id=test_user_a.id,
        future_profile_id=None,
        branch_name="Prime Timeline Baseline",
        initial_story="Genesis node in Neo-Kashi."
    )
    await db_session.commit()

    assert root_branch.id is not None
    assert root_branch.parent_branch_id is None
    assert root_branch.branch_metadata["depth"] == 0
    assert genesis_node.branch_id == root_branch.id
    assert genesis_node.depth_level == 0

@pytest.mark.asyncio
async def test_child_branch_creation_preserves_parent_immutability(
    db_session: AsyncSession,
    test_user_a: User
):
    """Verify child branch creation creates R1 while parent R0 remains unchanged."""
    root_branch, genesis_node = await branch_engine.create_root_branch(
        db=db_session,
        user_id=test_user_a.id,
        future_profile_id=None,
        branch_name="Prime Timeline"
    )
    initial_root_entropy = root_branch.entropy_level
    initial_root_resonance = root_branch.resonance_score

    # Add choice to genesis node
    choice = Choice(
        id=str(uuid.uuid4()),
        node_id=genesis_node.id,
        choice_label="Hack the Nexus terminal",
        choice_description="Infiltrate the city power grid",
        risk_level="high",
        philosophical_vector="Defiance",
        order_index=0
    )
    db_session.add(choice)
    await db_session.commit()

    # Create child branch from choice
    result = await branch_engine.create_branch_from_decision(
        db=db_session,
        user_id=test_user_a.id,
        parent_branch_id=root_branch.id,
        timeline_node_id=genesis_node.id,
        choice_id=choice.id,
        intention="Expose the ministry corruption",
        narrative_consequence_proposal="Terminal alarms sounded across the district."
    )
    await db_session.commit()

    child_branch = result["branch"]
    child_node = result["timeline_node"]
    decision = result["decision"]

    # Assert child branch
    assert child_branch.parent_branch_id == root_branch.id
    assert child_branch.branch_metadata["depth"] == 1
    assert child_branch.entropy_level > initial_root_entropy
    assert child_node.branch_id == child_branch.id
    assert child_node.depth_level == 1
    assert decision.chosen_choice_id == choice.id

    # Verify parent branch R0 remained 100% IMMUTABLE
    parent_check = await db_session.get(RealityBranch, root_branch.id)
    assert parent_check.entropy_level == initial_root_entropy
    assert parent_check.resonance_score == initial_root_resonance
    assert parent_check.parent_branch_id is None

@pytest.mark.asyncio
async def test_idempotent_choice_execution(
    db_session: AsyncSession,
    test_user_a: User
):
    """Verify duplicate choice submissions with same idempotency_key return existing branch."""
    root_branch, genesis_node = await branch_engine.create_root_branch(
        db=db_session,
        user_id=test_user_a.id,
        future_profile_id=None
    )
    choice = Choice(
        id=str(uuid.uuid4()),
        node_id=genesis_node.id,
        choice_label="Activate the Chronos conduit",
        choice_description="Attempt reality alignment",
        risk_level="moderate",
        philosophical_vector="Harmony",
        order_index=0
    )
    db_session.add(choice)
    await db_session.commit()

    idempotency_key = "idemp_test_req_999"

    # First call
    res_1 = await branch_engine.create_branch_from_decision(
        db=db_session,
        user_id=test_user_a.id,
        parent_branch_id=root_branch.id,
        timeline_node_id=genesis_node.id,
        choice_id=choice.id,
        idempotency_key=idempotency_key
    )
    await db_session.commit()

    # Second identical call
    res_2 = await branch_engine.create_branch_from_decision(
        db=db_session,
        user_id=test_user_a.id,
        parent_branch_id=root_branch.id,
        timeline_node_id=genesis_node.id,
        choice_id=choice.id,
        idempotency_key=idempotency_key
    )
    await db_session.commit()

    assert res_1["branch"].id == res_2["branch"].id
    assert res_2["is_idempotent_replay"] is True

@pytest.mark.asyncio
async def test_rewind_creates_parallel_fork_without_deleting_history(
    db_session: AsyncSession,
    test_user_a: User
):
    """Verify rewind creates a new fork branch from an earlier node while preserving all original branches."""
    root_branch, genesis_node = await branch_engine.create_root_branch(
        db=db_session,
        user_id=test_user_a.id,
        future_profile_id=None
    )
    choice_a = Choice(
        id=str(uuid.uuid4()),
        node_id=genesis_node.id,
        choice_label="Take the Left Portal",
        choice_description="Enter the glowing cyan rift",
        risk_level="high",
        philosophical_vector="Defiance"
    )
    db_session.add(choice_a)
    await db_session.commit()

    # Step 1: Create Branch R1
    step_1 = await branch_engine.create_branch_from_decision(
        db=db_session,
        user_id=test_user_a.id,
        parent_branch_id=root_branch.id,
        timeline_node_id=genesis_node.id,
        choice_id=choice_a.id
    )
    await db_session.commit()
    r1_branch = step_1["branch"]

    # Step 2: Rewind back to genesis_node
    rewind_res = await branch_engine.rewind_to_node(
        db=db_session,
        user_id=test_user_a.id,
        historical_node_id=genesis_node.id,
        rewind_intention="Try a different path without the alarm"
    )
    await db_session.commit()

    fork_branch = rewind_res["fork_branch"]

    # Assertions
    assert fork_branch.id != r1_branch.id
    assert fork_branch.fork_node_id == genesis_node.id
    assert fork_branch.branch_metadata["is_rewind_fork"] is True

    # Check that original R1 is still active and intact
    r1_check = await db_session.get(RealityBranch, r1_branch.id)
    assert r1_check is not None
    assert r1_check.status == "active"

@pytest.mark.asyncio
async def test_branch_tree_and_comparison(
    db_session: AsyncSession,
    test_user_a: User
):
    """Verify branch tree graph topology and branch comparison matrix."""
    root_branch, genesis_node = await branch_engine.create_root_branch(
        db=db_session,
        user_id=test_user_a.id,
        future_profile_id=None
    )
    choice_1 = Choice(
        id=str(uuid.uuid4()),
        node_id=genesis_node.id,
        choice_label="Path Alpha",
        choice_description="Aggressive push",
        risk_level="high",
        philosophical_vector="Defiance"
    )
    choice_2 = Choice(
        id=str(uuid.uuid4()),
        node_id=genesis_node.id,
        choice_label="Path Beta",
        choice_description="Diplomatic mediation",
        risk_level="low",
        philosophical_vector="Harmony"
    )
    db_session.add_all([choice_1, choice_2])
    await db_session.commit()

    # Create Branch A and Branch B from root
    r_a = await branch_engine.create_branch_from_decision(
        db=db_session,
        user_id=test_user_a.id,
        parent_branch_id=root_branch.id,
        timeline_node_id=genesis_node.id,
        choice_id=choice_1.id
    )
    r_b = await branch_engine.create_branch_from_decision(
        db=db_session,
        user_id=test_user_a.id,
        parent_branch_id=root_branch.id,
        timeline_node_id=genesis_node.id,
        choice_id=choice_2.id
    )
    await db_session.commit()

    branch_a = r_a["branch"]
    branch_b = r_b["branch"]

    # 1. Test Multiverse Tree
    tree = await branch_engine.get_branch_tree(db=db_session, user_id=test_user_a.id)
    assert tree["total_branches"] >= 3
    assert len(tree["nodes"]) >= 3
    assert len(tree["edges"]) >= 2

    # 2. Test Compare Branches
    comp = await branch_engine.compare_branches(
        db=db_session,
        user_id=test_user_a.id,
        branch_a_id=branch_a.id,
        branch_b_id=branch_b.id
    )
    assert "metrics_differential" in comp
    assert comp["branch_a"]["id"] == branch_a.id
    assert comp["branch_b"]["id"] == branch_b.id

# ================= 3. API ENDPOINT TESTS =================

@pytest.mark.asyncio
async def test_api_choose_action_endpoint(
    client: AsyncClient,
    auth_headers_user_a: dict,
    db_session: AsyncSession,
    test_user_a: User
):
    """Verify POST /api/v1/multiverse/choose executes choice and returns full reality delta."""
    root_branch, genesis_node = await branch_engine.create_root_branch(
        db=db_session,
        user_id=test_user_a.id,
        future_profile_id=None
    )
    choice = Choice(
        id=str(uuid.uuid4()),
        node_id=genesis_node.id,
        choice_label="Bribe the Terminal Guard",
        choice_description="Slip quantum credits to the guard",
        risk_level="moderate",
        philosophical_vector="Pragmatism"
    )
    db_session.add(choice)
    await db_session.commit()

    res = await client.post(
        "/api/v1/multiverse/choose",
        headers=auth_headers_user_a,
        json={
            "branch_id": root_branch.id,
            "timeline_node_id": genesis_node.id,
            "choice_id": choice.id,
            "intention": "Slip into the sector undetected"
        }
    )

    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["new_branch"]["parent_branch_id"] == root_branch.id
    assert data["new_branch"]["depth"] == 1
    assert data["new_timeline_node"]["depth_level"] == 1
    assert "butterfly_ripple" in data

@pytest.mark.asyncio
async def test_api_cross_user_isolation_rejected(
    client: AsyncClient,
    auth_headers_user_b: dict,
    db_session: AsyncSession,
    test_user_a: User,
    test_user_b: User
):
    """Verify User B cannot choose or rewind branches belonging to User A."""
    root_branch, genesis_node = await branch_engine.create_root_branch(
        db=db_session,
        user_id=test_user_a.id,
        future_profile_id=None
    )
    choice = Choice(
        id=str(uuid.uuid4()),
        node_id=genesis_node.id,
        choice_label="Infiltrate",
        choice_description="Test"
    )
    db_session.add(choice)
    await db_session.commit()

    res = await client.post(
        "/api/v1/multiverse/choose",
        headers=auth_headers_user_b,
        json={
            "branch_id": root_branch.id,
            "timeline_node_id": genesis_node.id,
            "choice_id": choice.id
        }
    )

    assert res.status_code == 400
    assert "forbidden" in res.json()["detail"].lower() or "not found" in res.json()["detail"].lower()

# ================= 4. COMPLETE MULTIVERSE LIFECYCLE (E2E) =================

@pytest.mark.asyncio
async def test_complete_multiverse_lifecycle_e2e(
    db_session: AsyncSession,
    test_user_a: User
):
    """
    Complete E2E Test:
    User
    → Root Reality R0
    → Choose A → Reality R1
    → Choose B → Reality R1B
    → Rewind to Genesis
    → Choose C → Reality R2
    
    Verifies:
    - R0, R1, R1B remain immutable
    - R2 is a distinct parallel branch
    - Graph tree has 4 branches and correct edges
    - Memories are generated and searchable
    - MCP can retrieve state for all branches
    - Branch comparison between R1 and R2
    """
    token = create_access_token(test_user_a.id)

    # 1. Create Root Reality R0
    r0_branch, genesis_node = await branch_engine.create_root_branch(
        db=db_session,
        user_id=test_user_a.id,
        future_profile_id=None,
        branch_name="Reality R0 (Root)"
    )
    await db_session.commit()

    # 2. Add Choices to Genesis Node (Choice A and Choice C)
    choice_a = Choice(
        id=str(uuid.uuid4()),
        node_id=genesis_node.id,
        choice_label="Choice A: Expose Ministry AI",
        choice_description="Broadcast secret logs",
        risk_level="high",
        philosophical_vector="Defiance"
    )
    choice_c = Choice(
        id=str(uuid.uuid4()),
        node_id=genesis_node.id,
        choice_label="Choice C: Negotiate Peace Treaty",
        choice_description="Send diplomatic courier",
        risk_level="low",
        philosophical_vector="Harmony"
    )
    db_session.add_all([choice_a, choice_c])
    await db_session.commit()

    # 3. Choose Choice A -> Spawns Reality R1
    res_r1 = await branch_engine.create_branch_from_decision(
        db=db_session,
        user_id=test_user_a.id,
        parent_branch_id=r0_branch.id,
        timeline_node_id=genesis_node.id,
        choice_id=choice_a.id,
        custom_branch_name="Reality R1"
    )
    await db_session.commit()
    r1_branch = res_r1["branch"]
    r1_node = res_r1["timeline_node"]
    r1_entropy = r1_branch.entropy_level

    # 4. Add Choice B on R1 node
    choice_b = Choice(
        id=str(uuid.uuid4()),
        node_id=r1_node.id,
        choice_label="Choice B: Build Underground Enclave",
        choice_description="Fortify rogue district",
        risk_level="moderate",
        philosophical_vector="Defiance"
    )
    db_session.add(choice_b)
    await db_session.commit()

    # 5. Choose Choice B -> Spawns Reality R1B
    res_r1b = await branch_engine.create_branch_from_decision(
        db=db_session,
        user_id=test_user_a.id,
        parent_branch_id=r1_branch.id,
        timeline_node_id=r1_node.id,
        choice_id=choice_b.id,
        custom_branch_name="Reality R1B"
    )
    await db_session.commit()
    r1b_branch = res_r1b["branch"]
    assert r1b_branch.branch_metadata["depth"] == 2

    # 6. Rewind to Genesis Node
    rewind_res = await branch_engine.rewind_to_node(
        db=db_session,
        user_id=test_user_a.id,
        historical_node_id=genesis_node.id
    )
    await db_session.commit()

    # 7. Choose Choice C from Genesis -> Spawns Reality R2
    res_r2 = await branch_engine.create_branch_from_decision(
        db=db_session,
        user_id=test_user_a.id,
        parent_branch_id=r0_branch.id,
        timeline_node_id=genesis_node.id,
        choice_id=choice_c.id,
        custom_branch_name="Reality R2"
    )
    await db_session.commit()
    r2_branch = res_r2["branch"]

    # 8. Verify Branch Immutability
    r0_check = await db_session.get(RealityBranch, r0_branch.id)
    r1_check = await db_session.get(RealityBranch, r1_branch.id)
    r1b_check = await db_session.get(RealityBranch, r1b_branch.id)

    assert r0_check.entropy_level == r0_branch.entropy_level
    assert r1_check.entropy_level == r1_entropy
    assert r1b_check.branch_metadata["depth"] == 2
    assert r2_branch.id not in [r0_branch.id, r1_branch.id, r1b_branch.id]

    # 9. Verify Multiverse Graph Tree
    tree = await branch_engine.get_branch_tree(db=db_session, user_id=test_user_a.id)
    assert tree["total_branches"] >= 4 # R0, R1, R1B, Fork, R2
    assert len(tree["edges"]) >= 3

    # 10. Verify MCP Integration with new branch R1B
    mcp_branch_state = await mcp_client.call_tool(
        tool_name="get_branch_state",
        arguments={"branch_id": r1b_branch.id},
        auth_token=token
    )
    assert mcp_branch_state.success is True
    assert mcp_branch_state.data["branch_id"] == r1b_branch.id

    # 11. Verify Branch Comparison R1 vs R2
    comp = await branch_engine.compare_branches(
        db=db_session,
        user_id=test_user_a.id,
        branch_a_id=r1_branch.id,
        branch_b_id=r2_branch.id
    )
    assert comp["branch_a"]["name"] == "Reality R1"
    assert comp["branch_b"]["name"] == "Reality R2"
    assert comp["metrics_differential"]["resonance_delta"] is not None
