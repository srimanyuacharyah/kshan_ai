from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token
)
from backend.app.models.user import User, UserProfile
from backend.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    TokenResponse,
    UserResponse
)
from backend.app.schemas.user import UserProfileUpdateRequest
from backend.app.schemas.common import StandardResponse
from backend.app.api.deps import get_current_active_user
from backend.app.core.logging import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=StandardResponse[AuthResponse], status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account with isolated tenant identity and initial profile."""
    # Check existing email
    email_query = select(User).where(User.email == request.email.lower())
    result = await db.execute(email_query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists"
        )
        
    # Check existing username
    username_query = select(User).where(User.username == request.username)
    result = await db.execute(username_query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken"
        )
        
    # Create User
    new_user = User(
        email=request.email.lower(),
        username=request.username,
        hashed_password=get_password_hash(request.password),
        is_active=True,
        is_superuser=False
    )
    db.add(new_user)
    await db.flush() # Populate new_user.id
    
    # Create Profile
    new_profile = UserProfile(
        user_id=new_user.id,
        display_name=request.display_name or request.username,
        bio="Voyager of alternate realities",
        sound_enabled=True,
        preferences={"theme": "obsidian", "ambient_audio": True}
    )
    db.add(new_profile)
    await db.commit()
    
    # Reload with profile
    query = select(User).where(User.id == new_user.id).options(selectinload(User.profile))
    result = await db.execute(query)
    user_record = result.scalar_one()
    
    token = create_access_token(user_record.id)
    
    logger.info(f"New user registered: {user_record.username} ({user_record.id})")
    
    return StandardResponse(
        message="Registration successful. Welcome to KSHAN.",
        data=AuthResponse(
            user=UserResponse.model_validate(user_record),
            token=TokenResponse(
                access_token=token,
                expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
    )

@router.post("/login", response_model=StandardResponse[AuthResponse])
async def login_user(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate with email and password to receive a Bearer JWT."""
    query = select(User).where(User.email == request.email.lower()).options(selectinload(User.profile))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
        
    token = create_access_token(user.id)
    
    logger.info(f"User logged in: {user.username} ({user.id})")
    
    return StandardResponse(
        message="Login successful",
        data=AuthResponse(
            user=UserResponse.model_validate(user),
            token=TokenResponse(
                access_token=token,
                expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
    )

@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Return the authenticated user profile and settings."""
    return StandardResponse(
        message="User profile retrieved",
        data=UserResponse.model_validate(current_user)
    )

@router.put("/me/profile", response_model=StandardResponse[UserResponse])
async def update_profile(
    request: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user display preferences and bio."""
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        
    if request.display_name is not None:
        profile.display_name = request.display_name
    if request.bio is not None:
        profile.bio = request.bio
    if request.avatar_url is not None:
        profile.avatar_url = request.avatar_url
    if request.sound_enabled is not None:
        profile.sound_enabled = request.sound_enabled
    if request.preferences is not None:
        profile.preferences = request.preferences
        
    await db.commit()
    
    # Reload
    query = select(User).where(User.id == current_user.id).options(selectinload(User.profile))
    result = await db.execute(query)
    refreshed_user = result.scalar_one()
    
    return StandardResponse(
        message="Profile updated successfully",
        data=UserResponse.model_validate(refreshed_user)
    )
