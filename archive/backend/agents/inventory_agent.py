"""库存Agent - 库存巡检 + 缺货预警 + 补货建议"""
from datetime import datetime

from langgraph.graph import StateGraph, END

from agents.base import BaseAgent, AgentState
from config.llm import agnes_client, TEXT_MODEL


class InventoryAgent(BaseAgent):
    """
    库存Agent：
    - 定期RPA巡检各店铺库存
    - 缺货预警（低于安全库存自动触发补货建议）
    - 低库存商品自动触发选品Agent
    - 滞销商品建议促销
    """

    INVENTORY_CHECK_PROMPT = """
你是一个资深库存管理顾问。基于以下库存数据，给出补货和促销建议。

当前库存状态：
{inventory_data}

安全库存阈值：
{safety_stock_levels}

历史销售数据（近30天）：
{sales_history}

请输出JSON：
{{
  "restock_recommendations": [
    {{
      "product_id": "...",
      "product_name": "...",
      "current_stock": 0,
      "safety_stock": 0,
      "recommended_qty": 0,
      "urgency": "critical|high|medium|low",
      "reason": "..."
    }}
  ],
  "promotions": [
    {{
      "product_id": "...",
      "reason": "滞销超过30天",
      "suggested_discount": "10%"
    }}
  ],
  "alerts": ["缺货预警1", "滞销预警2"]
}}
"""

    def _build_graph(self) -> StateGraph:
        """构建库存Agent状态图"""
        graph = StateGraph(AgentState)

        graph.add_node("scan_inventory", self.scan_inventory)
        graph.add_node("analyze", self.analyze)
        graph.add_node("check_approval", self.check_approval_needed)
        graph.add_node("wait_approval", self.wait_for_approval)
        graph.add_node("execute", self.execute_actions)

        graph.set_entry_point("scan_inventory")
        graph.add_edge("scan_inventory", "analyze")
        graph.add_edge("analyze", "check_approval")
        graph.add_conditional_edges(
            "check_approval",
            lambda state: "wait_approval" if state["requires_approval"] else "execute",
            {"wait_approval": "wait_approval", "execute": "execute"},
        )
        graph.add_edge("wait_approval", "execute")
        graph.add_edge("execute", END)

        return graph.compile()

    async def scan_inventory(self, state: AgentState) -> AgentState:
        """RPA巡检各店铺库存"""
        shop_ids = state["input_data"].get("shop_ids", [])

        for shop_id in shop_ids:
            # TODO: RPA抓取店铺库存数据
            inventory = await self._fetch_shop_inventory(shop_id)
            state["input_data"].setdefault("inventory_data", []).extend(inventory)

        return state

    async def _fetch_shop_inventory(self, shop_id: str) -> list[dict]:
        """从平台RPA抓取库存数据"""
        # TODO: 调用平台适配器获取库存
        return []

    async def analyze(self, state: AgentState) -> AgentState:
        """LLM分析库存，生成补货和促销建议"""
        inventory_data = state["input_data"].get("inventory_data", [])
        safety_stock = state["input_data"].get("safety_stock_levels", {})
        sales_history = state["input_data"].get("sales_history", {})

        if not inventory_data:
            state["errors"].append({
                "error": "没有库存数据",
                "timestamp": datetime.now().isoformat(),
            })
            return state

        prompt = self.INVENTORY_CHECK_PROMPT.format(
            inventory_data=str(inventory_data),
            safety_stock_levels=str(safety_stock),
            sales_history=str(sales_history),
        )

        response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        import json

        try:
            analysis = json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, AttributeError):
            analysis = {"restock_recommendations": [], "promotions": [], "alerts": []}

        state["decisions"].append({
            "analyzed_at": datetime.now().isoformat(),
            **analysis,
        })

        # 生成补货建议动作
        for rec in analysis.get("restock_recommendations", []):
            urgency = rec.get("urgency", "low")
            risk_level = "high" if urgency == "critical" else "medium"
            state["actions"].append({
                "type": "restock",
                "product_id": rec.get("product_id"),
                "recommended_qty": rec.get("recommended_qty"),
                "urgency": urgency,
                "risk_level": risk_level,
            })

        # 生成促销建议动作
        for promo in analysis.get("promotions", []):
            state["actions"].append({
                "type": "promotion",
                "product_id": promo.get("product_id"),
                "suggested_discount": promo.get("suggested_discount"),
                "risk_level": "low",
            })

        # 如果有critical级别缺货，标记需要审批
        critical_items = [r for r in analysis.get("restock_recommendations", []) if r.get("urgency") == "critical"]
        if critical_items:
            state["actions"].append({
                "type": "alert_critical_stockout",
                "items": critical_items,
                "risk_level": "high",
            })
            state["requires_approval"] = True

        return state

    async def _execute_action(self, action: dict) -> dict:
        """执行库存动作"""
        action_type = action.get("type")
        if action_type == "restock":
            # TODO: RPA在1688上下单补货
            return {"status": "restock_triggered", "action": action}
        elif action_type == "promotion":
            # TODO: RPA执行降价促销
            return {"status": "promotion_triggered", "action": action}
        elif action_type == "alert_critical_stockout":
            # TODO: 推送紧急缺货告警
            return {"status": "alert_sent", "action": action}
        return {"status": "unknown_action"}
