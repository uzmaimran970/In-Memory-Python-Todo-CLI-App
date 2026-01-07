"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be configured via .env file or environment variables.
    """

    # Database
    database_url: str

    # Authentication
    better_auth_secret: str
    jwt_algorithm: str = "HS256"
    jwt_audience: str = "http://localhost:3000"
    jwt_issuer: str = "better-auth"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
