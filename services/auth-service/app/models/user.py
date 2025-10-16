"""
User Database Model

SQLAlchemy model for users table.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from ..core.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(Base):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Unique user identifier (UUID)
        email: User email (unique)
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        is_active: Whether user account is active
        is_verified: Whether email is verified
        subscription_tier: Current subscription level
        articles_count: Number of articles created
        articles_limit: Monthly article limit based on subscription
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Subscription
    subscription_tier = Column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    
    # Usage Tracking
    articles_count = Column(Integer, default=0, nullable=False)
    articles_limit = Column(Integer, default=5, nullable=False)  # Free tier default
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships (will be added when we create Article model)
    # articles = relationship("Article", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def can_create_article(self) -> bool:
        """Check if user can create more articles."""
        return self.articles_count < self.articles_limit
    
    @property
    def remaining_articles(self) -> int:
        """Get remaining article quota."""
        return max(0, self.articles_limit - self.articles_count)
    
    def increment_article_count(self):
        """Increment article count."""
        self.articles_count += 1
    
    def reset_article_count(self):
        """Reset monthly article count."""
        self.articles_count = 0
    
    def update_subscription(self, tier: SubscriptionTier):
        """Update subscription tier and limits."""
        self.subscription_tier = tier
        
        # Update limits based on tier
        tier_limits = {
            SubscriptionTier.FREE: 5,
            SubscriptionTier.BASIC: 50,
            SubscriptionTier.PRO: 200,
            SubscriptionTier.ENTERPRISE: 999999  # Unlimited
        }
        
        self.articles_limit = tier_limits.get(tier, 5)

