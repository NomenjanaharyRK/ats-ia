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
