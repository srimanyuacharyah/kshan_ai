from typing import Dict, Any, Optional

class RegretEngine:
    """
    Deterministic calculation engine for Multiverse Regret & Divergence Magnitude.
    Measures psychological and timeline deviation tension from the unchosen branches.
    Bounded to [0.0, 1.0].
    """

    @staticmethod
    def calculate_regret_delta(
        current_regret: float,
        consequence_severity: str = "minor",
        risk_level: str = "moderate",
        past_failures_count: int = 0
    ) -> float:
        """
        Calculate delta change in regret index following a turning point decision.
        """
        severity_mult = {
            "minor": 0.02,
            "moderate": 0.06,
            "severe": 0.14,
            "catastrophic": 0.25
        }.get(consequence_severity.lower(), 0.05)

        risk_add = 0.05 if risk_level.lower() in ["high", "critical"] else 0.0
        past_weight = min(0.10, past_failures_count * 0.02)

        delta = severity_mult + risk_add + past_weight
        return round(max(0.0, min(0.35, delta)), 4)

    @staticmethod
    def calculate_divergence_magnitude(
        entropy_delta: float,
        resonance_delta: float,
        risk_score: float
    ) -> float:
        """Calculate the scalar magnitude (0.0 - 1.0) of timeline divergence."""
        mag = (abs(entropy_delta) * 0.4) + (abs(resonance_delta) * 0.3) + (risk_score * 0.3)
        return round(max(0.05, min(1.0, mag)), 4)

    @staticmethod
    def apply_regret(current_regret: float, delta: float) -> float:
        """Apply delta to current regret index within [0.0, 1.0]."""
        new_val = current_regret + delta
        return round(max(0.0, min(1.0, new_val)), 4)

regret_engine = RegretEngine()
