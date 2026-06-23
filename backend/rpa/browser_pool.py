"""浏览器池管理 - 多店铺独立浏览器上下文"""
import asyncio
from typing import Dict, Callable, Any
from playwright.async_api import async_playwright, BrowserContext, Page

from config.settings import settings


class BrowserPool:
    """
    每个店铺维护独立的浏览器上下文
    支持并发操作多个店铺，互不干扰
    """

    def __init__(self):
        self._playwright = None
        self._browser = None
        self._contexts: Dict[str, BrowserContext] = {}
        self._lock = asyncio.Lock()

    async def initialize(self):
        """初始化浏览器实例"""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)

    async def close(self):
        """关闭所有浏览器实例"""
        for context in self._contexts.values():
            await context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def get_context(self, shop_id: str) -> BrowserContext:
        """获取或创建店铺的浏览器上下文"""
        async with self._lock:
            if shop_id not in self._contexts:
                # TODO: 加载该店铺的Cookie
                context = await self._browser.new_context()
                self._contexts[shop_id] = context
            return self._contexts[shop_id]

    async def execute(self, shop_id: str, task_func: Callable, *args) -> Any:
        """
        在店铺独立的浏览器上下文中执行任务

        Args:
            shop_id: 店铺ID
            task_func: 要执行的异步函数，接收page参数
            *args: 传递给task_func的其他参数

        Returns:
            task_func的返回值
        """
        context = await self.get_context(shop_id)
        page = await context.new_page()
        try:
            result = await task_func(page, *args)
            # TODO: 刷新Cookie
            return result
        except Exception as e:
            # 异常截图存档
            await page.screenshot(path=f"screenshots/error_{shop_id}.png")
            raise
        finally:
            await page.close()


# 全局浏览器池实例
browser_pool = BrowserPool()
