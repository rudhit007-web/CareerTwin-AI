"""
CareerTwin AI – Application Configuration
Loads settings from environment variables with sensible defaults.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "CareerTwin AI"
    app_env: str = "development"
    secret_key: str = Field(default="change-me-in-production-use-openssl-rand-hex-32")
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Database
    database_url: str = "sqlite+aiosqlite:///./database/careertwin.db"

    # IBM watsonx.ai
    watsonx_api_key: str = ""
    watsonx_project_id: str = ""
    watsonx_url: str = "https://au-syd.ml.cloud.ibm.com"
    watsonx_model_id: str = "meta-llama/llama-3-3-70b-instruct"

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # File Upload
    max_upload_size_mb: int = 10
    upload_folder: str = "uploads"
    allowed_file_types: list[str] = [
        "application/pdf",
        "text/plain",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
