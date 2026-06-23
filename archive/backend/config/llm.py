"""Agnes AI LLM客户端配置"""
from openai import AsyncOpenAI

from config.settings import settings

# 模型配置
TEXT_MODEL = settings.text_model
IMAGE_MODEL = settings.image_model
VIDEO_MODEL = settings.video_model


def _get_client():
    """延迟创建客户端，避免模块级别立即初始化"""
    return AsyncOpenAI(
        api_key=settings.agnes_api_key,
        base_url=settings.agnes_base_url,
    )


async def chat_completion(messages: list[dict], model: str = TEXT_MODEL, **kwargs) -> str:
    """
    简化的聊天补全接口

    Args:
        messages: 消息列表，格式 [{"role": "user/system/assistant", "content": "..."}]
        model: 使用的模型，默认为TEXT_MODEL
        **kwargs: 其他参数（temperature, max_tokens等）

    Returns:
        模型回复的文本内容
    """
    client = _get_client()
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )
    return response.choices[0].message.content


async def generate_image(prompt: str, model: str = IMAGE_MODEL, **kwargs) -> str:
    """
    生成图片

    Args:
        prompt: 图片描述
        model: 使用的模型，默认为IMAGE_MODEL
        **kwargs: 其他参数（size, quality等）

    Returns:
        图片URL
    """
    client = _get_client()
    response = await client.images.generate(
        model=model,
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        **kwargs,
    )
    return response.data[0].url
