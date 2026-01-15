"""Configuration settings for the Swig GM Dashboard API."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    duckdb_path: str = str(Path(__file__).parent.parent.parent.parent / "swig_operations.duckdb")

    # Anthropic API
    anthropic_api_key: str = ""

    # API Settings
    api_prefix: str = "/api"
    debug: bool = True

    # The "current" date in the synthetic data (last day of generated data)
    data_current_date: str = "2025-01-26"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
