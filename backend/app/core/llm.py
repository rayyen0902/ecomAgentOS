"""LLM provider abstraction and factory.

This module exposes a single factory, :func:`create_llm_provider`, which builds
an OpenAI-compatible client for Agnes, OpenAI, or DeepSeek. A ``mock`` provider
is also available for tests and local development.
"""

import os
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from app.core.config import get_settings


@dataclass(frozen=True)
class ProviderConfig:
    """Static configuration for a single LLM provider."""

    name: str
    base_url: str
    default_model: str
    api_key_env: str


_PROVIDER_CONFIGS: dict[str, ProviderConfig] = {
    "agnes": ProviderConfig(
        name="agnes",
        base_url="https://api.agnes.ai/v1",
        default_model="agnes-large-latest",
        api_key_env="AGNES_API_KEY",
    ),
    "openai": ProviderConfig(
        name="openai",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
    ),
    "deepseek": ProviderConfig(
        name="deepseek",
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
        api_key_env="DEEPSEEK_API_KEY",
    ),
}


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: ProviderConfig, api_key: str | None = None) -> None:
        self.config = config
        self.api_key = api_key
        self.default_model = config.default_model

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None,
        temperature: float,
        max_tokens: int | None,
        json_mode: bool,
    ) -> dict[str, Any]:
        """Call the chat completions endpoint and return normalized raw data."""

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None,
        temperature: float,
    ) -> AsyncIterator[str]:
        """Stream completion text chunks."""


class OpenAICompatibleProvider(BaseLLMProvider):
    """Provider implementation backed by the OpenAI SDK 1.x async client."""

    def __init__(self, config: ProviderConfig, api_key: str | None = None) -> None:
        super().__init__(config, api_key)
        resolved_key = api_key or os.environ.get(config.api_key_env)
        self.client = AsyncOpenAI(
            api_key=resolved_key or "no-key",
            base_url=config.base_url,
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> dict[str, Any]:
        model = model or self.default_model
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)
        usage = response.usage
        return {
            "content": response.choices[0].message.content or "",
            "model": response.model,
            "provider": self.config.name,
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        }

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        model = model or self.default_model
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


class MockProvider(BaseLLMProvider):
    """In-memory provider for unit tests and offline development."""

    def __init__(self) -> None:
        super().__init__(
            ProviderConfig(name="mock", base_url="", default_model="mock-model", api_key_env=""),
            api_key="mock",
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> dict[str, Any]:
        prompt_tokens = sum(len(m.get("content", "")) for m in messages)
        completion_tokens = 12
        return {
            "content": "Mock response",
            "model": model or self.default_model,
            "provider": "mock",
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        for token in ("Mock", " response"):
            yield token


def create_llm_provider(provider: str | None = None) -> BaseLLMProvider:
    """Create an LLM provider instance.

    Args:
        provider: Provider name. Defaults to ``settings.llm_provider``.

    Returns:
        A configured provider instance.

    Raises:
        ValueError: If the requested provider is not supported.
    """
    provider = provider or get_settings().llm_provider
    if provider == "mock":
        return MockProvider()

    if provider not in _PROVIDER_CONFIGS:
        supported = ", ".join(_PROVIDER_CONFIGS)
        raise ValueError(
            f"Unsupported LLM provider: {provider!r}. Supported providers are: {supported}."
        )

    config = _PROVIDER_CONFIGS[provider]
    return OpenAICompatibleProvider(config)
