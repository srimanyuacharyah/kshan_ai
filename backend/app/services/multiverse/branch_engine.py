import uuid
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from backend.app.models.multiverse import RealityBranch, MultiverseState
from backend.app.models.timeline import TimelineNode, Choice, Decision, Consequence
from backend.app.models.memory import Memory
from backend.app.models.world import World, Character
from backend.app.services.multiverse.state_engine import state_engine, MultiverseStateVector, clamp
from backend.app.services.multiverse.entropy_engine import entropy_engine
from backend.app.services.multiverse.resonance_engine import resonance_engine
from backend.app.services.multiverse.regret_engine import regret_engine, destiny_engine
from backend.app.services.multiverse.butterfly_engine import butterfly_engine, ButterflyRipple
from backend.app.services.multiverse.decision_engine import decision_engine
from backend.app.services.multiverse.timeline_engine import timeline_engine
from backend.app.services.rag.rag_pipeline import rag_pipeline
from backend.app.core.logging import get_logger

logger = get_logger("kshan.multiverse.branch")

class BranchEngine:
    """
    Core multiverse branching engine for KSHAN:
    Governs persistent reality branching, immutable history preservation,
    rewind/fork mechanics, and cross-branch comparison.
    """

    async def create_root_branch(
        self,
        db: AsyncSession,
        user_id: str,
        future_profile_id: Optional[str],
        branch_name: str = "Prime Reality Baseline",
        branch_code: Optional[str] = None,
        initial_story: str = "The genesis moment of your multiverse journey.",
        initial_state: Optional[Dict[str, Any]] = None
    ) -> Tuple[RealityBranch, TimelineNode]:
        """
        Creates the immutable Root Reality (R0) for a traveler.
        """
        b_code = branch_code or f"TL-PRIME-{uuid.uuid4().hex[:4].upper()}"
        initial_state = initial_state or {}

        # 1. Create Root Branch
        root_branch = RealityBranch(
            id=str(uuid.uuid4()),
            user_id=user_id,
            future_profile_id=future_profile_id,
            parent_branch_id=None,
            fork_node_id=None,
            branch_name=branch_name,
            branch_code=b_code,
            status="active",
            entropy_level=initial_state.get("entropy", 0.10),
            resonance_score=initial_state.get("resonance", 0.70),
            regret_index=initial_state.get("regret", 0.00),
            destiny_shift=0.00,
            branch_metadata={
                "depth": 0,
                "is_root": True,
                "root_branch_id": None,
                "world_stability": initial_state.get("world_stability", 0.85),
                "social_stability": initial_state.get("social_stability", 0.80),
                "technology_level": initial_state.get("technology_level", 0.50)
            }
        )
        root_branch.branch_metadata["root_branch_id"] = root_branch.id
        db.add(root_branch)
        await db.flush()

        # 2. Create Genesis Timeline Node
        genesis_node = await timeline_engine.append_timeline_node(
            db=db,
            user_id=user_id,
            branch_id=root_branch.id,
            parent_node_id=None,
            depth_level=0,
            story_text=initial_story,
            era_year="Genesis Cycle",
            sensory_cue="Pure consciousness; the humming of unwritten realities",
            audio_ambiance="genesis_harmonic",
            entropy_delta=0.0,
            resonance_delta=0.0,
            regret_delta=0.0,
            butterfly_impact="The baseline thread of reality is established."
        )

        # 3. Create Multiverse State Snapshot
        m_state = MultiverseState(
            id=str(uuid.uuid4()),
            branch_id=root_branch.id,
            active_node_id=genesis_node.id,
            total_nodes_count=1,
            world_coherence=1.0,
            timeline_era="Genesis Cycle",
            state_variables={
                "danger_level": "low",
                "surveillance_grid": "inactive",
                "world_stability": 0.85,
                "social_stability": 0.80,
                "technology_level": 0.50
            }
        )
        db.add(m_state)
        await db.flush()

        logger.info(f"Created Root Reality: id={root_branch.id}, code={b_code}")
        return root_branch, genesis_node

    async def create_branch_from_decision(
        self,
        db: AsyncSession,
        user_id: str,
        parent_branch_id: str,
        timeline_node_id: str,
        choice_id: str,
        intention: Optional[str] = None,
        narrative_consequence_proposal: Optional[str] = None,
        custom_branch_name: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a player choice at a timeline node, generating a NEW child reality branch.
        The parent branch and parent timeline nodes remain strictly immutable.
        """
        # 1. Check idempotency: If already executed, retrieve and return existing child branch
        if idempotency_key:
            existing_stmt = select(RealityBranch).where(
                RealityBranch.user_id == user_id,
                RealityBranch.parent_branch_id == parent_branch_id,
                RealityBranch.fork_node_id == timeline_node_id
            )
            existing_res = await db.execute(existing_stmt)
            for cand in existing_res.scalars().all():
                if cand.branch_metadata.get("idempotency_key") == idempotency_key:
                    logger.info(f"Idempotent branch retrieval for key '{idempotency_key}': branch_id={cand.id}")
                    # Fetch active node
                    node_stmt = select(TimelineNode).where(TimelineNode.branch_id == cand.id).order_by(TimelineNode.depth_level.desc())
                    n_res = await db.execute(node_stmt)
                    active_node = n_res.scalars().first()
                    return {
                        "branch": cand,
                        "timeline_node": active_node,
                        "is_idempotent_replay": True
                    }

        # 2. Load and verify parent branch
        parent_stmt = select(RealityBranch).where(
            RealityBranch.id == parent_branch_id,
            RealityBranch.user_id == user_id
        )
        parent_res = await db.execute(parent_stmt)
        parent_branch = parent_res.scalar_one_or_none()
        if not parent_branch:
            raise ValueError(f"Parent branch '{parent_branch_id}' not found or access forbidden.")

        # 3. Load origin timeline node
        origin_node = await timeline_engine.get_node_by_id(db, timeline_node_id, user_id)
        if not origin_node:
            raise ValueError(f"Timeline node '{timeline_node_id}' not found or access forbidden.")

        # 4. Load choice
        choice_stmt = select(Choice).where(Choice.id == choice_id)
        c_res = await db.execute(choice_stmt)
        choice = c_res.scalar_one_or_none()
        if not choice:
            raise ValueError(f"Choice '{choice_id}' not found.")

        # 5. Load parent multiverse state
        state_stmt = select(MultiverseState).where(MultiverseState.branch_id == parent_branch.id)
        s_res = await db.execute(state_stmt)
        parent_m_state = s_res.scalar_one_or_none()
        state_vars = dict(parent_m_state.state_variables) if parent_m_state else {}

        # 6. Load relevant characters for the scenario/world
        char_stmt = select(Character).limit(5)
        char_res = await db.execute(char_stmt)
        chars_data = [{"name": c.name, "role": c.role, "trust": 0.70} for c in char_res.scalars().all()]

        # 7. Deterministic Butterfly Calculations
        butterfly_ripple = butterfly_engine.calculate_butterfly_effects(
            choice_id=choice.id,
            choice_label=choice.choice_label,
            risk_level=choice.risk_level,
            philosophical_vector=choice.philosophical_vector,
            narrative_consequence_proposal=narrative_consequence_proposal,
            characters=chars_data,
            world_state_variables=state_vars
        )

        # 8. Deterministic State Metrics Calculation
        choice_risk_val = 0.2 if choice.risk_level == "low" else (0.5 if choice.risk_level == "moderate" else 0.85)
        entropy_delta = entropy_engine.calculate_entropy_delta(
            current_entropy=parent_branch.entropy_level,
            risk_level=choice.risk_level,
            choice_risk=choice_risk_val,
            depth_level=origin_node.depth_level + 1
        )
        resonance_delta = resonance_engine.calculate_resonance_delta(
            current_resonance=parent_branch.resonance_score,
            choice_philosophical_vector=choice.philosophical_vector,
            choice_risk=choice_risk_val
        )
        regret_delta = regret_engine.calculate_regret_delta(
            current_regret=parent_branch.regret_index,
            risk_level=choice.risk_level
        )
        divergence_mag = clamp(abs(entropy_delta) + abs(resonance_delta) + (choice_risk_val * 0.3))
        destiny_delta = destiny_engine.calculate_destiny_shift_delta(
            divergence_magnitude=divergence_mag,
            entropy_delta=entropy_delta,
            is_major_decision=choice.risk_level in ["high", "existential"],
            depth_level=origin_node.depth_level + 1
        )

        # Build new 7D state vector
        current_vec = MultiverseStateVector(
            entropy=parent_branch.entropy_level,
            resonance=parent_branch.resonance_score,
            regret=parent_branch.regret_index,
            destiny_shift=parent_branch.destiny_shift,
            world_stability=state_vars.get("world_stability", 0.85),
            social_stability=state_vars.get("social_stability", 0.80),
            technology_level=state_vars.get("technology_level", 0.50)
        )
        world_stab_delta = -0.10 if choice.risk_level in ["high", "existential"] else 0.02
        social_stab_delta = -0.15 if choice.philosophical_vector == "Defiance" else 0.05

        new_state_vec = state_engine.calculate_state_transition(
            current_state=current_vec,
            entropy_delta=entropy_delta,
            resonance_delta=resonance_delta,
            regret_delta=regret_delta,
            destiny_shift_delta=destiny_delta,
            world_stability_delta=world_stab_delta,
            social_stability_delta=social_stab_delta
        )

        # 9. Record Decision
        decision = await decision_engine.record_decision(
            db=db,
            user_id=user_id,
            node_id=origin_node.id,
            choice_id=choice.id,
            rationale=f"Executed '{choice.choice_label}' (Intent: {intention or 'Exploration'})",
            intention=intention,
            divergence_magnitude=divergence_mag,
            idempotency_key=idempotency_key
        )

        # 10. Spawn NEW Child Reality Branch (Parent remains untouched!)
        parent_depth = parent_branch.branch_metadata.get("depth", 0)
        new_depth = parent_depth + 1
        root_branch_id = parent_branch.branch_metadata.get("root_branch_id") or parent_branch.id
        short_id = uuid.uuid4().hex[:4].upper()
        branch_code = f"TL-{parent_branch.branch_code.split('-')[-1]}-{short_id}"
        branch_name = custom_branch_name or f"Divergence: {choice.choice_label[:40]}"

        # Apply tertiary butterfly effects to state variables
        for te in butterfly_ripple.tertiary_effects:
            state_vars[te.variable_name] = te.new_value
        state_vars.update({
            "world_stability": new_state_vec.world_stability,
            "social_stability": new_state_vec.social_stability,
            "technology_level": new_state_vec.technology_level
        })

        new_branch = RealityBranch(
            id=str(uuid.uuid4()),
            user_id=user_id,
            future_profile_id=parent_branch.future_profile_id,
            parent_branch_id=parent_branch.id,
            fork_node_id=origin_node.id,
            branch_name=branch_name,
            branch_code=branch_code,
            status="active",
            entropy_level=new_state_vec.entropy,
            resonance_score=new_state_vec.resonance,
            regret_index=new_state_vec.regret,
            destiny_shift=new_state_vec.destiny_shift,
            branch_metadata={
                "depth": new_depth,
                "root_branch_id": root_branch_id,
                "origin_decision_id": decision.id,
                "parent_branch_name": parent_branch.branch_name,
                "idempotency_key": idempotency_key,
                "unlocked_pathways": butterfly_ripple.unlocked_pathways,
                "locked_pathways": butterfly_ripple.locked_pathways
            }
        )
        db.add(new_branch)
        await db.flush()

        # 11. Append Child Timeline Node
        story_content = narrative_consequence_proposal or butterfly_ripple.immediate_effect
        new_node = await timeline_engine.append_timeline_node(
            db=db,
            user_id=user_id,
            branch_id=new_branch.id,
            parent_node_id=origin_node.id,
            depth_level=new_depth,
            story_text=story_content,
            era_year=f"Divergence Era +{new_depth}",
            sensory_cue="Kinetic air; reality boundaries crystallizing",
            entropy_delta=entropy_delta,
            resonance_delta=resonance_delta,
            regret_delta=regret_delta,
            butterfly_impact=f"Immediate: {butterfly_ripple.immediate_effect[:80]}...",
            node_metadata={
                "divergence_magnitude": divergence_mag,
                "philosophical_vector": choice.philosophical_vector,
                "choice_label": choice.choice_label
            }
        )

        # 12. Create Multiverse State for the child branch
        new_m_state = MultiverseState(
            id=str(uuid.uuid4()),
            branch_id=new_branch.id,
            active_node_id=new_node.id,
            total_nodes_count=new_depth + 1,
            world_coherence=round(1.0 - (new_state_vec.entropy * 0.3), 4),
            timeline_era=f"Divergence Era +{new_depth}",
            state_variables=state_vars
        )
        db.add(new_m_state)
        await db.flush()

        # 13. Create Causal Memory
        memory_title = f"Decision at Node #{new_depth}: {choice.choice_label[:50]}"
        memory_content = (
            f"In branch '{new_branch.branch_name}', the traveler made a pivotal choice: '{choice.choice_label}'. "
            f"Immediate result: {butterfly_ripple.immediate_effect} "
            f"State shift: Entropy={new_state_vec.entropy:.2f}, Resonance={new_state_vec.resonance:.2f}, Regret={new_state_vec.regret:.2f}."
        )
        memory = Memory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            branch_id=new_branch.id,
            node_id=new_node.id,
            title=memory_title,
            content=memory_content,
            emotional_tone="dread" if choice.risk_level in ["high", "existential"] else "epiphany",
            memory_type="event",
            clarity_level=1.0,
            memory_metadata={
                "choice_id": choice.id,
                "decision_id": decision.id,
                "unlocked_pathways": butterfly_ripple.unlocked_pathways
            }
        )
        db.add(memory)
        await db.flush()

        # 14. Auto-index memory into RAG pipeline
        try:
            await rag_pipeline.index_memory(db=db, memory=memory, user_id=user_id)
            logger.info(f"Indexed memory '{memory.id}' into RAG vector store for branch '{new_branch.id}'.")
        except Exception as e:
            logger.warning(f"RAG auto-indexing non-fatal warning: {e}")

        logger.info(
            f"Spawned Child Reality Branch: id={new_branch.id}, parent={parent_branch.id}, "
            f"depth={new_depth}, entropy={new_state_vec.entropy}, resonance={new_state_vec.resonance}"
        )

        return {
            "branch": new_branch,
            "timeline_node": new_node,
            "decision": decision,
            "state_vector": new_state_vec,
            "butterfly_ripple": butterfly_ripple,
            "memory": memory,
            "is_idempotent_replay": False
        }

    async def rewind_to_node(
        self,
        db: AsyncSession,
        user_id: str,
        historical_node_id: str,
        rewind_intention: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Time Travel / Rewind Mechanism:
        Rewinds to an earlier historical timeline node by creating a NEW fork branch (Reality A')
        starting from that node. Historical branches and nodes remain completely intact.
        """
        # 1. Load historical node
        hist_node = await timeline_engine.get_node_by_id(db, historical_node_id, user_id)
        if not hist_node:
            raise ValueError(f"Historical timeline node '{historical_node_id}' not found.")

        # 2. Load originating branch
        orig_branch_stmt = select(RealityBranch).where(
            RealityBranch.id == hist_node.branch_id,
            RealityBranch.user_id == user_id
        )
        orig_branch_res = await db.execute(orig_branch_stmt)
        orig_branch = orig_branch_res.scalar_one_or_none()
        if not orig_branch:
            raise ValueError(f"Originating branch for node '{historical_node_id}' not found.")

        # 3. Create parallel fork branch
        root_branch_id = orig_branch.branch_metadata.get("root_branch_id") or orig_branch.id
        short_id = uuid.uuid4().hex[:4].upper()
        fork_code = f"TL-REWIND-{short_id}"
        fork_name = f"Rewind Fork (Node #{hist_node.depth_level})"

        fork_branch = RealityBranch(
            id=str(uuid.uuid4()),
            user_id=user_id,
            future_profile_id=orig_branch.future_profile_id,
            parent_branch_id=orig_branch.id,
            fork_node_id=hist_node.id,
            branch_name=fork_name,
            branch_code=fork_code,
            status="active",
            entropy_level=clamp(orig_branch.entropy_level + 0.05), # Slight entropy cost for rewinding
            resonance_score=orig_branch.resonance_score,
            regret_index=clamp(orig_branch.regret_index * 0.8), # Rewinding offers hope, mitigating immediate regret
            destiny_shift=orig_branch.destiny_shift,
            branch_metadata={
                "depth": hist_node.depth_level,
                "root_branch_id": root_branch_id,
                "is_rewind_fork": True,
                "rewind_source_node_id": hist_node.id,
                "rewind_intention": rewind_intention
            }
        )
        db.add(fork_branch)
        await db.flush()

        # 4. Clone state variables at that point
        m_state = MultiverseState(
            id=str(uuid.uuid4()),
            branch_id=fork_branch.id,
            active_node_id=hist_node.id,
            total_nodes_count=hist_node.depth_level + 1,
            world_coherence=1.0,
            timeline_era=f"Rewind Reality +{hist_node.depth_level}",
            state_variables={"rewind_from_branch": orig_branch.id}
        )
        db.add(m_state)
        await db.flush()

        logger.info(f"Executed Multiverse Rewind: Created fork branch '{fork_branch.id}' from node '{hist_node.id}'.")
        return {
            "fork_branch": fork_branch,
            "anchor_node": hist_node,
            "parent_branch": orig_branch
        }

    async def get_branch_tree(
        self,
        db: AsyncSession,
        user_id: str,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Constructs graph-ready node/edge topology representing the user's multiverse reality tree.
        """
        stmt = (
            select(RealityBranch)
            .where(RealityBranch.user_id == user_id)
            .order_by(RealityBranch.created_at.asc())
        )
        res = await db.execute(stmt)
        branches = res.scalars().all()

        nodes = []
        edges = []

        for b in branches:
            nodes.append({
                "id": b.id,
                "branch_id": b.id,
                "parent_branch_id": b.parent_branch_id,
                "label": b.branch_name,
                "branch_code": b.branch_code,
                "depth": b.branch_metadata.get("depth", 0),
                "entropy": b.entropy_level,
                "resonance": b.resonance_score,
                "regret": b.regret_index,
                "destiny_shift": b.destiny_shift,
                "status": b.status
            })
            if b.parent_branch_id:
                edges.append({
                    "source": b.parent_branch_id,
                    "target": b.id,
                    "decision_id": b.branch_metadata.get("origin_decision_id"),
                    "fork_node_id": b.fork_node_id
                })

        return {
            "total_branches": len(nodes),
            "nodes": nodes,
            "edges": edges
        }

    async def compare_branches(
        self,
        db: AsyncSession,
        user_id: str,
        branch_a_id: str,
        branch_b_id: str
    ) -> Dict[str, Any]:
        """
        Performs a comprehensive multidimensional comparison between two reality branches.
        """
        stmt = select(RealityBranch).where(
            RealityBranch.id.in_([branch_a_id, branch_b_id]),
            RealityBranch.user_id == user_id
        )
        res = await db.execute(stmt)
        branches = {b.id: b for b in res.scalars().all()}

        if branch_a_id not in branches or branch_b_id not in branches:
            raise ValueError("One or both branches not found or access forbidden.")

        b_a = branches[branch_a_id]
        b_b = branches[branch_b_id]

        # Load timeline nodes count
        nodes_a = await timeline_engine.get_timeline_nodes(db, b_a.id, user_id)
        nodes_b = await timeline_engine.get_timeline_nodes(db, b_b.id, user_id)

        entropy_diff = round(b_b.entropy_level - b_a.entropy_level, 4)
        resonance_diff = round(b_b.resonance_score - b_a.resonance_score, 4)
        regret_diff = round(b_b.regret_index - b_a.regret_index, 4)
        destiny_diff = round(b_b.destiny_shift - b_a.destiny_shift, 4)

        if abs(destiny_diff) > 0.4:
            divergence_verdict = "Radical Multiverse Divergence"
        elif abs(destiny_diff) > 0.15:
            divergence_verdict = "Significant Timeline Deviation"
        else:
            divergence_verdict = "Close Parallel Harmonic"

        return {
            "branch_a": {
                "id": b_a.id,
                "name": b_a.branch_name,
                "code": b_a.branch_code,
                "depth": b_a.branch_metadata.get("depth", 0),
                "nodes_count": len(nodes_a),
                "entropy": b_a.entropy_level,
                "resonance": b_a.resonance_score,
                "regret": b_a.regret_index,
                "destiny_shift": b_a.destiny_shift
            },
            "branch_b": {
                "id": b_b.id,
                "name": b_b.branch_name,
                "code": b_b.branch_code,
                "depth": b_b.branch_metadata.get("depth", 0),
                "nodes_count": len(nodes_b),
                "entropy": b_b.entropy_level,
                "resonance": b_b.resonance_score,
                "regret": b_b.regret_index,
                "destiny_shift": b_b.destiny_shift
            },
            "metrics_differential": {
                "entropy_delta": entropy_diff,
                "resonance_delta": resonance_diff,
                "regret_delta": regret_diff,
                "destiny_shift_delta": destiny_diff
            },
            "divergence_verdict": divergence_verdict
        }

branch_engine = BranchEngine()
