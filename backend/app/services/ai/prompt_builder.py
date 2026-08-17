from typing import Dict, Any, List, Optional

PROMPT_VERSION_V1 = "KSHAN_SYSTEM_PROMPT_V1"

KSHAN_SYSTEM_PROMPT_V1 = """You are KSHAN — Multiverse Intelligence, the authoritative narrative engine for KSHAN: "One Moment. Infinite Lives. Your choices create worlds that never existed."

CORE AXIOMS:
1. FICTIONAL SIMULATION: KSHAN is a fictional multiverse simulation. You must strictly remain inside this fictional universe. Never claim to predict or dictate the user's real life or future.
2. NARRATIVE CONTINUITY: Always maintain strict continuity with established world lore, character dossiers, previous decisions, and memory shards provided in the context.
3. PRESERVE WORLD RULES: Obey the laws of physics, technology level, and factions established for the active cosmos.
4. NO ARBITRARY STATE CONTRADICTION: Never contradict known timeline facts without explicitly explaining the quantum divergence causing the shift.
5. FUTURE YOU FRAMING: When manifesting the persona of 'Future You', you are a fictional alternate manifestation of the voyager from a parallel timeline branch. Embody the personality and memories with warmth, depth, and philosophical gravity while never claiming to be a real psychic prophecy.
6. STRUCTURED INTEGRITY: You MUST return valid, well-formed JSON conforming precisely to the requested schema. Do NOT include markdown code blocks (```json) in your raw output when structured mode is active.
"""

class PromptBuilder:
    """
    Constructs versioned, grounded prompts for the Gemini client.
    """

    def __init__(self, prompt_version: str = PROMPT_VERSION_V1):
        self.prompt_version = prompt_version

    def build_story_prompt(
        self,
        world_lore: str,
        branch_state: Dict[str, Any],
        recent_decisions: List[Dict[str, Any]],
        grounded_context: str,
        intention: Optional[str] = None
    ) -> str:
        intention_block = f"\nVoyager Intention: {intention}" if intention else ""
        return f"""Task: Generate the next immersive timeline event and 3 branching choices for the voyager.

{self._format_context_block(world_lore, branch_state, recent_decisions, grounded_context)}
{intention_block}

Requirements:
- Generate a vivid, poetic, cinematic narrative continuation (minimum 20 words).
- Describe the environmental atmosphere and sensory details (sound, visual, tactile).
- Produce EXACTLY 3 distinct, impactful choices representing genuinely different philosophical and strategic paths.
- Each choice must include: id (choice_a, choice_b, choice_c), title, description, immediate_effect, long_term_consequence, risk (0.0 to 1.0), resonance (0.0 to 1.0), and entropy_delta (-1.0 to 1.0).
- Return JSON strictly adhering to the StoryGenerationResponse schema.
"""

    def build_branch_choices_prompt(
        self,
        current_node_text: str,
        world_lore: str,
        branch_state: Dict[str, Any],
        grounded_context: str,
        intention: Optional[str] = None
    ) -> str:
        intention_block = f"\nVoyager Intention / Query: {intention}" if intention else ""
        return f"""Task: Generate EXACTLY 3 divergent, non-superficial branching choices from the current timeline node.

Current Timeline Moment:
"{current_node_text}"

{self._format_context_block(world_lore, branch_state, [], grounded_context)}
{intention_block}

Requirements:
- Choice A: Direct action / confrontation / leap into the unknown.
- Choice B: Diplomatic, systemic, or investigative approach.
- Choice C: Subversive, introspective, or reality-altering divergence.
- Each choice must contain realistic trade-offs, immediate effects, and distant consequences.
- Return JSON strictly adhering to the BranchGenerationResponse schema.
"""

    def build_future_you_prompt(
        self,
        user_question: str,
        branch_summary: Dict[str, Any],
        grounded_memories: str,
        world_name: str
    ) -> str:
        return f"""Task: Manifest the fictional persona of 'Future You' from parallel reality branch '{branch_summary.get('branch_code', 'TL-PRIME')}'.

Voyager's Question to Future You:
"{user_question}"

Active Reality Parameters:
- World: {world_name}
- Entropy Level: {branch_summary.get('entropy', 0.5)}
- Resonance Score: {branch_summary.get('resonance', 0.5)}
- Timeline Era: {branch_summary.get('era', 'Genesis')}

Retrieved Memory Shards & Chronicle:
{grounded_memories}

Requirements:
- Respond in-character as the traveler's alternate future self who lived through the consequences of this branch.
- Explicitly mark is_fictional_simulation as true.
- Include identity, age, occupation, personality, key achievements, haunting regrets, and an empathetic message to the present voyager.
- Return JSON adhering to FutureYouResponse schema.
"""

    def build_world_prompt(self, theme_prompt: str, cosmos_type: str) -> str:
        return f"""Task: Generate a rich, coherent sci-fi / mythic multiverse world.

Theme: {theme_prompt}
Cosmos Type: {cosmos_type}

Requirements:
- Generate a unique name, era, geography, atmosphere, technology level, and governing system.
- Detail physics/supernatural laws, at least 2 distinct factions, cultural taboos/rules, and 2 iconic locations.
- Return JSON adhering to WorldGenerationResponse schema.
"""

    def build_character_prompt(self, world_lore: str, role_description: str, faction: Optional[str] = None) -> str:
        faction_block = f"\nPreferred Faction: {faction}" if faction else ""
        return f"""Task: Create a deep, multidimensional NPC or companion character for the world.

World Context:
{world_lore}

Role Description:
{role_description}
{faction_block}

Requirements:
- Generate name, role, backstory, psychological traits, motivations, fears, dialogue style, and character arc.
- Return JSON adhering to CharacterGenerationResponse schema.
"""

    def build_decision_analysis_prompt(
        self,
        chosen_action: str,
        action_description: str,
        rationale: str,
        world_rules: str,
        past_decisions_summary: str
    ) -> str:
        return f"""Task: Perform deep multiverse analysis on the turning point decision taken by the voyager.

Action Chosen: {chosen_action}
Description: {action_description}
Voyager Rationale: {rationale or 'Intuitive Leap'}

Context:
World Rules: {world_rules}
Past Timeline Decisions: {past_decisions_summary}

Requirements:
- Analyze philosophical weight, systemic implications across factions, parallel paths unlocked, hidden tradeoffs, and advice.
- Return JSON adhering to DecisionAnalysisResponse schema.
"""

    def _format_context_block(
        self,
        world_lore: str,
        branch_state: Dict[str, Any],
        recent_decisions: List[Dict[str, Any]],
        grounded_context: str
    ) -> str:
        decisions_text = "\n".join(
            f"- [{d.get('era_year', 'Past')}]: {d.get('chosen_action')} (Rationale: {d.get('rationale', 'N/A')})"
            for d in recent_decisions
        ) if recent_decisions else "No recorded prior turning points."

        return f"""Active World Lore:
{world_lore}

Branch State Metrics:
- Code: {branch_state.get('branch_code', 'TL-PRIME')}
- Entropy: {branch_state.get('entropy', 0.2)}
- Resonance: {branch_state.get('resonance', 0.8)}
- Regret Index: {branch_state.get('regret', 0.0)}

Recent Turning Points:
{decisions_text}

Grounded RAG Context:
{grounded_context or 'No memory echoes found.'}"""

prompt_builder = PromptBuilder()
