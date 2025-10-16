"""
Authentication Service

Business logic for user authentication and management.
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import uuid

from ..models.user import User, SubscriptionTier
from ..schemas.user import UserCreate, UserLogin, UserUpdate, UserPasswordUpdate
from ..core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)
from ..core.config import get_settings


settings = get_settings()


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize auth service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            subscription_tier=SubscriptionTier.FREE,
            articles_limit=5
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate_user(self, credentials: UserLogin) -> tuple[User, dict]:
        """
        Authenticate user and generate tokens.
        
        Args:
            credentials: Login credentials
            
        Returns:
            Tuple of (user, tokens)
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = await self.get_user_by_email(credentials.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        # Generate tokens
        tokens = self.generate_tokens(user)
        
        return user, tokens
    
    def generate_tokens(self, user: User) -> dict:
        """
        Generate access and refresh tokens for user.
        
        Args:
            user: User to generate tokens for
            
        Returns:
            Dictionary with tokens
        """
        token_data = {
            "sub": str(user.id),
            "email": user.email
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    async def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New tokens
            
        Raises:
            HTTPException: If token is invalid
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        
        if not payload or not verify_token_type(payload, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user_id = payload.get("sub")
        user = await self.get_user_by_id(uuid.UUID(user_id))
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        return self.generate_tokens(user)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User or None
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> User:
        """
        Update user profile.
        
        Args:
            user_id: User ID
            user_data: Update data
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found
        """
        user = await self.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.email is not None:
            # Check if new email already exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = user_data.email
            user.is_verified = False  # Require re-verification
        
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_password(
        self,
        user_id: uuid.UUID,
        password_data: UserPasswordUpdate
    ) -> User:
        """
        Update user password.
        
        Args:
            user_id: User ID
            password_data: Password update data
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If current password is incorrect
        """
        user = await self.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.hashed_password = hash_password(password_data.new_password)
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_subscription(
        self,
        user_id: uuid.UUID,
        tier: SubscriptionTier
    ) -> User:
        """
        Update user subscription tier.
        
        Args:
            user_id: User ID
            tier: New subscription tier
            
        Returns:
            Updated user
        """
        user = await self.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.update_subscription(tier)
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def verify_token(self, token: str) -> Optional[User]:
        """
        Verify access token and return user.
        
        Args:
            token: Access token
            
        Returns:
            User or None
        """
        payload = decode_token(token)
        
        if not payload or not verify_token_type(payload, "access"):
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return await self.get_user_by_id(uuid.UUID(user_id))

