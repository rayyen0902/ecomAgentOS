"""Global test fixtures.

Ensures required environment variables are set **before** any test module
is imported (via ``pytest_configure`` hook), and clears the ``get_settings``
lru_cache so every test process starts with a clean slate.
"""

import os

import pytest

from app.core.config import get_settings


def pytest_configure(config: pytest.Config) -> None:
    """Set deterministic test env vars before any test module is imported.

    ``pytest_configure`` runs during pytest's collection phase — before any
    test file is imported — so Settings is built with these values instead
    of falling back to a local ``.env`` file or CI's missing vars.

    Key variables are forcefully overwritten (not ``setdefault``) to prevent
    CI environments that preset ``LLM_PROVIDER=agnes`` from breaking mock
    tests (F-005).
    """
    os.environ["SECRET_KEY"] = "test-secret-key-for-ci-only"
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://ecom:LocalDev2024!@localhost:6210/ecomagentos"
    os.environ["REDIS_URL"] = "redis://localhost:6211/0"
    os.environ["LLM_PROVIDER"] = "mock"
    os.environ["APP_ENV"] = "test"
    os.environ["LOG_LEVEL"] = "WARNING"
    os.environ["LOG_FORMAT"] = "json"
    os.environ["AGNES_API_KEY"] = "test-agnes-key"
    os.environ["OPENAI_API_KEY"] = "test-openai-key"
    os.environ["DEEPSEEK_API_KEY"] = "test-deepseek-key"

    get_settings.cache_clear()


@pytest.fixture(scope="session", autouse=True)
def _test_env_teardown() -> None:
    """Clear the settings cache after the test session ends."""
    yield
    get_settings.cache_clear()
