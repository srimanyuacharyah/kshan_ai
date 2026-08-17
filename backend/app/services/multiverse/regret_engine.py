from typing import Optional
from backend.app.services.multiverse.state_engine import clamp

class MultiverseRegretEngine:
    """
    Calculates psychological regret resulting from unintended divergences,
    betrayals, or severity of consequences relative to the traveler's stated intention.
    """

    SEVERITY_FACTORS = {
        "minor": 0.04,
        "moderate": 0.10,
        "severe": 0.22,
        "catastrophic": 0.38
    }

    def calculate_regret_delta(
        self,
        current_regret: float,
        consequence_severity: str = "moderate",
        risk_level: str = "moderate",
        intention_alignment: float = 0.5, # 1.0 = perfect match, 0.0 = total contradiction
        character_loss_factor: float = 0.0
    ) -> float:
        """
        Formula:
        ΔR = (severity_factor * 0.4) + (risk_penalty * 0.2) + ((1.0 - intention_alignment) * 0.25) + (character_loss * 0.2)
        """
        sev = self.SEVERITY_FACTORS.get(consequence_severity.lower(), 0.10)
        risk_mod = 0.05 if risk_level == "low" else (0.10 if risk_level == "moderate" else 0.18)
        intention_gap = (1.0 - clamp(intention_alignment)) * 0.25
        loss_mod = clamp(character_loss_factor) * 0.20

        raw_delta = (sev * 0.4) + (risk_mod * 0.2) + intention_gap + loss_mod
        return round(raw_delta, 4)

    def apply_regret(self, current_regret: float, delta: float) -> float:
        return clamp(current_regret + delta)

class MultiverseDestinyEngine:
    """
    Calculates cumulative deviation of a branch from the root reality trajectory.
    """

    def calculate_destiny_shift_delta(
        self,
        divergence_magnitude: float,
        entropy_delta: float,
        is_major_decision: bool = False,
        depth_level: int = 1
    ) -> float:
        """
        Formula:
        ΔDestiny = (divergence_mag * 0.15) + (abs(entropy_delta) * 0.10) + (0.10 if major else 0.02)
        """
        major_bonus = 0.10 if is_major_decision else 0.02
        delta = (clamp(divergence_magnitude) * 0.15) + (abs(entropy_delta) * 0.10) + major_bonus
        return round(delta, 4)

    def apply_destiny_shift(self, current_shift: float, delta: float) -> float:
        return clamp(current_shift + delta)

regret_engine = MultiverseRegretEngine()
destiny_engine = MultiverseDestinyEngine()
