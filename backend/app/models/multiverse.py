from sqlalchemy import Column, String, Text, Float, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from backend.app.models.base import Base, UUIDMixin, TimestampMixin

class RealityBranch(Base, UUIDMixin, TimestampMixin):
    """Represents a discrete parallel timeline / branch in the multiverse."""
    __tablename__ = "reality_branches"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    future_profile_id = Column(String(36), ForeignKey("future_profiles.id", ondelete="CASCADE"), index=True, nullable=True)
    parent_branch_id = Column(String(36), ForeignKey("reality_branches.id", ondelete="SET NULL"), index=True, nullable=True)
    fork_node_id = Column(String(36), nullable=True) # ID of the node where this fork happened
    
    branch_name = Column(String(200), nullable=False)
    branch_code = Column(String(50), index=True, nullable=False) # e.g. 'TL-A9-04'
    status = Column(String(50), default="active", nullable=False) # 'active', 'archived', 'collapsed', 'transcended'
    
    entropy_level = Column(Float, default=0.1, nullable=False) # 0.0 to 1.0 (Chaos/Uncertainty)
    resonance_score = Column(Float, default=0.5, nullable=False) # 0.0 to 1.0 (Psychological harmony)
    regret_index = Column(Float, default=0.0, nullable=False) # 0.0 to 1.0 (Divergence consequence pain)
    destiny_shift = Column(Float, default=0.0, nullable=False) # Total deviation from baseline
    
    branch_metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", back_populates="reality_branches")
    future_profile = relationship("FutureProfile", back_populates="reality_branches")
    parent_branch = relationship("RealityBranch", remote_side="RealityBranch.id", backref="child_branches")
    timeline_nodes = relationship("TimelineNode", back_populates="branch", cascade="all, delete-orphan")
    multiverse_state = relationship("MultiverseState", back_populates="branch", uselist=False, cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="branch", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="branch", cascade="all, delete-orphan")

class MultiverseState(Base, UUIDMixin, TimestampMixin):
    """Aggregate snapshot of world variables, faction states, and timeline health for a branch."""
    __tablename__ = "multiverse_states"

    branch_id = Column(String(36), ForeignKey("reality_branches.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    active_node_id = Column(String(36), nullable=True)
    total_nodes_count = Column(Integer, default=1, nullable=False)
    world_coherence = Column(Float, default=1.0, nullable=False)
    timeline_era = Column(String(100), default="Genesis Moment", nullable=False)
    state_variables = Column(JSON, default=dict, nullable=False) # Faction power, technology level, environmental state

    # Relationships
    branch = relationship("RealityBranch", back_populates="multiverse_state")
