from sqlalchemy import Column, String, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.app.models.base import Base, UUIDMixin, TimestampMixin

class Memory(Base, UUIDMixin, TimestampMixin):
    """Pivotal realization, flashback, or memory shard unlocked by choices."""
    __tablename__ = "memories"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    branch_id = Column(String(36), ForeignKey("reality_branches.id", ondelete="CASCADE"), index=True, nullable=False)
    node_id = Column(String(36), ForeignKey("timeline_nodes.id", ondelete="SET NULL"), index=True, nullable=True)

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    emotional_tone = Column(String(50), default="nostalgic", nullable=False) # 'grief', 'epiphany', 'triumph', 'dread'
    memory_type = Column(String(50), default="event", nullable=False) # 'origin', 'echo', 'epiphany', 'regret'
    clarity_level = Column(Float, default=1.0, nullable=False) # 0.0 (Faded) to 1.0 (Vivid)
    memory_metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", back_populates="memories")
    branch = relationship("RealityBranch", back_populates="memories")
    node = relationship("TimelineNode", back_populates="memories")
    media_items = relationship("MediaItem", back_populates="memory", cascade="all, delete-orphan")

class MediaItem(Base, UUIDMixin, TimestampMixin):
    """Visual or auditory artifacts linked to memories or events."""
    __tablename__ = "media_items"

    memory_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), index=True, nullable=False)
    media_type = Column(String(50), default="image", nullable=False) # 'image', 'audio_cue', 'ambient_loop'
    media_url = Column(String(500), nullable=False)
    caption = Column(String(255), nullable=True)
    generated_prompt = Column(Text, nullable=True)

    # Relationships
    memory = relationship("Memory", back_populates="media_items")
