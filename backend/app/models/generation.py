import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from backend.app.models.base import Base

class GenerationHistory(Base):
    """
    Persistent audit trail and observability record of AI generations.
    Stores metadata, model name, prompt versions, latency, and context metrics without logging secrets.
    """
    __tablename__ = "generation_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id = Column(String(36), ForeignKey("scenarios.id", ondelete="SET NULL"), nullable=True, index=True)
    branch_id = Column(String(36), ForeignKey("reality_branches.id", ondelete="SET NULL"), nullable=True, index=True)
    
    generation_type = Column(String(64), nullable=False, index=True) # e.g. "story", "branch", "future_you", "world", "character", "decision_analysis"
    model = Column(String(128), nullable=False)
    prompt_version = Column(String(64), nullable=False)
    input_context_hash = Column(String(64), nullable=True)
    
    latency_ms = Column(Float, nullable=False, default=0.0)
    rag_retrievals_count = Column(Float, nullable=False, default=0)
    mcp_tools_invoked = Column(JSON, nullable=False, default=list) # List of tool names called
    status = Column(String(32), nullable=False, default="success") # "success", "failed", "retried"
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index("ix_generation_history_user_type", "user_id", "generation_type"),
        Index("ix_generation_history_created", "created_at"),
    )
