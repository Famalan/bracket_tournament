from typing import Any
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "E-Sport Symphony"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ALGORITHM: str = "HS256"
    
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "tournament_db"

    @property
    def DATABASE_URL(self) -> str:
        """Формируем URL для подключения к базе данных"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 