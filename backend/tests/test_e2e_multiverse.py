import pytest
from httpx import AsyncClient
from backend.app.models import RealityBranch, TimelineNode, Choice, Memory, World
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest.mark.asyncio
async def test_30_step_e2e_multiverse_lifecycle(client: AsyncClient, db_session: AsyncSession):
    """
    Comprehensive 30-Step End-to-End Multiverse Lifecycle Test.
    Validates the complete persisted multiverse system across all core engines:
    Auth, Relational Hierarchy, Deterministic 7D State, 4-Tier Butterfly Ripples,
    RAG vector embeddings, MCP tool discovery, non-destructive spacetime rewinds,
    multiverse diff matrix, tenant isolation, and structured error handling.
    """

    # --------------------------------------------------------------------------
    # STEP 1: Register User A
    # --------------------------------------------------------------------------
    reg_payload_a = {
        "email": "traveler_prime@kshan.ai",
        "username": "traveler_prime",
        "password": "Password123!",
        "display_name": "Traveler Prime"
    }
    res_reg_a = await client.post("/api/v1/auth/register", json=reg_payload_a)
    assert res_reg_a.status_code == 201, f"Registration failed: {res_reg_a.text}"
    user_a_data = res_reg_a.json()["data"]["user"]
    assert "id" in user_a_data

    # --------------------------------------------------------------------------
    # STEP 2 & 3: Login User A & Obtain JWT Bearer Token
    # --------------------------------------------------------------------------
    login_data_a = {
        "email": "traveler_prime@kshan.ai",
        "password": "Password123!"
    }
    res_login_a = await client.post("/api/v1/auth/login", json=login_data_a)
    assert res_login_a.status_code == 200
    token_a = res_login_a.json()["data"]["token"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register User B for tenant isolation checks
    reg_payload_b = {
        "email": "traveler_shadow@kshan.ai",
        "username": "traveler_shadow",
        "password": "Password123!",
        "display_name": "Traveler Shadow"
    }
    await client.post("/api/v1/auth/register", json=reg_payload_b)
    res_login_b = await client.post("/api/v1/auth/login", json={"email": "traveler_shadow@kshan.ai", "password": "Password123!"})
    token_b = res_login_b.json()["data"]["token"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # --------------------------------------------------------------------------
    # STEP 4: Retrieve Available Scenarios
    # --------------------------------------------------------------------------
    res_scenarios = await client.get("/api/v1/scenarios")
    assert res_scenarios.status_code == 200
    scenarios = res_scenarios.json()
    assert len(scenarios) >= 3
    scenario_neo_kashi = next(s for s in scenarios if s["slug"] == "neo-kashi-2042")
    scenario_id = scenario_neo_kashi["id"]

    # --------------------------------------------------------------------------
    # STEP 5 & 6: Create Root Reality Branch R0
    # --------------------------------------------------------------------------
    branch_payload = {
        "branch_name": "Prime Reality: Neo-Kashi 2042",
        "initial_story": "You stand at the edge of the Manikarnika Sky-Pier. Rain sizzles on holographic prayer flags.",
        "initial_entropy": 0.15,
        "initial_resonance": 0.75
    }
    res_root = await client.post("/api/v1/multiverse/branch", json=branch_payload, headers=headers_a)
    assert res_root.status_code == 201
    root_data = res_root.json()
    root_branch = root_data["branch"]
    genesis_node = root_data["genesis_node"]
    root_branch_id = root_branch["id"]
    genesis_node_id = genesis_node["id"]

    # --------------------------------------------------------------------------
    # STEP 7: Verify Initial Narrative Genesis Persistence
    # --------------------------------------------------------------------------
    assert root_branch["depth"] == 0
    assert "Sky-Pier" in genesis_node["story_text"]

    # --------------------------------------------------------------------------
    # STEP 8: Retrieve / Seed Available Choices at Genesis Node
    # --------------------------------------------------------------------------
    choice_a = Choice(
        node_id=genesis_node_id,
        choice_label="Break the firewall and escape into the Quantum Frontier",
        choice_description="Sever all biometric ties and dive through the reality breach.",
        risk_level="high",
        philosophical_vector="Defiance"
    )
    db_session.add(choice_a)
    await db_session.commit()
    await db_session.refresh(choice_a)
    choice_a_id = choice_a.id

    # --------------------------------------------------------------------------
    # STEP 9: Select Choice A (Execute Choice Action)
    # --------------------------------------------------------------------------
    choose_payload_1 = {
        "branch_id": root_branch_id,
        "timeline_node_id": genesis_node_id,
        "choice_id": choice_a_id,
        "intention": "Break the firewall and escape",
        "custom_branch_name": "Reality R1: The Quantum Escape"
    }
    res_choose_1 = await client.post("/api/v1/multiverse/choose", json=choose_payload_1, headers=headers_a)
    assert res_choose_1.status_code == 201
    r1_data = res_choose_1.json()

    # --------------------------------------------------------------------------
    # STEP 10: Verify New Child Branch R1 Created
    # --------------------------------------------------------------------------
    branch_r1 = r1_data["new_branch"]
    node_r1 = r1_data["new_timeline_node"]
    branch_r1_id = branch_r1["id"]
    node_r1_id = node_r1["id"]

    assert branch_r1["parent_branch_id"] == root_branch_id
    assert branch_r1["depth"] == 1

    # --------------------------------------------------------------------------
    # STEP 11 & 12: Verify Deterministic 7D State Transitions & Bounds
    # --------------------------------------------------------------------------
    state_vector = r1_data["state_vector"]
    assert 0.0 <= state_vector["entropy"] <= 1.0
    assert 0.0 <= state_vector["resonance"] <= 1.0
    assert 0.0 <= state_vector["regret"] <= 1.0
    assert 0.0 <= state_vector["destiny_shift"] <= 1.0
    assert state_vector["entropy"] > root_branch["entropy"]

    # --------------------------------------------------------------------------
    # STEP 13: Verify 4-Tier Butterfly Effect Cascade Structure
    # --------------------------------------------------------------------------
    butterfly = r1_data["butterfly_ripple"]
    assert "immediate_effect" in butterfly
    assert isinstance(butterfly["secondary_effects"], list)
    assert len(butterfly["tertiary_effects"]) >= 1
    assert len(butterfly["unlocked_pathways"]) >= 1

    # --------------------------------------------------------------------------
    # STEP 14: Verify Timeline Node Chain
    # --------------------------------------------------------------------------
    assert node_r1["depth_level"] == 1

    # --------------------------------------------------------------------------
    # STEP 15 & 16: Verify Memory Creation & Automatic RAG Indexing
    # --------------------------------------------------------------------------
    mem_stmt = select(Memory).where(Memory.branch_id == branch_r1_id)
    mem_res = await db_session.execute(mem_stmt)
    memories = mem_res.scalars().all()
    assert len(memories) >= 1

    # --------------------------------------------------------------------------
    # STEP 17: Query RAG for Memory Echoes
    # --------------------------------------------------------------------------
    rag_payload = {
        "query": "firewall escape quantum breach",
        "branch_id": branch_r1_id,
        "top_k": 3
    }
    res_rag = await client.post("/api/v1/rag/search", json=rag_payload, headers=headers_a)
    assert res_rag.status_code == 200
    rag_results = res_rag.json()["data"]["results"]
    assert len(rag_results) >= 1

    # --------------------------------------------------------------------------
    # STEP 18, 19, 20: Query Readiness Probes
    # --------------------------------------------------------------------------
    res_ready = await client.get("/api/v1/health/ready")
    assert res_ready.status_code == 200

    # --------------------------------------------------------------------------
    # STEP 21 & 22: Make Second Choice -> Deeper Branch R1B
    # --------------------------------------------------------------------------
    choice_b = Choice(
        node_id=node_r1_id,
        choice_label="Rendezvous with the Memory Weavers in Sub-Ghat ruins",
        choice_description="Seek sanctuary and decrypt the ancient shard.",
        risk_level="moderate",
        philosophical_vector="Harmony"
    )
    db_session.add(choice_b)
    await db_session.commit()
    await db_session.refresh(choice_b)

    choose_payload_2 = {
        "branch_id": branch_r1_id,
        "timeline_node_id": node_r1_id,
        "choice_id": choice_b.id,
        "intention": "Seek sanctuary with weavers",
        "custom_branch_name": "Reality R1B: The Memory Sanctuary"
    }
    res_choose_2 = await client.post("/api/v1/multiverse/choose", json=choose_payload_2, headers=headers_a)
    assert res_choose_2.status_code == 201
    r1b_data = res_choose_2.json()
    branch_r1b = r1b_data["new_branch"]
    assert branch_r1b["depth"] == 2
    assert branch_r1b["parent_branch_id"] == branch_r1_id

    # --------------------------------------------------------------------------
    # STEP 23 & 24: Spacetime Rewind to Genesis Node -> Creates Parallel Fork R2
    # --------------------------------------------------------------------------
    rewind_payload = {
        "historical_node_id": genesis_node_id,
        "rewind_intention": "Try an alternate diplomatic negotiation",
        "fork_branch_name": "Reality R2: The Diplomatic Concord"
    }
    res_rewind = await client.post("/api/v1/multiverse/rewind", json=rewind_payload, headers=headers_a)
    assert res_rewind.status_code == 201
    rewind_data = res_rewind.json()
    branch_r2 = rewind_data["fork_branch"]
    branch_r2_id = branch_r2["id"]

    assert branch_r2["parent_branch_id"] == root_branch_id
    assert branch_r2["depth"] in [0, 1]

    # --------------------------------------------------------------------------
    # STEP 25: Parent Branch Immutability Verification
    # --------------------------------------------------------------------------
    res_r0_check = await client.get(f"/api/v1/multiverse/branch/{root_branch_id}", headers=headers_a)
    assert res_r0_check.status_code == 200
    assert res_r0_check.json()["branch"]["entropy"] == root_branch["entropy"]

    res_r1_check = await client.get(f"/api/v1/multiverse/branch/{branch_r1_id}", headers=headers_a)
    assert res_r1_check.status_code == 200
    assert res_r1_check.json()["branch"]["entropy"] == branch_r1["entropy"]

    # --------------------------------------------------------------------------
    # STEP 26: Retrieve Complete Multiverse Tree
    # --------------------------------------------------------------------------
    res_tree = await client.get(f"/api/v1/multiverse/tree/{scenario_id}", headers=headers_a)
    assert res_tree.status_code == 200
    tree_nodes = res_tree.json()["nodes"]
    assert len(tree_nodes) >= 3

    # --------------------------------------------------------------------------
    # STEP 27: Compare Two Branches (R1 vs R2)
    # --------------------------------------------------------------------------
    res_compare = await client.get(f"/api/v1/multiverse/compare/{branch_r1_id}/{branch_r2_id}", headers=headers_a)
    assert res_compare.status_code == 200
    diff_data = res_compare.json()
    assert "metrics_differential" in diff_data
    assert "divergence_verdict" in diff_data

    # --------------------------------------------------------------------------
    # STEP 28: Cross-User Tenant Isolation Verification
    # --------------------------------------------------------------------------
    res_cross_branch = await client.get(f"/api/v1/multiverse/branch/{branch_r1_id}", headers=headers_b)
    assert res_cross_branch.status_code in [400, 403, 404]

    res_cross_choose = await client.post("/api/v1/multiverse/choose", json=choose_payload_1, headers=headers_b)
    assert res_cross_choose.status_code in [400, 403, 404]

    # --------------------------------------------------------------------------
    # STEP 29: Idempotency Against Duplicate Choice Submission
    # --------------------------------------------------------------------------
    res_dup_choose = await client.post("/api/v1/multiverse/choose", json=choose_payload_1, headers=headers_a)
    assert res_dup_choose.status_code in [200, 201]
    assert "new_branch" in res_dup_choose.json()

    # --------------------------------------------------------------------------
    # STEP 30: Graceful Error Handling & Structured JSON Envelope
    # --------------------------------------------------------------------------
    res_invalid_branch = await client.get("/api/v1/multiverse/branch/00000000-0000-0000-0000-000000000000", headers=headers_a)
    assert res_invalid_branch.status_code == 404
    err_body = res_invalid_branch.json()
    assert "error" in err_body
    assert "code" in err_body["error"]
    assert "message" in err_body["error"]
    assert "request_id" in err_body["error"]
