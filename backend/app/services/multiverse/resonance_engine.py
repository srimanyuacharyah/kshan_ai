from typing import Optional
from backend.app.services.multiverse.state_engine import clamp

class MultiverseResonanceEngine:
    """
    Calculates psychological and archetype alignment (Resonance) between
    the traveler's choice and the world/character frequency.
    """

    ARCHETYPE_AFFINITIES = {
        ("Defiance", "Rebel"): 0.20,
        ("Defiance", "Innovator"): 0.15,
        ("Submission", "Guardian"): 0.15,
        ("Submission", "Scholar"): 0.10,
        ("Transcendence", "Mystic"): 0.25,
        ("Transcendence", "Philosopher"): 0.20,
        ("Harmony", "Empath"): 0.20,
        ("Pragmatism", "Survivor"): 0.18
    }

    def calculate_resonance_delta(
        self,
        current_resonance: float,
        choice_philosophical_vector: Optional[str] = None,
        profile_archetype: Optional[str] = None,
        choice_risk: float = 0.5,
        character_alignment_bonus: float = 0.0
    ) -> float:
        """
        Formula:
        ΔRes = ArchetypeAffinity + CharacterAlignmentBonus - (choice_risk * 0.15)
        """
        affinity = 0.05
        if choice_philosophical_vector and profile_archetype:
            key = (choice_philosophical_vector, profile_archetype)
            affinity = self.ARCHETYPE_AFFINITIES.get(key, 0.08)

        risk_penalty = clamp(choice_risk) * 0.12
        raw_delta = affinity + clamp(character_alignment_bonus) - risk_penalty

        # If current resonance is low, positive alignment provides a rebound bonus
        if current_resonance < 0.3 and raw_delta > 0:
            raw_delta *= 1.3

        return round(raw_delta, 4)

    def apply_resonance(self, current_resonance: float, delta: float) -> float:
        return clamp(current_resonance + delta)

resonance_engine = MultiverseResonanceEngine()
