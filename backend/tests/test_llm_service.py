"""Tests for the LLM provider abstraction and LLMService."""

import pytest

from app.core.llm import _PROVIDER_CONFIGS, MockProvider, create_llm_provider
from app.schemas.llm import LLMResponse
from app.services.llm_service import LLMService, log_ai_usage


@pytest.mark.parametrize("provider_name", ["agnes", "openai", "deepseek"])
def test_create_llm_provider_supported(provider_name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Factory returns the correct provider configuration for each backend."""
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    provider = create_llm_provider(provider_name)
    assert provider.config.name == provider_name
    assert provider.default_model == _PROVIDER_CONFIGS[provider_name].default_model


def test_create_llm_provider_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mock provider is selected when LLM_PROVIDER=mock."""
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    provider = create_llm_provider()
    assert provider.config.name == "mock"
    assert provider.default_model == "mock-model"


def test_create_llm_provider_unsupported() -> None:
    """An unsupported provider name raises a clear error."""
    with pytest.raises(ValueError, match="Unsupported LLM provider: 'unknown'"):
        create_llm_provider("unknown")


@pytest.mark.asyncio
async def test_llm_service_chat_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    """LLMService.chat returns a complete LLMResponse via the mock provider."""
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    service = LLMService()

    response = await service.chat([{"role": "user", "content": "Hello"}])

    assert isinstance(response, LLMResponse)
    assert response.content == "Mock response"
    assert response.provider == "mock"
    assert response.model == "mock-model"
    assert response.prompt_tokens > 0
    assert response.completion_tokens == 12
    assert response.total_tokens == response.prompt_tokens + response.completion_tokens
    assert response.latency_ms >= 0
    assert response.created_at.tzinfo is not None


@pytest.mark.asyncio
async def test_llm_service_chat_model_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """The model argument is forwarded to the provider."""
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    service = LLMService()

    response = await service.chat(
        [{"role": "user", "content": "Hi"}],
        model="custom-mock",
        temperature=0.5,
        max_tokens=100,
    )

    assert response.model == "custom-mock"


@pytest.mark.asyncio
async def test_llm_service_chat_stream_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    """LLMService.chat_stream yields chunks from the mock provider."""
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    service = LLMService()

    chunks = [chunk async for chunk in service.chat_stream([{"role": "user", "content": "Hi"}])]

    assert "".join(chunks) == "Mock response"


def test_log_ai_usage_does_not_raise() -> None:
    """The logging hook is callable with a valid response."""
    response = LLMResponse(
        content="test",
        model="mock-model",
        provider="mock",
        prompt_tokens=1,
        completion_tokens=2,
        total_tokens=3,
        latency_ms=100,
        created_at="2024-01-01T00:00:00+00:00",
    )
    log_ai_usage(response)


@pytest.mark.asyncio
async def test_mock_provider_token_counting() -> None:
    """Mock provider derives token counts from input message lengths."""
    provider = MockProvider()
    raw = await provider.chat([{"role": "user", "content": "abc"}])

    assert raw["prompt_tokens"] == 3
    assert raw["completion_tokens"] == 12
    assert raw["total_tokens"] == 15
