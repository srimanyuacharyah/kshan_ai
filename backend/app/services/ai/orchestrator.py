import time
import hashlib
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.core.logging import logger
from backend.app.models.base import Base
from backend.app.models.generation import GenerationHistory
from backend.app.models.multiverse import RealityBranch, MultiverseState
from backend.app.models.timeline import TimelineNode, Choice, Decision
from backend.app.models.world import World, Location, Character
from backend.app.models.scenario import Scenario

from backend.app.services.engine.consequence_engine import consequence_engine, MultiverseStateTransition
from backend.app.services.rag.rag_pipeline import rag_pipeline
from backend.app.services.mcp.client import mcp_client
from backend.app.services.ai.gemini_client import gemini_client
from backend.app.services.ai.prompt_builder import prompt_builder, KSHAN_SYSTEM_PROMPT_V1, PROMPT_VERSION_V1
from backend.app.services.ai.context_builder import context_budget_manager
from backend.app.services.ai.response_validator import response_validator
from backend.app.services.ai.rate_limiter import rate_limiter
from backend.app.services.ai.exceptions import AIGenerationError, ResponseValidationError
from backend.app.core.security import create_access_token
from backend.app.services.mcp.exceptions import MCPAuthorizationError
from backend.app.services.ai.schemas import (
    StoryGenerationResponse,
    BranchGenerationResponse,
    FutureYouResponse,
    WorldGenerationResponse,
    CharacterGenerationResponse,
    DecisionAnalysisResponse,
    BranchingChoice,
    ContextSource
)

class AIOrchestrator:
    """
    Central Intelligence Layer of KSHAN:
    Orchestrates Gemini GenAI, pgvector RAG, MCP context tools, and the deterministic consequence engine.
    """

    async def _verify_tenant_branch(self, db: AsyncSession, user_id: str, branch_id: str) -> RealityBranch:
        """Enforces tenant isolation before invoking any AI or context services."""
        query = select(RealityBranch).where(
            RealityBranch.id == branch_id,
            RealityBranch.user_id == user_id
        )
        res = await db.execute(query)
        branch = res.scalar_one_or_none()
        if not branch:
            logger.warning(f"Tenant isolation rejection: user_id='{user_id}' cannot access branch='{branch_id}'.")
            raise MCPAuthorizationError(f"Unauthorized: Branch '{branch_id}' does not belong to the authenticated user.")
        return branch

    async def _record_generation(
        self,
        db: AsyncSession,
        user_id: str,
        generation_type: str,
        gen_id: str,
        scenario_id: Optional[str],
        branch_id: Optional[str],
        latency_ms: float,
        rag_count: int,
        mcp_tools: List[str],
        context_str: str,
        status: str = "success"
    ):
        """Persists generation metadata to the database for auditing and telemetry."""
        ctx_hash = hashlib.sha256(context_str.encode("utf-8")).hexdigest()[:16]
        history = GenerationHistory(
            id=gen_id,
            user_id=user_id,
            scenario_id=scenario_id,
            branch_id=branch_id,
            generation_type=generation_type,
            model=gemini_client.model_name if not gemini_client.demo_mode else "kshan-mock-engine",
            prompt_version=PROMPT_VERSION_V1,
            input_context_hash=ctx_hash,
            latency_ms=latency_ms,
            rag_retrievals_count=float(rag_count),
            mcp_tools_invoked=mcp_tools,
            status=status
        )
        db.add(history)
        await db.flush()
        await db.commit()
        logger.info(f"Recorded generation history: id={gen_id}, type={generation_type}")

    async def generate_story(
        self,
        db: AsyncSession,
        user_id: str,
        scenario_id: str,
        branch_id: str,
        prompt_seed: Optional[str] = None,
        custom_intention: Optional[str] = None,
        auth_token: Optional[str] = None
    ) -> StoryGenerationResponse:
        """Generates grounded narrative continuation with 3 branching choices."""
        rate_limiter.check_and_record(user_id)
        start_time = time.perf_counter()
        branch = await self._verify_tenant_branch(db, user_id, branch_id)

        # 1. RAG + MCP Context Retrieval (Intelligent Selection)
        mcp_tools_called = ["get_story_context"]
        story_ctx = await mcp_client.call_tool(
            "get_story_context",
            {"branch_id": branch.id, "query": prompt_seed or custom_intention or "Narrative continuation", "scenario_id": scenario_id},
            auth_token=auth_token
        )
        ctx_data = story_ctx.data if story_ctx.success else {}

        # 2. Context Budget Assembly
        budgeted = context_budget_manager.assemble_budgeted_context(
            branch_state=ctx_data.get("branch_summary", {"branch_name": branch.branch_name, "branch_code": branch.branch_code}),
            recent_decisions=ctx_data.get("recent_decisions", [])
        )

        # 3. Prompt Construction
        prompt = prompt_builder.build_story_prompt(
            world_lore=f"Scenario ID: {scenario_id}",
            branch_state=ctx_data.get("branch_summary", {}),
            recent_decisions=ctx_data.get("recent_decisions", []),
            grounded_context=budgeted["grounded_text"],
            intention=custom_intention or prompt_seed
        )

        # 4. Structured Gemini Generation
        response = await gemini_client.generate_structured(
            prompt=prompt,
            system_instruction=KSHAN_SYSTEM_PROMPT_V1,
            schema_class=StoryGenerationResponse,
            generation_type="story"
        )
        response.context_sources = budgeted["sources"]

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        await self._record_generation(
            db=db,
            user_id=user_id,
            generation_type="story",
            gen_id=response.generation_id,
            scenario_id=scenario_id,
            branch_id=branch_id,
            latency_ms=elapsed_ms,
            rag_count=ctx_data.get("retrieved_chunks_count", 0),
            mcp_tools=mcp_tools_called,
            context_str=budgeted["grounded_text"]
        )
        return response

    async def generate_branching_choices(
        self,
        db: AsyncSession,
        user_id: str,
        scenario_id: str,
        branch_id: str,
        timeline_node_id: Optional[str] = None,
        intention: Optional[str] = None,
        auth_token: Optional[str] = None
    ) -> BranchGenerationResponse:
        """Generates exactly 3 distinct, divergent choices for the active node."""
        rate_limiter.check_and_record(user_id)
        start_time = time.perf_counter()
        branch = await self._verify_tenant_branch(db, user_id, branch_id)

        # 1. Fetch Timeline Node Text
        current_node_text = "Genesis Point"
        if timeline_node_id:
            node_res = await db.execute(
                select(TimelineNode).where(TimelineNode.id == timeline_node_id, TimelineNode.user_id == user_id)
            )
            node = node_res.scalar_one_or_none()
            if node:
                current_node_text = node.story_text

        # 2. RAG Context Search
        rag_data = await rag_pipeline.search_and_ground(
            db=db,
            query=intention or current_node_text,
            user_id=user_id,
            branch_id=branch.id,
            scenario_id=scenario_id,
            top_k=3
        )

        budgeted = context_budget_manager.assemble_budgeted_context(
            branch_state={"branch_name": branch.branch_name, "branch_code": branch.branch_code, "entropy": branch.entropy_level, "resonance": branch.resonance_score},
            rag_memories=[{"title": r.document_title, "content": r.content} for r in rag_data.results]
        )

        # 3. Prompt Construction
        prompt = prompt_builder.build_branch_choices_prompt(
            current_node_text=current_node_text,
            world_lore=f"Scenario: {scenario_id}",
            branch_state={"branch_code": branch.branch_code, "entropy": branch.entropy_level, "resonance": branch.resonance_score},
            grounded_context=budgeted["grounded_text"],
            intention=intention
        )

        # 4. Structured Generation
        response = await gemini_client.generate_structured(
            prompt=prompt,
            system_instruction=KSHAN_SYSTEM_PROMPT_V1,
            schema_class=BranchGenerationResponse,
            generation_type="branch"
        )
        response.context_sources = budgeted["sources"]

        # Ensure exactly 3 choices
        if len(response.choices) != 3:
            raise ResponseValidationError(f"Expected exactly 3 branching choices, received {len(response.choices)}.")

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        await self._record_generation(
            db=db,
            user_id=user_id,
            generation_type="branch",
            gen_id=response.generation_id,
            scenario_id=scenario_id,
            branch_id=branch_id,
            latency_ms=elapsed_ms,
            rag_count=rag_data.results_count,
            mcp_tools=["search_memories"],
            context_str=budgeted["grounded_text"]
        )
        return response

    async def generate_future_you(
        self,
        db: AsyncSession,
        user_id: str,
        scenario_id: str,
        branch_id: str,
        user_question: str,
        auth_token: Optional[str] = None
    ) -> FutureYouResponse:
        """Manifests Future You persona grounded by branch state and memory shards."""
        rate_limiter.check_and_record(user_id)
        start_time = time.perf_counter()
        auth_token = auth_token or create_access_token(user_id)
        branch = await self._verify_tenant_branch(db, user_id, branch_id)

        # 1. RAG Search for memories
        rag_data = await rag_pipeline.search_and_ground(
            db=db,
            query=user_question,
            user_id=user_id,
            branch_id=branch.id,
            scenario_id=scenario_id,
            top_k=4
        )

        # 2. MCP State
        default_metrics = {"branch_code": branch.branch_code, "entropy": branch.entropy_level, "resonance": branch.resonance_score}
        try:
            state_call = await mcp_client.call_tool("get_branch_state", {"branch_id": branch.id}, auth_token=auth_token)
            raw_data = state_call.data if state_call.success else {}
            if isinstance(raw_data, dict):
                branch_metrics = raw_data.get("metrics", default_metrics)
                if not isinstance(branch_metrics, dict):
                    branch_metrics = default_metrics
            else:
                branch_metrics = default_metrics
        except Exception as e:
            logger.warning(f"MCP get_branch_state fallback: {e}")
            branch_metrics = default_metrics

        # 3. Prompt Construction
        prompt = prompt_builder.build_future_you_prompt(
            user_question=user_question,
            branch_summary=branch_metrics,
            grounded_memories=rag_data.context,
            world_name="Neo-Kashi Prime"
        )

        # 4. Structured Generation
        response = await gemini_client.generate_structured(
            prompt=prompt,
            system_instruction=KSHAN_SYSTEM_PROMPT_V1,
            schema_class=FutureYouResponse,
            generation_type="future_you"
        )
        response.is_fictional_simulation = True

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        await self._record_generation(
            db=db,
            user_id=user_id,
            generation_type="future_you",
            gen_id=response.generation_id,
            scenario_id=scenario_id,
            branch_id=branch_id,
            latency_ms=elapsed_ms,
            rag_count=rag_data.results_count,
            mcp_tools=["get_branch_state"],
            context_str=rag_data.context
        )
        return response

    async def generate_world(
        self,
        db: AsyncSession,
        user_id: str,
        scenario_id: str,
        theme_prompt: str,
        cosmos_type: str = "Parallel Earth"
    ) -> WorldGenerationResponse:
        """Generates a rich multiverse world, persists it to DB, and indexes into RAG."""
        rate_limiter.check_and_record(user_id)
        start_time = time.perf_counter()

        prompt = prompt_builder.build_world_prompt(theme_prompt=theme_prompt, cosmos_type=cosmos_type)
        response = await gemini_client.generate_structured(
            prompt=prompt,
            system_instruction=KSHAN_SYSTEM_PROMPT_V1,
            schema_class=WorldGenerationResponse,
            generation_type="world"
        )

        # Persist generated World into DB
        world = World(
            scenario_id=scenario_id,
            name=response.world_name,
            cosmos_type=cosmos_type,
            lore_chronicle=f"Era: {response.era}\nGeography: {response.geography}\nAtmosphere: {response.atmosphere}",
            laws_of_physics=response.physics_supernatural_rules,
            factions_overview="; ".join(f"{f.get('name')}: {f.get('doctrine')}" for f in response.factions)
        )
        db.add(world)
        await db.flush()

        # Add Locations
        for loc in response.major_locations:
            l_obj = Location(
                world_id=world.id,
                name=loc.get("name", "Landmark"),
                realm_zone="Central Zone",
                description=loc.get("description", "A notable location."),
                danger_rating=0.3
            )
            db.add(l_obj)

        await db.flush()
        # Index world into RAG
        await rag_pipeline.index_world(db, world, user_id)
        await db.commit()

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        await self._record_generation(
            db=db,
            user_id=user_id,
            generation_type="world",
            gen_id=response.generation_id,
            scenario_id=scenario_id,
            branch_id=None,
            latency_ms=elapsed_ms,
            rag_count=0,
            mcp_tools=[],
            context_str=theme_prompt
        )
        return response

    async def generate_character(
        self,
        db: AsyncSession,
        user_id: str,
        world_id: str,
        role_description: str,
        faction_preference: Optional[str] = None
    ) -> CharacterGenerationResponse:
        """Generates an NPC/companion, persists it to DB, and indexes into RAG."""
        rate_limiter.check_and_record(user_id)
        start_time = time.perf_counter()

        # Query World lore for context
        world_res = await db.execute(select(World).where(World.id == world_id))
        world = world_res.scalar_one_or_none()
        world_lore = world.lore_chronicle if world else "Cosmic Realm"

        prompt = prompt_builder.build_character_prompt(
            world_lore=world_lore,
            role_description=role_description,
            faction=faction_preference
        )

        response = await gemini_client.generate_structured(
            prompt=prompt,
            system_instruction=KSHAN_SYSTEM_PROMPT_V1,
            schema_class=CharacterGenerationResponse,
            generation_type="character"
        )

        # Persist Character in DB
        char = Character(
            world_id=world_id,
            name=response.name,
            role=response.role,
            faction=faction_preference or (list(response.relationships.keys())[0] if response.relationships else "Independent"),
            backstory=response.background,
            psychological_profile=response.personality,
            dialogue_style=response.dialogue_style
        )
        db.add(char)
        await db.flush()

        # Index into RAG
        await rag_pipeline.index_character(db, char, user_id)
        await db.commit()

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        await self._record_generation(
            db=db,
            user_id=user_id,
            generation_type="character",
            gen_id=response.generation_id,
            scenario_id=world.scenario_id if world else None,
            branch_id=None,
            latency_ms=elapsed_ms,
            rag_count=0,
            mcp_tools=[],
            context_str=role_description
        )
        return response

    async def analyze_decision(
        self,
        db: AsyncSession,
        user_id: str,
        branch_id: str,
        node_id: str,
        chosen_choice_id: str,
        rationale: Optional[str] = None,
        auth_token: Optional[str] = None
    ) -> DecisionAnalysisResponse:
        """Performs systemic and philosophical analysis of a chosen turning point."""
        rate_limiter.check_and_record(user_id)
        start_time = time.perf_counter()
        branch = await self._verify_tenant_branch(db, user_id, branch_id)

        # Fetch choice and node
        choice_res = await db.execute(select(Choice).where(Choice.id == chosen_choice_id))
        choice = choice_res.scalar_one_or_none()
        action_label = choice.choice_label if choice else "Pivotal Decision"
        action_desc = choice.choice_description if choice else "An impactful path taken."

        prompt = prompt_builder.build_decision_analysis_prompt(
            chosen_action=action_label,
            action_description=action_desc,
            rationale=rationale or "Intuitive Path",
            world_rules="Standard Multiverse Resonance Rules",
            past_decisions_summary=f"Branch {branch.branch_code} at entropy {branch.entropy_level}"
        )

        response = await gemini_client.generate_structured(
            prompt=prompt,
            system_instruction=KSHAN_SYSTEM_PROMPT_V1,
            schema_class=DecisionAnalysisResponse,
            generation_type="decision_analysis"
        )
        response.decision_id = f"dec_{chosen_choice_id[:8]}"

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        await self._record_generation(
            db=db,
            user_id=user_id,
            generation_type="decision_analysis",
            gen_id=response.generation_id,
            scenario_id=None,
            branch_id=branch_id,
            latency_ms=elapsed_ms,
            rag_count=0,
            mcp_tools=["get_recent_decisions"],
            context_str=action_label
        )
        return response

    def evaluate_deterministic_consequence(
        self,
        current_entropy: float,
        current_resonance: float,
        current_regret: float,
        choice_risk: float,
        risk_level: str = "moderate",
        philosophical_vector: Optional[str] = None,
        profile_archetype: Optional[str] = None
    ) -> MultiverseStateTransition:
        """Deterministic mathematical consequence transition using the consequence engine."""
        return consequence_engine.process_decision_consequence(
            current_entropy=current_entropy,
            current_resonance=current_resonance,
            current_regret=current_regret,
            risk_level=risk_level,
            choice_risk=choice_risk,
            choice_philosophical_vector=philosophical_vector,
            profile_archetype=profile_archetype
        )

ai_orchestrator = AIOrchestrator()
