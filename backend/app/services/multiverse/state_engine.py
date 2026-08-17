import math
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class MultiverseStateVector(BaseModel):
    """
    7-Dimensional Multiverse State Vector.
    Strictly bounded between 0.0 and 1.0 with NaN safety protections.
    """
    entropy: float = Field(default=0.10, ge=0.0, le=1.0, description="System chaos and timeline instability")
    resonance: float = Field(default=0.70, ge=0.0, le=1.0, description="Psychological harmony and archetype alignment")
    regret: float = Field(default=0.00, ge=0.0, le=1.0, description="Divergence consequence pain from original intention")
    destiny_shift: float = Field(default=0.00, ge=0.0, le=1.0, description="Cumulative deviation from root timeline baseline")
    world_stability: float = Field(default=0.85, ge=0.0, le=1.0, description="Environmental and institutional coherence")
    social_stability: float = Field(default=0.80, ge=0.0, le=1.0, description="Faction harmony and civil trust")
    technology_level: float = Field(default=0.50, ge=0.0, le=1.0, description="Technological sophistication level")

    def to_dict(self) -> Dict[str, float]:
        return {
            "entropy": round(self.entropy, 4),
            "resonance": round(self.resonance, 4),
            "regret": round(self.regret, 4),
            "destiny_shift": round(self.destiny_shift, 4),
            "world_stability": round(self.world_stability, 4),
            "social_stability": round(self.social_stability, 4),
            "technology_level": round(self.technology_level, 4)
        }

def clamp(val: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamps a floating point value to [min_val, max_val] with NaN safety."""
    if val is None or math.isnan(val) or math.isinf(val):
        return min_val
    return max(min_val, min(max_val, float(val)))

class StateEngine:
    """
    Authoritative state transition engine for KSHAN.
    Manages deterministic updates across the 7D multiverse state vector.
    """

    @staticmethod
    def clamp_vector(vector_dict: Dict[str, Any]) -> MultiverseStateVector:
        return MultiverseStateVector(
            entropy=clamp(vector_dict.get("entropy", 0.10)),
            resonance=clamp(vector_dict.get("resonance", 0.70)),
            regret=clamp(vector_dict.get("regret", 0.00)),
            destiny_shift=clamp(vector_dict.get("destiny_shift", 0.00)),
            world_stability=clamp(vector_dict.get("world_stability", 0.85)),
            social_stability=clamp(vector_dict.get("social_stability", 0.80)),
            technology_level=clamp(vector_dict.get("technology_level", 0.50))
        )

    def calculate_state_transition(
        self,
        current_state: MultiverseStateVector,
        entropy_delta: float,
        resonance_delta: float,
        regret_delta: float,
        destiny_shift_delta: float,
        world_stability_delta: float = 0.0,
        social_stability_delta: float = 0.0,
        technology_level_delta: float = 0.0
    ) -> MultiverseStateVector:
        """
        Computes new state vector by applying deterministic deltas with strict bounds.
        """
        return MultiverseStateVector(
            entropy=clamp(current_state.entropy + entropy_delta),
            resonance=clamp(current_state.resonance + resonance_delta),
            regret=clamp(current_state.regret + regret_delta),
            destiny_shift=clamp(current_state.destiny_shift + destiny_shift_delta),
            world_stability=clamp(current_state.world_stability + world_stability_delta),
            social_stability=clamp(current_state.social_stability + social_stability_delta),
            technology_level=clamp(current_state.technology_level + technology_level_delta)
        )

state_engine = StateEngine()
