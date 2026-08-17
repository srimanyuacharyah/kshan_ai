from typing import Optional
from backend.app.services.multiverse.state_engine import clamp

class MultiverseEntropyEngine:
    """
    Calculates deterministic entropy shifts based on choice risk,
    branch depth, contradictory choices, and world disruption.
    """

    RISK_WEIGHTS = {
        "low": 0.05,
        "moderate": 0.12,
        "high": 0.22,
        "existential": 0.35
    }

    def calculate_entropy_delta(
        self,
        current_entropy: float,
        risk_level: str = "moderate",
        choice_risk: float = 0.5,
        depth_level: int = 0,
        contradiction_factor: float = 0.0,
        world_disruption: float = 0.0
    ) -> float:
        """
        Formula:
        ΔS = (risk_weight * 0.5 + choice_risk * 0.3) + (depth * 0.015) + (contradiction * 0.12) + (disruption * 0.15)
        Damped if current entropy is approaching upper asymptote (1.0).
        """
        base_risk = self.RISK_WEIGHTS.get(risk_level.lower(), 0.12)
        risk_component = (base_risk * 0.5) + (clamp(choice_risk) * 0.3)
        depth_component = min(0.15, depth_level * 0.015)
        contradiction_component = clamp(contradiction_factor) * 0.12
        disruption_component = clamp(world_disruption) * 0.15

        raw_delta = risk_component + depth_component + contradiction_component + disruption_component

        # Apply damping near saturation: when S is high, increases are harder to push higher
        saturation_damping = max(0.2, 1.0 - current_entropy)
        delta = raw_delta * saturation_damping
        return round(delta, 4)

    def apply_entropy(self, current_entropy: float, delta: float) -> float:
        return clamp(current_entropy + delta)

entropy_engine = MultiverseEntropyEngine()
