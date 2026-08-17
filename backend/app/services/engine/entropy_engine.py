from typing import Dict, Any, Optional

class EntropyEngine:
    """
    Deterministic calculation engine for Multiverse Entropy.
    Entropy measures reality instability, chaos, and quantum divergence.
    Bounded strictly to [0.0, 1.0].
    """

    @staticmethod
    def calculate_entropy_delta(
        current_entropy: float,
        risk_level: str,
        choice_risk: float = 0.5,
        depth_level: int = 0
    ) -> float:
        """
        Calculate the delta change in entropy for a given choice.
        High risk and deep timeline nodes induce higher entropy swings.
        """
        risk_multiplier = {
            "low": 0.05,
            "moderate": 0.12,
            "high": 0.22,
            "critical": 0.35
        }.get(risk_level.lower(), 0.10)

        # Depth dampening or escalation
        depth_factor = min(1.5, 1.0 + (depth_level * 0.05))
        raw_delta = (choice_risk * risk_multiplier) * depth_factor

        # S-curve dampening as entropy approaches boundary 1.0
        if current_entropy > 0.8:
            raw_delta *= (1.0 - current_entropy) * 2.5

        return round(max(0.01, min(0.40, raw_delta)), 4)

    @staticmethod
    def apply_entropy(current_entropy: float, delta: float, stabilizer: bool = False) -> float:
        """Apply delta to current entropy, clamping within [0.0, 1.0]."""
        if stabilizer:
            new_val = current_entropy - delta
        else:
            new_val = current_entropy + delta
        return round(max(0.0, min(1.0, new_val)), 4)

entropy_engine = EntropyEngine()
