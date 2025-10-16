"""
Configuration Management for Orchestrator Service

Central configuration for the orchestrator that coordinates all services.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings for the orchestrator service.
    """
    
    # ==============================================
    # Application Settings
    # ==============================================
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SERVICE_NAME: str = "orchestrator-service"
    
    # ==============================================
    # Service URLs
    # ==============================================
    CONTENT_SERVICE_URL: str = "http://content-service:8000"
    PUBLISHING_SERVICE_URL: str = "http://publishing-service:8000"
    
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
    # Celery Configuration
    # ==============================================
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    @property
    def CELERY_BROKER(self) -> str:
        """Get Celery broker URL."""
        return self.CELERY_BROKER_URL or self.REDIS_CONNECTION_URL
    
    @property
    def CELERY_BACKEND(self) -> str:
        """Get Celery result backend URL."""
        return self.CELERY_RESULT_BACKEND or self.REDIS_CONNECTION_URL
    
    # ==============================================
    # Task Settings
    # ==============================================
    MAX_CONCURRENT_TASKS: int = 10
    TASK_TIMEOUT_SECONDS: int = 600  # 10 minutes
    
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

