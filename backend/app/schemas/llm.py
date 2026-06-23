"""Pydantic schemas for LLM requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """Standardized response from any LLM provider.

    Attributes:
        content: The generated text content.
        model: The model identifier returned by the provider.
        provider: The provider name (e.g. ``agnes``, ``openai``, ``deepseek``).
        prompt_tokens: Number of tokens in the input prompt.
        completion_tokens: Number of tokens in the generated completion.
        total_tokens: Total tokens consumed by the request.
        latency_ms: Request latency in milliseconds.
        created_at: UTC timestamp when the response was created.
    """

    content: str
    model: str
    provider: str
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    latency_ms: int = Field(ge=0)
    created_at: datetime
