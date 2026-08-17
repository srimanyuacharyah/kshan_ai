from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from backend.app.schemas.common import BaseSchema

class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=6, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int

class UserProfileResponse(BaseSchema):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    sound_enabled: bool = True
    preferences: Dict[str, Any] = {}

class UserResponse(BaseSchema):
    id: str
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    profile: Optional[UserProfileResponse] = None

class AuthResponse(BaseModel):
    user: UserResponse
    token: TokenResponse
