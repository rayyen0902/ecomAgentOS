"""Application configuration.

Settings are loaded from environment variables where available. Secrets and
environment-specific values must never be hard-coded.
"""

from __future__ import annotations

from functools import cached_property

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings.

    Required fields (no defaults):
        secret_key
        database_url
        redis_url

    Optional fields carry sensible defaults.
    """

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    app_env: str = "development"
    app_name: str = "ecomAgentOS"
    app_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 6200

    # ------------------------------------------------------------------
    # Secrets (required)
    # ------------------------------------------------------------------
    secret_key: str

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    database_url: str

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------
    redis_url: str

    # ------------------------------------------------------------------
    # LLM provider selection: agnes | openai | deepseek | mock
    # ------------------------------------------------------------------
    llm_provider: str = "agnes"

    # Agnes
    agnes_api_key: str | None = None
    agnes_base_url: str | None = None
    agnes_default_model: str = "agnes-large-latest"

    # OpenAI
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_default_model: str = "gpt-4o"

    # DeepSeek
    deepseek_api_key: str | None = None
    deepseek_base_url: str | None = None
    deepseek_default_model: str = "deepseek-chat"

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    log_level: str = "INFO"
    log_format: str = "json"  # json | console

    @cached_property
    def llm_providers(self) -> tuple[str, ...]:
        """Return the ordered list of supported provider names."""
        return ("agnes", "openai", "deepseek", "mock")

    @property
    def is_production(self) -> bool:
        """Whether the application runs in production mode."""
        return self.app_env == "production"


settings = Settings()
