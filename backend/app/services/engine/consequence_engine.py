from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.services.engine.entropy_engine import entropy_engine
from backend.app.services.engine.resonance_engine import resonance_engine
from backend.app.services.engine.regret_engine import regret_engine

class MultiverseStateTransition(BaseModel):
    new_entropy: float = Field(..., ge=0.0, le=1.0)
    entropy_delta: float
    new_resonance: float = Field(..., ge=0.0, le=1.0)
    resonance_delta: float
    new_regret: float = Field(..., ge=0.0, le=1.0)
    regret_delta: float
    divergence_magnitude: float = Field(..., ge=0.0, le=1.0)
    destiny_shift: str

class ConsequenceEngine:
    """
    Primary authoritative state engine for KSHAN:
    Calculates deterministic mathematical state updates for multiverse branches,
    preventing LLM hallucination over numerical game state.
    """

    def process_decision_consequence(
        self,
        current_entropy: float,
        current_resonance: float,
        current_regret: float,
        risk_level: str,
        choice_risk: float = 0.5,
        choice_philosophical_vector: Optional[str] = None,
        profile_archetype: Optional[str] = None,
        consequence_severity: str = "moderate",
        depth_level: int = 0
    ) -> MultiverseStateTransition:
        """
        Calculates authoritative new multiverse state metrics following a player decision.
        """
        # 1. Entropy
        entropy_delta = entropy_engine.calculate_entropy_delta(
            current_entropy=current_entropy,
            risk_level=risk_level,
            choice_risk=choice_risk,
            depth_level=depth_level
        )
        new_entropy = entropy_engine.apply_entropy(current_entropy, entropy_delta)

        # 2. Resonance
        resonance_delta = resonance_engine.calculate_resonance_delta(
            current_resonance=current_resonance,
            choice_philosophical_vector=choice_philosophical_vector,
            profile_archetype=profile_archetype,
            base_resonance=1.0 - choice_risk
        )
        new_resonance = resonance_engine.apply_resonance(current_resonance, resonance_delta)

        # 3. Regret & Divergence
        regret_delta = regret_engine.calculate_regret_delta(
            current_regret=current_regret,
            consequence_severity=consequence_severity,
            risk_level=risk_level
        )
        new_regret = regret_engine.apply_regret(current_regret, regret_delta)

        divergence_mag = regret_engine.calculate_divergence_magnitude(
            entropy_delta=entropy_delta,
            resonance_delta=resonance_delta,
            risk_score=choice_risk
        )

        # 4. Destiny Shift qualitative tag
        if divergence_mag > 0.6:
            destiny_shift = "Major Paradigm Divergence"
        elif divergence_mag > 0.3:
            destiny_shift = "Noticeable Ripple"
        else:
            destiny_shift = "Harmonic Progression"

        return MultiverseStateTransition(
            new_entropy=new_entropy,
            entropy_delta=entropy_delta,
            new_resonance=new_resonance,
            resonance_delta=resonance_delta,
            new_regret=new_regret,
            regret_delta=regret_delta,
            divergence_magnitude=divergence_mag,
            destiny_shift=destiny_shift
        )

consequence_engine = ConsequenceEngine()
