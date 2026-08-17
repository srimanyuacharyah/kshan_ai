from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator

# ----------------- ATOMIC MODELS -----------------

class BranchingChoice(BaseModel):
    id: str = Field(..., description="Unique choice identifier (e.g. choice_a, choice_b, choice_c)")
    title: str = Field(..., min_length=2, description="Concise choice label")
    description: str = Field(..., min_length=5, description="Full explanation of the action")
    immediate_effect: str = Field(..., description="Instant consequence of making this choice")
    long_term_consequence: str = Field(..., description="Distant butterfly effect across the timeline")
    risk: float = Field(..., ge=0.0, le=1.0, description="Risk factor between 0.0 and 1.0")
    resonance: float = Field(..., ge=0.0, le=1.0, description="Harmonic alignment between 0.0 and 1.0")
    entropy_delta: float = Field(..., ge=-1.0, le=1.0, description="Predicted entropy shift")

class ContextSource(BaseModel):
    source_type: str # "rag_memory", "mcp_world", "mcp_timeline", "mcp_decision"
    title: str
    snippet: str

# ----------------- STRUCTURED AI OUTPUT SCHEMAS -----------------

class BranchGenerationResponse(BaseModel):
    generation_id: str
    choices: List[BranchingChoice] = Field(..., min_length=3, max_length=3)
    divergence_reasoning: str
    context_sources: List[ContextSource] = Field(default_factory=list)
    simulation_notes: Optional[str] = None

class StoryGenerationResponse(BaseModel):
    generation_id: str
    narrative: str
    choices: List[BranchingChoice] = Field(..., min_length=3, max_length=3, description="Exactly 3 distinct narrative paths")
    foreshadowing: Optional[List[str]] = Field(default_factory=list)
    context_sources: List[ContextSource] = Field(default_factory=list)

class FutureYouResponse(BaseModel):
    generation_id: str
    is_fictional_simulation: bool = Field(default=True, description="Strict marker establishing fictional simulation")
    identity: str = Field(..., description="Full title / identity of the alternate self")
    age: str
    world: str
    occupation: str
    personality: str
    relationships: List[str] = Field(default_factory=list)
    major_life_events: List[str] = Field(default_factory=list)
    regrets: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    message_to_present_self: str = Field(..., description="Empathetic in-character message to traveler")

class WorldGenerationResponse(BaseModel):
    generation_id: str
    world_name: str
    era: str
    geography: str
    atmosphere: str
    governing_system: str
    technology_level: str
    factions: List[Dict[str, str]] = Field(default_factory=list) # [{"name": "...", "doctrine": "..."}]
    cultural_rules: List[str] = Field(default_factory=list)
    physics_supernatural_rules: str
    major_locations: List[Dict[str, str]] = Field(default_factory=list) # [{"name": "...", "description": "..."}]

class CharacterGenerationResponse(BaseModel):
    generation_id: str
    name: str
    role: str
    background: str
    personality: str
    motivations: List[str] = Field(default_factory=list)
    fears: List[str] = Field(default_factory=list)
    relationships: Dict[str, str] = Field(default_factory=dict)
    dialogue_style: str
    character_arc: str

class ConsequenceResponse(BaseModel):
    generation_id: str
    narrative_consequence: str = Field(..., description="AI narrative description of unfolding consequence")
    calculated_entropy_delta: float
    calculated_resonance_delta: float
    calculated_regret_delta: float
    divergence_magnitude: float
    destiny_shift: str
    new_entropy: float
    new_resonance: float
    new_regret: float

class DecisionAnalysisResponse(BaseModel):
    generation_id: str
    decision_id: str
    philosophical_weight: str
    systemic_implications: str
    parallel_paths_unlocked: List[str] = Field(default_factory=list)
    hidden_tradeoffs: List[str] = Field(default_factory=list)
    advice_for_traveler: str

# ----------------- API REQUEST SCHEMAS -----------------

class StoryGenerationRequest(BaseModel):
    scenario_id: str
    branch_id: str
    prompt_seed: Optional[str] = None
    custom_intention: Optional[str] = None

class BranchGenerationRequest(BaseModel):
    scenario_id: str
    branch_id: str
    timeline_node_id: Optional[str] = None
    intention: Optional[str] = None

class FutureYouRequest(BaseModel):
    scenario_id: Optional[str] = None
    branch_id: Optional[str] = None
    user_question: Optional[str] = None
    message: Optional[str] = None

class WorldGenerationRequest(BaseModel):
    scenario_id: str
    theme_prompt: str
    cosmos_type: str = "Parallel Earth"

class CharacterGenerationRequest(BaseModel):
    world_id: str
    role_description: str
    faction_preference: Optional[str] = None

class DecisionAnalysisRequest(BaseModel):
    branch_id: str
    node_id: str
    chosen_choice_id: Optional[str] = None
    choice_id: Optional[str] = None
    rationale: Optional[str] = None
