"""Configuration settings for the Swig GM Dashboard API."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # PostgreSQL (Cloud SQL)
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:swig-postgres-2026@34.74.169.146:5432/swig"
    )

    # LLM Configuration
    # Options: "gpt-4o", "gpt-4o-mini", "claude-sonnet-4", "claude-sonnet-4-20250514"
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o")
    
    # OpenAI API Key (for gpt-* models)
    openai_api_key: str = ""

    # GCP settings for Claude via Vertex AI (for claude-* models)
    gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "prj-cts-lab-vertex-sandbox")
    gcp_region: str = os.getenv("GCP_REGION", "us-east5")  # Claude on Vertex requires us-east5

    # AWS Bedrock settings (fallback if no OpenAI key)
    aws_region: str = "us-west-2"

    # API Settings
    api_prefix: str = "/api"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # The "current" date in the synthetic data (last day of generated data)
    data_current_date: str = "2025-01-26"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
