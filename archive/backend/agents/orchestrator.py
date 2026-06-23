"""Orchestrator调度中枢"""
from datetime import datetime
from celery.schedules import crontab

from config.llm import agnes_client, TEXT_MODEL
from config.settings import settings


class OrchestratorAgent:
    """
    调度中枢：决定何时触发哪个Agent
    基于事件驱动 + 定时触发双模式
    """

    # 定时任务配置
    SCHEDULED_TASKS = {
        "selection_scan": {
            "schedule": crontab(hour=8, minute=0),
            "agent": "selection",
        },
        "price_check": {
            "schedule": crontab(minute="*/15"),
            "agent": "pricing",
        },
        "ads_optimization": {
            "schedule": crontab(minute=0, hour="*/2"),
            "agent": "ads",
        },
        "inventory_check": {
            "schedule": crontab(hour="9,18", minute=0),
            "agent": "inventory",
        },
        "order_process": {
            "schedule": crontab(minute="*/5"),
            "agent": "inventory",
        },
    }

    # 事件路由表
    EVENT_ROUTING = {
        "new_order": "inventory",
        "competitor_price_drop": "pricing",
        "low_stock": "inventory",
        "negative_review": "customer_service",
        "user_command": "orchestrator",
    }

    async def route(self, event: dict) -> str:
        """根据事件类型路由到对应Agent"""
        event_type = event.get("type")
        agent_name = self.EVENT_ROUTING.get(event_type)
        if agent_name:
            return agent_name
        return "orchestrator"

    async def _parse_user_intent(self, event: dict) -> str:
        """
        解析手机端自然语言指令
        例："帮我把拼多多3店的连衣裙降价10%"
             → routing to pricing agent for pdd_shop_3
        """
        response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个电商运营指令解析器。将用户的自然语言指令解析为JSON，"
                        "包含platform、shop_id、operation、parameters等字段。"
                        "只输出JSON，不要输出其他内容。"
                    ),
                },
                {"role": "user", "content": event.get("message", "")},
            ],
        )
        return response.choices[0].message.content

    async def dispatch(self, agent_name: str, shop_id: str, data: dict) -> dict:
        """
        分发任务到指定Agent

        Args:
            agent_name: Agent名称（selection/pricing/inventory/ads/cs/content/image/video）
            shop_id: 店铺ID
            data: 任务数据

        Returns:
            执行结果
        """
        # TODO: 根据agent_name实例化对应的Agent类并执行
        return {
            "agent": agent_name,
            "shop_id": shop_id,
            "status": "dispatched",
            "timestamp": datetime.now().isoformat(),
        }
