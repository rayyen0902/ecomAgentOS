"""平台RPA适配器基类"""
from abc import ABC, abstractmethod
from playwright.async_api import Page

from rpa.browser_pool import BrowserPool


class BasePlatform(ABC):
    """
    电商平台RPA适配器基类
    所有平台适配器必须实现以下方法
    """

    def __init__(self, browser_pool: BrowserPool):
        self.pool = browser_pool

    @abstractmethod
    async def login(self, page: Page) -> bool:
        """
        登录平台

        Returns:
            是否登录成功
        """
        pass

    @abstractmethod
    async def scrape_products(self, page: Page, shop_id: str) -> list[dict]:
        """
        抓取商品列表

        Returns:
            商品列表，每项包含id/title/price等
        """
        pass

    @abstractmethod
    async def scrape_prices(self, page: Page, product_ids: list[str]) -> list[dict]:
        """
        抓取商品价格信息

        Returns:
            价格列表，每项包含product_id/price
        """
        pass

    @abstractmethod
    async def update_price(self, page: Page, product_id: str, new_price: float) -> bool:
        """
        更新商品价格

        Returns:
            是否更新成功
        """
        pass

    @abstractmethod
    async def scrape_orders(self, page: Page, shop_id: str) -> list[dict]:
        """
        抓取订单列表

        Returns:
            订单列表
        """
        pass

    @abstractmethod
    async def upload_product(self, page: Page, product_data: dict) -> str:
        """
        上架商品

        Returns:
            平台商品ID
        """
        pass
