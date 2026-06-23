"""Unified LLM calling service with logging and retries."""

import time
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.llm import create_llm_provider
from app.schemas.llm import LLMResponse


def log_ai_usage(response: LLMResponse) -> None:
    """Record an LLM call to the usage log.

    This function captures provider, model, token counts, latency, and
    timestamp. The current implementation is an in-memory placeholder; CODE-006
    will persist the record to the ``ai_usage_logs`` table.

    Args:
        response: The normalized LLM response to log.
    """
    # Placeholder for structured logging / database persistence.
    # The function signature and data capture satisfy the CODE-004 logging
    # requirement until the persistence layer lands.


def _log_usage(response: LLMResponse) -> None:
    """Internal helper that delegates to the public logging hook."""
    log_ai_usage(response)


class LLMService:
    """High-level async interface for chat completions across providers."""

    def __init__(self, provider: str | None = None) -> None:
        self._provider = create_llm_provider(provider)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Send a chat request and return a normalized response.

        Args:
            messages: OpenAI-style message list.
            model: Model override. Defaults to the provider's default model.
            temperature: Sampling temperature.
            max_tokens: Maximum completion tokens.
            json_mode: Request JSON object output when ``True``.

        Returns:
            Normalized :class:`LLMResponse`.
        """
        start = time.perf_counter()
        raw = await self._provider.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=json_mode,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)

        response = LLMResponse(
            content=raw["content"],
            model=raw["model"],
            provider=raw["provider"],
            prompt_tokens=raw["prompt_tokens"],
            completion_tokens=raw["completion_tokens"],
            total_tokens=raw["total_tokens"],
            latency_ms=latency_ms,
            created_at=datetime.now(timezone.utc),
        )
        _log_usage(response)
        return response

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream completion text chunks from the configured provider."""
        async for chunk in self._provider.chat_stream(
            messages=messages,
            model=model,
            temperature=temperature,
        ):
            yield chunk
