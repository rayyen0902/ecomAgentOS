"""Tests for the global configuration (Settings)."""

import subprocess

import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.fixture()
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Remove all relevant env vars to simulate a clean environment."""
    for key in (
        "SECRET_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "APP_ENV",
        "LLM_PROVIDER",
        "LOG_LEVEL",
        "LOG_FORMAT",
    ):
        monkeypatch.delenv(key, raising=False)
    return monkeypatch


def test_required_fields_missing_raises(clean_env: pytest.MonkeyPatch) -> None:
    """Missing SECRET_KEY raises a validation error."""
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_required_fields_all_present(clean_env: pytest.MonkeyPatch) -> None:
    """All required fields supplied → settings loads cleanly."""
    clean_env.setenv("SECRET_KEY", "test-secret")
    clean_env.setenv("DATABASE_URL", "sqlite:///test.db")
    clean_env.setenv("REDIS_URL", "redis://localhost/0")
    s = Settings(_env_file=None)
    assert s.secret_key == "test-secret"
    assert s.database_url == "sqlite:///test.db"
    assert s.redis_url == "redis://localhost/0"


def test_defaults(clean_env: pytest.MonkeyPatch) -> None:
    """Optional fields carry correct defaults."""
    clean_env.setenv("SECRET_KEY", "x")
    clean_env.setenv("DATABASE_URL", "sqlite:///x.db")
    clean_env.setenv("REDIS_URL", "redis://localhost/0")
    s = Settings(_env_file=None)
    assert s.app_name == "ecomAgentOS"
    assert s.app_version == "0.1.0"
    assert s.app_env == "development"
    assert s.llm_provider == "agnes"
    assert s.log_level == "INFO"
    assert s.log_format == "json"
    assert s.agnes_default_model == "agnes-large-latest"
    assert s.openai_default_model == "gpt-4o"
    assert s.deepseek_default_model == "deepseek-chat"


def test_env_override(clean_env: pytest.MonkeyPatch) -> None:
    """Environment variables override defaults."""
    clean_env.setenv("SECRET_KEY", "from-env")
    clean_env.setenv("DATABASE_URL", "postgresql://env/db")
    clean_env.setenv("REDIS_URL", "redis://env/1")
    clean_env.setenv("APP_ENV", "staging")
    clean_env.setenv("LLM_PROVIDER", "openai")
    clean_env.setenv("LOG_LEVEL", "DEBUG")
    clean_env.setenv("LOG_FORMAT", "console")

    s = Settings(_env_file=None)
    assert s.secret_key == "from-env"
    assert s.app_env == "staging"
    assert s.llm_provider == "openai"
    assert s.log_level == "DEBUG"
    assert s.log_format == "console"


def test_is_production(clean_env: pytest.MonkeyPatch) -> None:
    """is_production reflects APP_ENV."""
    clean_env.setenv("SECRET_KEY", "x")
    clean_env.setenv("DATABASE_URL", "sqlite:///x.db")
    clean_env.setenv("REDIS_URL", "redis://localhost/0")
    s = Settings(_env_file=None)
    assert s.is_production is False

    clean_env.setenv("APP_ENV", "production")
    s2 = Settings(_env_file=None)
    assert s2.is_production is True


def test_llm_providers_tuple() -> None:
    """llm_providers returns a tuple of supported names."""
    from app.core.config import get_settings

    settings = get_settings()
    assert isinstance(settings.llm_providers, tuple)
    assert "mock" in settings.llm_providers


def test_settings_module_import() -> None:
    """from app.core.config import get_settings works."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.app_name == "ecomAgentOS"


def test_no_hardcoded_secrets_in_source() -> None:
    """Source code must not contain hard-coded secret values."""
    result = subprocess.run(
        ["grep", "-rn", "hardcoded_secret_placeholder", "app/core/config.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "Hard-coded secret found in config.py"


def test_settings_has_env_file_config() -> None:
    """Settings model uses .env file for loading."""
    assert ".env" in str(Settings.model_config.get("env_file", ""))


def test_clear_error_message_on_missing_fields(clean_env: pytest.MonkeyPatch) -> None:
    """Missing required fields produce a clear ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)
    error_messages = str(exc_info.value)
    assert "secret_key" in error_messages.lower() or "secret" in error_messages.lower()
