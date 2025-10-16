"""
Auth Service Configuration

Configuration management using Pydantic Settings.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # ==============================================
    # Application Settings
    # ==============================================
    APP_NAME: str = "AutoPublisher Auth Service"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
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
        """Construct async database URL."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # ==============================================
    # Redis Configuration
    # ==============================================
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    # ==============================================
    # JWT Configuration
    # ==============================================
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ==============================================
    # Security
    # ==============================================
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = False
    
    # ==============================================
    # Email Configuration (Optional)
    # ==============================================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: Optional[str] = "AutoPublisher"
    
    # ==============================================
    # CORS
    # ==============================================
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]
    
    # ==============================================
    # API Configuration
    # ==============================================
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings instance
    """
    return Settings()

