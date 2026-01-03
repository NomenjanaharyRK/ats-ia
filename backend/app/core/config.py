"""Configuration management using pydantic-settings."""
import secrets
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://ats_user:ats_pass@db:5432/ats"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    # Application
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS comma-separated string to list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    def validate_jwt_secret(self) -> None:
        """Validate JWT_SECRET is secure."""
        if self.JWT_SECRET == "CHANGE_ME_TO_RANDOM_32_CHARS_MINIMUM":
            raise ValueError(
                "JWT_SECRET must be changed from default value! "
                "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        if len(self.JWT_SECRET) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")


# Global settings instance
settings = Settings()

# Validate on import (fails fast in development)
if settings.ENVIRONMENT == "production":
    settings.validate_jwt_secret()
"""
Configuration centralisée de l'application via pydantic-settings.
Charge les variables d'environnement et valide les types.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600
    JWT_REFRESH_TOKEN_EXPIRE_SECONDS: int = 604800
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # App
    ENVIRONMENT: str = "development"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated origins"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instance globale
settings = Settings()
