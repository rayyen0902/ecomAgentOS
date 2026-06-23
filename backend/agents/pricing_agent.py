"""定价Agent - 竞品价格跟踪 + 自动调价"""
from typing import Any
from datetime import datetime

from langgraph.graph import StateGraph, END

from agents.base import BaseAgent, AgentState
from config.llm import agnes_client, TEXT_MODEL


class PricingAgent(BaseAgent):
    """
    定价Agent：
    - 实时跟踪竞品价格
    - LLM推理决策最优价格
    - 保护利润底线
    - 大幅调价需要人工审批
    """

    # 定价规则配置
    PRICING_RULES = {
        "follow_competitor": {
            "trigger": "competitor drops price",
            "action": "match or undercut by 1-3%",
        },
        "protect_margin": {
            "min_margin": 0.15,
            "action": "never price below cost * 1.15",
        },
        "promotion_window": {
            "platform_activity": True,
            "action": "join auto with approval",
        },
        "slow_moving": {
            "no_sale_days": 7,
            "action": "drop 5% per cycle, max 20%",
        },
    }

    PRICING_PROMPT = """
你是一个资深电商定价专家。基于以下数据，给出最优定价建议。

当前商品：{product_title}
当前售价：{current_price}元
采购成本：{cost}元
当前毛利：{margin}%

竞品价格：
{competitor_prices}

定价规则：
{rules}

店铺策略：{shop_strategy}

请输出JSON格式的定价建议：
{{
  "new_price": 0.00,
  "change_pct": 0.00,
  "reason": "降价原因说明",
  "estimated_impact": {
    "click_change_pct": 0,
    "conversion_change_pct": 0
  },
  "risk_level": "low|medium|high",
  "min_acceptable_price": 0.00
}}
"""

    def _build_graph(self) -> StateGraph:
        """构建定价Agent状态图"""
        graph = StateGraph(AgentState)

        # 添加节点
        graph.add_node("analyze", self.analyze)
        graph.add_node("check_approval", self.check_approval_needed)
        graph.add_node("wait_approval", self.wait_for_approval)
        graph.add_node("execute", self.execute_actions)

        # 设置入口和执行流
        graph.set_entry_point("analyze")
        graph.add_edge("analyze", "check_approval")
        graph.add_conditional_edges(
            "check_approval",
            lambda state: "wait_approval" if state["requires_approval"] else "execute",
            {"wait_approval": "wait_approval", "execute": "execute"},
        )
        graph.add_edge("wait_approval", "execute")
        graph.add_edge("execute", END)

        return graph.compile()

    async def analyze(self, state: AgentState) -> AgentState:
        """分析竞品价格，生成定价建议"""
        competitor_prices = state["input_data"].get("competitor_prices", [])
        current_price = state["input_data"].get("current_price", 0)
        cost = state["input_data"].get("cost", 0)
        product_title = state["input_data"].get("product_title", "未知商品")

        margin = ((current_price - cost) / current_price * 100) if current_price > 0 else 0

        competitor_str = "\n".join(
            f"- {cp.get('shop', '未知')}: ¥{cp.get('price', 0)}"
            for cp in competitor_prices
        )

        prompt = self.PRICING_PROMPT.format(
            product_title=product_title,
            current_price=current_price,
            cost=cost,
            margin=round(margin, 1),
            competitor_prices=competitor_str,
            rules=str(self.PRICING_RULES),
            shop_strategy=state["input_data"].get("shop_strategy", "balanced"),
        )

        response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        import json

        try:
            decision = json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, AttributeError):
            decision = {"new_price": current_price, "reason": "解析失败，保持原价"}

        # 计算价格变动百分比
        if current_price > 0:
            decision["change_pct"] = round(
                abs(decision.get("new_price", current_price) - current_price) / current_price * 100, 1
            )

        # 价格变动超过15%标记为高风险
        if decision.get("change_pct", 0) > 15:
            decision["risk_level"] = "high"

        state["decisions"].append(decision)
        state["actions"].append({
            "type": "update_price",
            "product_id": state["input_data"].get("product_id"),
            "new_price": decision.get("new_price"),
            "shop_id": self.shop_id,
            "risk_level": decision.get("risk_level", "low"),
        })
        return state

    async def _execute_action(self, action: dict) -> dict:
        """执行改价动作"""
        if action.get("type") != "update_price":
            return {"status": "skipped", "reason": f"未知动作类型: {action.get('type')}"}

        # TODO: 调用RPA执行改价
        return {
            "status": "executed",
            "action": action,
            "timestamp": datetime.now().isoformat(),
        }
