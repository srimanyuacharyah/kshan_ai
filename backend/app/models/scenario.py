from sqlalchemy import Column, String, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.models.base import Base, UUIDMixin, TimestampMixin

class Scenario(Base, UUIDMixin, TimestampMixin):
    """Preset or custom starting inflection moment ('Kshan') for multiverse divergence."""
    __tablename__ = "scenarios"

    title = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    genre = Column(String(50), index=True, nullable=False) # e.g. 'Cyber-Mythic', 'Quantum Sci-Fi', 'Magical Realism', 'Personal Crossroad'
    tagline = Column(String(255), nullable=False)
    premise = Column(Text, nullable=False)
    initial_kshan_moment = Column(Text, nullable=False)
    sensory_ambiance = Column(String(255), nullable=True) # Sound and visual cues
    cover_image_url = Column(String(500), nullable=True)
    is_curated = Column(Boolean, default=True, nullable=False)
    metadata_payload = Column(JSON, default=dict, nullable=False)

    # Relationships
    future_profiles = relationship("FutureProfile", back_populates="scenario")
    worlds = relationship("World", back_populates="scenario")

class FutureProfile(Base, UUIDMixin, TimestampMixin):
    """User-specific future trajectory and psychological archetype for a scenario."""
    __tablename__ = "future_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(36), ForeignKey("scenarios.id", ondelete="SET NULL"), index=True, nullable=True)
    title = Column(String(200), nullable=False)
    archetype = Column(String(100), nullable=False) # e.g. 'The Void Walker', 'The Celestial Architect', 'The Reluctant Rebel'
    philosophical_alignment = Column(String(100), nullable=True)
    psychological_traits = Column(JSON, default=dict, nullable=False) # Entropy Affinity, Resonance, Regret Index
    custom_seed_prompt = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="future_profiles")
    scenario = relationship("Scenario", back_populates="future_profiles")
    reality_branches = relationship("RealityBranch", back_populates="future_profile")
