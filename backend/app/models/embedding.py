from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from backend.app.models.base import Base, UUIDMixin, TimestampMixin
from backend.app.core.config import settings

class EmbeddingRecord(Base, UUIDMixin, TimestampMixin):
    """Vector embedding record stored with pgvector for semantic RAG retrieval."""
    __tablename__ = "embeddings"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    branch_id = Column(String(36), ForeignKey("reality_branches.id", ondelete="CASCADE"), index=True, nullable=True)
    
    entity_type = Column(String(50), index=True, nullable=False) # 'timeline_node', 'memory', 'decision', 'world', 'character'
    entity_id = Column(String(36), index=True, nullable=False)
    
    document_content = Column(Text, nullable=False)
    document_title = Column(String(255), nullable=True)
    metadata_payload = Column(JSON, default=dict, nullable=False)
    
    # Vector column using configurable dimension from settings
    embedding_vector = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)

    # Relationships
    user = relationship("User", back_populates="embeddings")
