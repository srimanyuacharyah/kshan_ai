from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.services.multiverse.state_engine import clamp

class CharacterEffect(BaseModel):
    character_name: str
    trust_delta: float = Field(..., ge=-1.0, le=1.0)
    new_status: str
    notes: str

class WorldEffect(BaseModel):
    variable_name: str
    previous_value: Any
    new_value: Any
    description: str

class ButterflyRipple(BaseModel):
    immediate_effect: str = Field(..., description="Tier 1: Direct consequence on the active moment")
    secondary_effects: List[CharacterEffect] = Field(default_factory=list, description="Tier 2: Character loyalties, allegiances, emotional reactions")
    tertiary_effects: List[WorldEffect] = Field(default_factory=list, description="Tier 3: Locations, environment, faction power, security status")
    long_term_effects: List[str] = Field(default_factory=list, description="Tier 4: Future timeline event unlocks, locks, and systemic trajectory shifts")
    unlocked_pathways: List[str] = Field(default_factory=list)
    locked_pathways: List[str] = Field(default_factory=list)

class ButterflyEngine:
    """
    Deterministic Butterfly Effect Propagation Engine.
    Propagates a player's choice through 4 distinct causal tiers:
    1. Immediate Effect (Instant narrative & physical result)
    2. Secondary Effects (Character trust & faction shifts)
    3. Tertiary Effects (World state & location parameters)
    4. Long-Term Possibilities (Future event locks/unlocks)
    """

    def calculate_butterfly_effects(
        self,
        choice_id: str,
        choice_label: str,
        risk_level: str,
        philosophical_vector: Optional[str] = None,
        narrative_consequence_proposal: Optional[str] = None,
        characters: Optional[List[Dict[str, Any]]] = None,
        world_state_variables: Optional[Dict[str, Any]] = None
    ) -> ButterflyRipple:
        characters = characters or []
        world_state_variables = world_state_variables or {}

        # 1. Tier 1: Immediate Effect
        if narrative_consequence_proposal and len(narrative_consequence_proposal) > 10:
            immediate = narrative_consequence_proposal
        else:
            immediate = f"Execution of '{choice_label}' triggered immediate causal divergence."

        # 2. Tier 2: Secondary Effects (Character loyalty/trust shifts)
        secondary_effects = []
        for char in characters:
            char_name = char.get("name", "Companion")
            curr_trust = char.get("trust", 0.70)
            
            # Deterministic trust delta based on philosophical alignment and risk
            if philosophical_vector == "Defiance":
                if char.get("role") in ["Rebel", "Smuggler", "Rogue"]:
                    trust_delta = +0.15
                    new_status = "Emboldened Ally"
                    notes = f"{char_name} respects your uncompromising defiance."
                else:
                    trust_delta = -0.20
                    new_status = "Alarmed / Cautious"
                    notes = f"{char_name} fears the dangerous exposure caused by your defiance."
            elif philosophical_vector == "Submission":
                if char.get("role") in ["Rebel", "Rogue"]:
                    trust_delta = -0.25
                    new_status = "Disillusioned"
                    notes = f"{char_name} views your surrender as a compromise of principles."
                else:
                    trust_delta = +0.10
                    new_status = "Reassured"
                    notes = f"{char_name} appreciates your focus on immediate survival."
            elif philosophical_vector == "Transcendence":
                trust_delta = +0.10
                new_status = "Reverent"
                notes = f"{char_name} is awed by the metaphysical shift in reality."
            else: # Default or Pragmatism
                trust_delta = -0.05 if risk_level in ["high", "existential"] else +0.05
                new_status = "Observant"
                notes = f"{char_name} is closely monitoring your decisions."

            secondary_effects.append(CharacterEffect(
                character_name=char_name,
                trust_delta=round(trust_delta, 2),
                new_status=new_status,
                notes=notes
            ))

        # 3. Tier 3: Tertiary Effects (World state & environment)
        tertiary_effects = []
        prev_danger = world_state_variables.get("danger_level", "low")
        prev_surveillance = world_state_variables.get("surveillance_grid", "active")

        if risk_level in ["high", "existential"]:
            tertiary_effects.append(WorldEffect(
                variable_name="surveillance_grid",
                previous_value=prev_surveillance,
                new_value="heightened_alert",
                description="City security forces deployed surveillance drones to your sector."
            ))
            tertiary_effects.append(WorldEffect(
                variable_name="danger_level",
                previous_value=prev_danger,
                new_value="elevated",
                description="Local districts have been locked down due to reality fluctuations."
            ))
        else:
            tertiary_effects.append(WorldEffect(
                variable_name="danger_level",
                previous_value=prev_danger,
                new_value="moderate",
                description="Subtle ripple in the electromagnetic grid recorded by local archivists."
            ))

        # 4. Tier 4: Long-Term Possibilities & Unlocks/Locks
        unlocked = []
        locked = []
        long_term = []

        if philosophical_vector == "Defiance":
            unlocked.append("The Subterranean Underground Enclave")
            locked.append("High Council Diplomatic Amnesty")
            long_term.append("The authoritarian syndicate permanently flags your identity as a rogue divergent.")
        elif philosophical_vector == "Submission":
            unlocked.append("Sanctioned Corporate Vault Access")
            locked.append("The Weavers' Inner Sanctum")
            long_term.append("Historical records are permanently redacted to reflect official ministry truth.")
        else:
            unlocked.append("Quantum Nexus Resonance Channel")
            long_term.append("A latent chronos-rift begins expanding in the periphery of Neo-Kashi.")

        return ButterflyRipple(
            immediate_effect=immediate,
            secondary_effects=secondary_effects,
            tertiary_effects=tertiary_effects,
            long_term_effects=long_term,
            unlocked_pathways=unlocked,
            locked_pathways=locked
        )

butterfly_engine = ButterflyEngine()
