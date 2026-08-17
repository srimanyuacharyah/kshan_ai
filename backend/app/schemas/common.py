from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

T = TypeVar("T")

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class StandardResponse(BaseSchema, Generic[T]):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None
    meta: Optional[dict] = None

class PaginatedResponse(BaseSchema, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    has_more: bool
