from typing import Dict, Any, Optional

class ResonanceEngine:
    """
    Deterministic calculation engine for Multiverse Resonance.
    Resonance measures harmonic alignment with the voyager's core archetype and universe laws.
    Bounded strictly to [0.0, 1.0].
    """

    @staticmethod
    def calculate_resonance_delta(
        current_resonance: float,
        choice_philosophical_vector: Optional[str] = None,
        profile_archetype: Optional[str] = None,
        base_resonance: float = 0.5
    ) -> float:
        """
        Calculate resonance delta based on harmony between decision vector and user archetype.
        """
        # Baseline delta
        delta = (base_resonance - 0.5) * 0.2

        if choice_philosophical_vector and profile_archetype:
            vector_clean = choice_philosophical_vector.lower()
            archetype_clean = profile_archetype.lower()
            
            # Harmonic match bonus
            if any(w in archetype_clean for w in vector_clean.split()) or any(w in vector_clean for w in archetype_clean.split()):
                delta += 0.08
            else:
                delta -= 0.04

        return round(max(-0.25, min(0.25, delta)), 4)

    @staticmethod
    def apply_resonance(current_resonance: float, delta: float) -> float:
        """Apply delta to current resonance, clamping within [0.0, 1.0]."""
        new_val = current_resonance + delta
        return round(max(0.0, min(1.0, new_val)), 4)

resonance_engine = ResonanceEngine()
