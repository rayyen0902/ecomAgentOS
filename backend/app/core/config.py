"""Application configuration.

Settings are loaded from environment variables where available. Secrets and
environment-specific values must never be hard-coded.
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "ecomAgentOS"
    app_version: str = "0.1.0"
    debug: bool = False

    # LLM provider selection: agnes | openai | deepseek | mock
    llm_provider: str = "agnes"

    # Agnes
    agnes_api_key: str | None = None
    agnes_base_url: str = "https://api.agnes.ai/v1"
    agnes_default_model: str = "agnes-large-latest"

    # OpenAI
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_default_model: str = "gpt-4o"

    # DeepSeek
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_default_model: str = "deepseek-chat"


settings = Settings()
