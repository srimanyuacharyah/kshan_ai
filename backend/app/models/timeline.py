from sqlalchemy import Column, String, Text, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.models.base import Base, UUIDMixin, TimestampMixin

class TimelineNode(Base, UUIDMixin, TimestampMixin):
    """An individual event / moment in a reality branch."""
    __tablename__ = "timeline_nodes"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    branch_id = Column(String(36), ForeignKey("reality_branches.id", ondelete="CASCADE"), index=True, nullable=False)
    parent_node_id = Column(String(36), ForeignKey("timeline_nodes.id", ondelete="SET NULL"), index=True, nullable=True)
    
    depth_level = Column(Integer, default=0, nullable=False) # 0 = Origin Kshan, 1 = First Choice, etc.
    era_year = Column(String(50), default="Year 0", nullable=False) # e.g. "Year 2042", "Cycle IX"
    
    story_text = Column(Text, nullable=False)
    sensory_cue = Column(String(255), nullable=True) # e.g. "Smell of ozone; distant temple bells"
    audio_ambiance = Column(String(100), default="cosmic_drone", nullable=False)
    
    entropy_delta = Column(Float, default=0.0, nullable=False)
    resonance_delta = Column(Float, default=0.0, nullable=False)
    regret_delta = Column(Float, default=0.0, nullable=False)
    butterfly_impact = Column(String(255), nullable=True) # Summary of causal ripple
    
    node_metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", back_populates="timeline_nodes")
    branch = relationship("RealityBranch", back_populates="timeline_nodes")
    parent_node = relationship("TimelineNode", remote_side="TimelineNode.id", backref="child_nodes")
    choices = relationship("Choice", back_populates="node", cascade="all, delete-orphan")
    decision = relationship("Decision", back_populates="node", uselist=False, cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="node", cascade="all, delete-orphan")

class Choice(Base, UUIDMixin, TimestampMixin):
    """Available branching action offered to the player at a timeline node."""
    __tablename__ = "choices"

    node_id = Column(String(36), ForeignKey("timeline_nodes.id", ondelete="CASCADE"), index=True, nullable=False)
    choice_label = Column(String(255), nullable=False)
    choice_description = Column(Text, nullable=False)
    risk_level = Column(String(50), default="moderate", nullable=False) # 'low', 'moderate', 'high', 'existential'
    philosophical_vector = Column(String(100), nullable=True) # e.g. 'Defiance', 'Submission', 'Transcendence'
    order_index = Column(Integer, default=0, nullable=False)

    # Relationships
    node = relationship("TimelineNode", back_populates="choices")
    consequence = relationship("Consequence", back_populates="choice", uselist=False, cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="chosen_choice")

class Consequence(Base, UUIDMixin, TimestampMixin):
    """Projected and actual causal repercussions of a choice."""
    __tablename__ = "consequences"

    choice_id = Column(String(36), ForeignKey("choices.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    predicted_outcome = Column(Text, nullable=False)
    expected_entropy_shift = Column(Float, default=0.0, nullable=False)
    expected_resonance_shift = Column(Float, default=0.0, nullable=False)
    expected_regret_shift = Column(Float, default=0.0, nullable=False)
    world_effect_summary = Column(String(255), nullable=True)

    # Relationships
    choice = relationship("Choice", back_populates="consequence")

class Decision(Base, UUIDMixin, TimestampMixin):
    """Immutable record of the choice executed by the user at a timeline node."""
    __tablename__ = "decisions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    node_id = Column(String(36), ForeignKey("timeline_nodes.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    chosen_choice_id = Column(String(36), ForeignKey("choices.id", ondelete="CASCADE"), index=True, nullable=False)
    
    rationale = Column(Text, nullable=True)
    divergence_magnitude = Column(Float, default=0.1, nullable=False)
    decision_metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", back_populates="decisions")
    node = relationship("TimelineNode", back_populates="decision")
    chosen_choice = relationship("Choice", back_populates="decisions")
