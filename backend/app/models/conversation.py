from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.models.base import Base, UUIDMixin, TimestampMixin

class Conversation(Base, UUIDMixin, TimestampMixin):
    """Dialogue session with 'Future You' or parallel timeline counterparts."""
    __tablename__ = "conversations"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    branch_id = Column(String(36), ForeignKey("reality_branches.id", ondelete="CASCADE"), index=True, nullable=False)
    persona_title = Column(String(150), default="Future You", nullable=False)
    timeline_context_summary = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="conversations")
    branch = relationship("RealityBranch", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ConversationMessage.created_at")

class ConversationMessage(Base, UUIDMixin, TimestampMixin):
    """Individual message in a Future You conversation."""
    __tablename__ = "conversation_messages"

    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    sender_role = Column(String(50), nullable=False) # 'user', 'future_you', 'system_narrator'
    content = Column(Text, nullable=False)
    grounding_sources = Column(JSON, default=list, nullable=False) # Cited memories, decisions, nodes from RAG

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
