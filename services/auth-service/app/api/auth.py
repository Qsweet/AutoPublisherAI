"""
Authentication API Endpoints

Routes for user authentication and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..services.auth_service import AuthService
from ..schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    TokenRefresh,
    UserUpdate,
    UserPasswordUpdate,
    UserSubscriptionUpdate,
    UsageStats
)
from ..models.user import User
from .dependencies import get_auth_service, get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        auth_service: Auth service instance
        
    Returns:
        Created user
    """
    user = await auth_service.register_user(user_data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login and get access tokens.
    
    Args:
        credentials: Login credentials
        auth_service: Auth service instance
        
    Returns:
        Access and refresh tokens
    """
    user, tokens = await auth_service.authenticate_user(credentials)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token.
    
    Args:
        token_data: Refresh token
        auth_service: Auth service instance
        
    Returns:
        New access and refresh tokens
    """
    tokens = await auth_service.refresh_access_token(token_data.refresh_token)
    return TokenResponse(**tokens)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update current user profile.
    
    Args:
        user_data: Update data
        current_user: Current authenticated user
        auth_service: Auth service instance
        
    Returns:
        Updated user
    """
    user = await auth_service.update_user(current_user.id, user_data)
    return UserResponse.model_validate(user)


@router.put("/me/password")
async def update_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update current user password.
    
    Args:
        password_data: Password update data
        current_user: Current authenticated user
        auth_service: Auth service instance
        
    Returns:
        Success message
    """
    await auth_service.update_password(current_user.id, password_data)
    return {"message": "Password updated successfully"}


@router.get("/me/usage", response_model=UsageStats)
async def get_usage_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user usage statistics.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Usage statistics
    """
    return UsageStats.from_user(current_user)


@router.put("/me/subscription", response_model=UserResponse)
async def update_subscription(
    subscription_data: UserSubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update user subscription tier.
    
    Note: In production, this should be called by payment webhook, not directly by user.
    
    Args:
        subscription_data: Subscription update data
        current_user: Current authenticated user
        auth_service: Auth service instance
        
    Returns:
        Updated user
    """
    user = await auth_service.update_subscription(
        current_user.id,
        subscription_data.subscription_tier
    )
    return UserResponse.model_validate(user)

