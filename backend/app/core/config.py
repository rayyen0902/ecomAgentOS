"""Application configuration placeholders.

This module will be extended in CODE-005 to load environment-specific settings.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Global application settings.

    Secrets and environment-specific values must be provided via environment
    variables rather than hard-coded constants.
    """

    app_name: str = "ecomAgentOS"
    app_version: str = "0.1.0"
    debug: bool = False


settings = Settings()
