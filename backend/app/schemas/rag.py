from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from backend.app.schemas.common import BaseSchema

class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language inquiry")
    scenario_id: Optional[str] = Field(None, description="Optional scenario scope")
    branch_id: Optional[str] = Field(None, description="Optional reality branch scope")
    entity_types: Optional[List[str]] = Field(None, description="Filter by entity types (e.g. 'memory', 'timeline_node', 'character')")
    top_k: int = Field(default=6, ge=1, le=20, description="Maximum number of retrieved grounded chunks")
    similarity_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum cosine similarity score")

class RetrievalResultItem(BaseSchema):
    content: str
    score: float
    document_type: str
    entity_id: str
    document_title: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RAGSearchResponse(BaseSchema):
    query: str
    results_count: int
    results: List[RetrievalResultItem]
    context: str
    retrieval_time_ms: float
