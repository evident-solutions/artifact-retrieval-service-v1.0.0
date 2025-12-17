"""
Application configuration using environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GitLab configuration
    gitlab_base_url: str = "https://gitlab.com"
    gitlab_access_token: str = ""  # Required at runtime, but allow empty for testing

    # Application configuration
    app_name: str = "Artifact Retrieval Service"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    download_directory: str = "./downloads"  # Directory where artifacts are downloaded

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()
