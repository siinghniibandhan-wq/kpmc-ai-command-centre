from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    aws_region: str = "us-east-2"
    gemini_parameter_name: str = "/kpmc-ai-command-centre/production/GEMINI_API_KEY"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-4-argon"
    cors_allowed_origins: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
