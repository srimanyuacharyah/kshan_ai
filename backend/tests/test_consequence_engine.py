import pytest
from backend.app.services.engine import (
    entropy_engine,
    resonance_engine,
    regret_engine,
    consequence_engine
)

def test_entropy_engine_bounds_and_risk_scaling():
    """Verify entropy calculations scale with risk and stay strictly within [0.0, 1.0]."""
    delta_low = entropy_engine.calculate_entropy_delta(current_entropy=0.2, risk_level="low", choice_risk=0.2)
    delta_high = entropy_engine.calculate_entropy_delta(current_entropy=0.2, risk_level="critical", choice_risk=0.9)
    assert delta_high > delta_low

    # Boundary test near 1.0
    applied_high = entropy_engine.apply_entropy(current_entropy=0.95, delta=0.3)
    assert applied_high <= 1.0
    assert applied_high >= 0.95

    # Stabilizer test
    applied_stabilized = entropy_engine.apply_entropy(current_entropy=0.5, delta=0.2, stabilizer=True)
    assert applied_stabilized == 0.3

def test_resonance_engine_archetype_harmony():
    """Verify resonance engine awards harmonic bonus for matching archetype vectors."""
    delta_harmonic = resonance_engine.calculate_resonance_delta(
        current_resonance=0.5,
        choice_philosophical_vector="void leap shadow",
        profile_archetype="The Void Walker"
    )
    delta_dissonant = resonance_engine.calculate_resonance_delta(
        current_resonance=0.5,
        choice_philosophical_vector="corporate hierarchy bureaucratic compliance",
        profile_archetype="The Void Walker"
    )
    assert delta_harmonic > delta_dissonant

def test_regret_engine_divergence_magnitude():
    """Verify divergence magnitude scales with entropy shift and risk score."""
    mag_low = regret_engine.calculate_divergence_magnitude(entropy_delta=0.02, resonance_delta=0.01, risk_score=0.1)
    mag_high = regret_engine.calculate_divergence_magnitude(entropy_delta=0.35, resonance_delta=-0.20, risk_score=0.9)
    assert mag_high > mag_low
    assert 0.0 <= mag_low <= 1.0
    assert 0.0 <= mag_high <= 1.0

def test_authoritative_consequence_engine():
    """Verify the composite consequence engine computes deterministic state transitions."""
    transition = consequence_engine.process_decision_consequence(
        current_entropy=0.30,
        current_resonance=0.70,
        current_regret=0.10,
        risk_level="high",
        choice_risk=0.75,
        choice_philosophical_vector="quantum transcendence",
        profile_archetype="The Cosmic Seeker",
        depth_level=2
    )

    assert 0.0 <= transition.new_entropy <= 1.0
    assert 0.0 <= transition.new_resonance <= 1.0
    assert 0.0 <= transition.new_regret <= 1.0
    assert transition.divergence_magnitude > 0.0
    assert transition.destiny_shift in [
        "Harmonic Progression",
        "Noticeable Ripple",
        "Major Paradigm Divergence"
    ]
