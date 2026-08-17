from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.models.base import Base, UUIDMixin, TimestampMixin

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    future_profiles = relationship("FutureProfile", back_populates="user", cascade="all, delete-orphan")
    reality_branches = relationship("RealityBranch", back_populates="user", cascade="all, delete-orphan")
    timeline_nodes = relationship("TimelineNode", back_populates="user", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    embeddings = relationship("EmbeddingRecord", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=True)
    bio = Column(String(500), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    sound_enabled = Column(Boolean, default=True, nullable=False)
    preferences = Column(JSON, default=dict, nullable=False)

    user = relationship("User", back_populates="profile")
