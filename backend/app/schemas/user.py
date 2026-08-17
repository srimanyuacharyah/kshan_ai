from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.common import BaseSchema

class UserProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    sound_enabled: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)
