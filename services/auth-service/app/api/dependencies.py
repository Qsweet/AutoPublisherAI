"""
API Dependencies

FastAPI dependencies for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..core.database import get_db
from ..services.auth_service import AuthService
from ..models.user import User


security = HTTPBearer()


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """
    Dependency to get auth service instance.
    
    Args:
        db: Database session
        
    Returns:
        AuthService instance
    """
    return AuthService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Dependency to get current authenticated user.
    
    Args:
        credentials: HTTP Bearer credentials
        auth_service: Auth service instance
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    user = await auth_service.verify_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current verified user.
    
    Args:
        current_user: Current user
        
    Returns:
        Current verified user
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    
    return current_user


def require_subscription(min_tier: str):
    """
    Dependency factory to require minimum subscription tier.
    
    Args:
        min_tier: Minimum subscription tier required
        
    Returns:
        Dependency function
    """
    tier_levels = {
        "free": 0,
        "basic": 1,
        "pro": 2,
        "enterprise": 3
    }
    
    min_level = tier_levels.get(min_tier.lower(), 0)
    
    async def check_subscription(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Check if user has required subscription tier."""
        user_level = tier_levels.get(current_user.subscription_tier.value, 0)
        
        if user_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {min_tier} subscription or higher"
            )
        
        return current_user
    
    return check_subscription

