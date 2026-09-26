from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Hospital Management System"
    API_V1_STR: str = "/api/v1"
    
    # Secrets - External configuration via .env
    SECRET_KEY: str = "CHANGE_THIS_TO_A_VERY_SECURE_RANDOM_SECRET_KEY_IN_PRODUCTION_32_BYTES"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "hms_user"
    POSTGRES_PASSWORD: str = "hms_password"
    POSTGRES_DB: str = "hms_db"
    POSTGRES_PORT: int = 5432

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
