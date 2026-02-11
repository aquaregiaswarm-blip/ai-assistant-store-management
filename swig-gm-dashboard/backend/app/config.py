"""Configuration settings for the Swig GM Dashboard API."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # BigQuery
    gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "prj-cts-lab-vertex-sandbox")
    bigquery_dataset: str = os.getenv("BIGQUERY_DATASET", "swig_operations")

    # OpenAI API Key
    openai_api_key: str = ""

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
