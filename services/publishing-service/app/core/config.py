"""
Configuration Management for Publishing Service

Handles all configuration settings for various publishing platforms.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings for the publishing service.
    """
    
    # ==============================================
    # Application Settings
    # ==============================================
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SERVICE_NAME: str = "publishing-service"
    
    # ==============================================
    # WordPress Configuration
    # ==============================================
    WORDPRESS_URL: Optional[str] = None
    WORDPRESS_USERNAME: Optional[str] = None
    WORDPRESS_APP_PASSWORD: Optional[str] = None
    
    @property
    def wordpress_configured(self) -> bool:
        """Check if WordPress is properly configured."""
        return all([
            self.WORDPRESS_URL,
            self.WORDPRESS_USERNAME,
            self.WORDPRESS_APP_PASSWORD
        ])
    
    # ==============================================
    # Instagram Configuration
    # ==============================================
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    INSTAGRAM_BUSINESS_ACCOUNT_ID: Optional[str] = None
    
    @property
    def instagram_configured(self) -> bool:
        """Check if Instagram is properly configured."""
        return all([
            self.INSTAGRAM_ACCESS_TOKEN,
            self.INSTAGRAM_BUSINESS_ACCOUNT_ID
        ])
    
    # ==============================================
    # Facebook Configuration (for future use)
    # ==============================================
    FACEBOOK_PAGE_ID: Optional[str] = None
    FACEBOOK_ACCESS_TOKEN: Optional[str] = None
    
    @property
    def facebook_configured(self) -> bool:
        """Check if Facebook is properly configured."""
        return all([
            self.FACEBOOK_PAGE_ID,
            self.FACEBOOK_ACCESS_TOKEN
        ])
    
    # ==============================================
    # X (Twitter) Configuration (for future use)
    # ==============================================
    X_API_KEY: Optional[str] = None
    X_API_SECRET: Optional[str] = None
    X_ACCESS_TOKEN: Optional[str] = None
    X_ACCESS_TOKEN_SECRET: Optional[str] = None
    
    @property
    def x_configured(self) -> bool:
        """Check if X (Twitter) is properly configured."""
        return all([
            self.X_API_KEY,
            self.X_API_SECRET,
            self.X_ACCESS_TOKEN,
            self.X_ACCESS_TOKEN_SECRET
        ])
    
    # ==============================================
    # Database Configuration
    # ==============================================
    POSTGRES_USER: str = "autopublisher"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "autopublisher_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # ==============================================
    # Redis Configuration
    # ==============================================
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None
    
    @property
    def REDIS_CONNECTION_URL(self) -> str:
        """Get Redis connection URL."""
        return self.REDIS_URL or f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    # ==============================================
    # Publishing Settings
    # ==============================================
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY_SECONDS: int = 5
    
    # ==============================================
    # Pydantic Settings Configuration
    # ==============================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Create global settings instance
settings = Settings()

