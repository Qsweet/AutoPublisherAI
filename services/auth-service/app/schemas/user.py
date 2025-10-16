"""
User Pydantic Schemas

Request and response models for user operations.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID

from ..models.user import SubscriptionTier


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserPasswordUpdate(BaseModel):
    """Schema for password update."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    is_active: bool
    is_verified: bool
    subscription_tier: SubscriptionTier
    articles_count: int
    articles_limit: int
    remaining_articles: int
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class UserSubscriptionUpdate(BaseModel):
    """Schema for updating user subscription."""
    subscription_tier: SubscriptionTier


class UsageStats(BaseModel):
    """Schema for user usage statistics."""
    articles_count: int
    articles_limit: int
    remaining_articles: int
    subscription_tier: SubscriptionTier
    usage_percentage: float
    
    @classmethod
    def from_user(cls, user):
        """Create from user model."""
        usage_percentage = (user.articles_count / user.articles_limit * 100) if user.articles_limit > 0 else 0
        
        return cls(
            articles_count=user.articles_count,
            articles_limit=user.articles_limit,
            remaining_articles=user.remaining_articles,
            subscription_tier=user.subscription_tier,
            usage_percentage=round(usage_percentage, 2)
        )

