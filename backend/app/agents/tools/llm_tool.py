"""LLM tool exposed to agents.

Agents can call :func:`llm_chat` to request a chat completion without needing
 to know which provider is configured.
"""

from app.schemas.llm import LLMResponse
from app.services.llm_service import LLMService


async def llm_chat(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    json_mode: bool = False,
) -> LLMResponse:
    """Agent-facing wrapper around :class:`LLMService`.

    Args:
        messages: OpenAI-style message list.
        model: Optional model override.
        temperature: Sampling temperature.
        max_tokens: Optional maximum completion tokens.
        json_mode: Request JSON object output when ``True``.

    Returns:
        Normalized :class:`LLMResponse`.
    """
    service = LLMService()
    return await service.chat(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        json_mode=json_mode,
    )
