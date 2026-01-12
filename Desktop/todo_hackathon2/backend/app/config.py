"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # CORS - comma-separated string
    cors_origins: str = "http://localhost:3000"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    def get_cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string or JSON array."""
        import json
        value = self.cors_origins.strip()
        # Try JSON array first
        if value.startswith("["):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        # Fall back to comma-separated
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
