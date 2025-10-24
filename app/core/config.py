"""Core configuration using Pydantic settings."""
from functools import lru_cache
from typing import List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    app_name: str = Field(default="Data Analyst Backend", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    dev_mode: Literal["dev", "prod"] = Field(default="prod", alias="DEV_MODE")

    # AWS Bedrock Configuration
    aws_region: str = Field(..., alias="AWS_REGION")
    aws_access_key_id: str = Field(..., alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., alias="AWS_SECRET_ACCESS_KEY")
    aws_session_token: str | None = Field(default=None, alias="AWS_SESSION_TOKEN")

    # File Upload Limits
    max_file_size_mb: int = Field(default=25, alias="MAX_FILE_SIZE_MB")

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173", alias="ALLOWED_ORIGINS"
    )

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated origins."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
