"""
Configuration Management

This module handles all configuration settings using Pydantic Settings.
All sensitive data is loaded from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This uses Pydantic Settings for type validation and automatic
    loading from .env files.
    """
    
    # ==============================================
    # Application Settings
    # ==============================================
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SERVICE_NAME: str = "content-service"
    
    # ==============================================
    # OpenAI Configuration
    # ==============================================
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_IMAGE_MODEL: str = "dall-e-3"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.7
    
    # ==============================================
    # Content Generation Settings
    # ==============================================
    DEFAULT_ARTICLE_LENGTH: int = 1500
    DEFAULT_LANGUAGE: str = "ar"
    SEO_OPTIMIZATION_LEVEL: str = "high"
    MAX_KEYWORDS: int = 10
    INCLUDE_IMAGES: bool = True
    
    # ==============================================
    # Database Configuration
    # ==============================================
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
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
    # API Rate Limiting
    # ==============================================
    RATE_LIMIT_PER_MINUTE: int = 60
    
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


# Validation on import
if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
    import warnings
    warnings.warn(
        "⚠️  OPENAI_API_KEY is not properly configured. "
        "Please set it in your .env file.",
        UserWarning
    )

