"""RPA反检测配置"""
import asyncio
import random
from playwright.async_api import Page

# 反检测配置
STEALTH_CONFIG = {
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "locale": "zh-CN",
    "timezone_id": "Asia/Shanghai",
    "permissions": ["geolocation"],
    "extra_http_headers": {
        "Accept-Language": "zh-CN,zh;q=0.9",
    },
}


async def human_like_behavior(page: Page):
    """模拟人类操作习惯"""
    # 随机延迟（正态分布，均值1秒）
    await asyncio.sleep(random.gauss(1.0, 0.3))

    # 随机鼠标移动
    await page.mouse.move(
        random.randint(100, 800),
        random.randint(100, 600),
        steps=random.randint(5, 15),
    )


async def human_type(page: Page, selector: str, text: str):
    """模拟人类打字速度"""
    await page.click(selector)
    for char in text:
        await page.keyboard.type(char)
        await asyncio.sleep(random.uniform(0.05, 0.2))  # 随机按键间隔


async def human_scroll(page: Page, steps: int = 5):
    """模拟人类滚动行为"""
    for _ in range(steps):
        await page.mouse.wheel(
            0,
            random.randint(200, 800),
        )
        await asyncio.sleep(random.uniform(0.1, 0.5))
