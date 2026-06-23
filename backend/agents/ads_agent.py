"""广告Agent - 广告数据监控 + ROI分析 + 自动调价"""
from datetime import datetime

from langgraph.graph import StateGraph, END

from agents.base import BaseAgent, AgentState
from config.llm import agnes_client, TEXT_MODEL


class AdsAgent(BaseAgent):
    """
    广告Agent：
    - 每2小时抓取广告数据（点击/展现/转化/花费）
    - LLM分析ROI，给出调价建议
    - 低ROI关键词降价或暂停
    - 高转化关键词加价扩量
    - 重大调整（预算变动>20%）需人工审批
    """

    ADS_OPTIMIZATION_PROMPT = """
你是一个资深电商广告投放专家。基于以下广告数据，给出优化建议。

广告数据（近7天）：
{ads_data}

平台：{platform}
目标ROI：{target_roi}

请输出JSON：
{{
  "keyword_adjustments": [
    {{
      "keyword": "...",
      "current_bid": 0.0,
      "new_bid": 0.0,
      "change_pct": 0.0,
      "current_roi": 0.0,
      "action": "increase|decrease|pause|keep",
      "reason": "..."
    }}
  ],
  "budget_adjustments": [
    {{
      "campaign": "...",
      "current_budget": 0.0,
      "new_budget": 0.0,
      "change_pct": 0.0,
      "risk_level": "low|medium|high"
    }}
  ],
  "overall_roi_forecast": 0.0,
  "recommendation": "优化建议总结"
}}
"""

    def _build_graph(self) -> StateGraph:
        """构建广告Agent状态图"""
        graph = StateGraph(AgentState)

        graph.add_node("fetch_ads_data", self.fetch_ads_data)
        graph.add_node("analyze", self.analyze)
        graph.add_node("check_approval", self.check_approval_needed)
        graph.add_node("wait_approval", self.wait_for_approval)
        graph.add_node("execute", self.execute_actions)

        graph.set_entry_point("fetch_ads_data")
        graph.add_edge("fetch_ads_data", "analyze")
        graph.add_edge("analyze", "check_approval")
        graph.add_conditional_edges(
            "check_approval",
            lambda state: "wait_approval" if state["requires_approval"] else "execute",
            {"wait_approval": "wait_approval", "execute": "execute"},
        )
        graph.add_edge("wait_approval", "execute")
        graph.add_edge("execute", END)

        return graph.compile()

    async def fetch_ads_data(self, state: AgentState) -> AgentState:
        """RPA抓取广告报表数据"""
        shop_id = state["shop_id"]
        platform = state["input_data"].get("platform", "pdd")

        # TODO: 调用平台适配器获取广告数据
        ads_data = await self._fetch_platform_ads(shop_id, platform)
        state["input_data"]["ads_data"] = ads_data
        return state

    async def _fetch_platform_ads(self, shop_id: str, platform: str) -> list[dict]:
        """从平台RPA抓取广告数据"""
        # TODO: 调用DouyinPlatform或PDDPlatform的广告数据接口
        return []

    async def analyze(self, state: AgentState) -> AgentState:
        """LLM分析广告ROI，生成优化建议"""
        ads_data = state["input_data"].get("ads_data", [])
        platform = state["input_data"].get("platform", "pdd")
        target_roi = state["input_data"].get("target_roi", 2.5)

        if not ads_data:
            state["errors"].append({
                "error": "没有广告数据",
                "timestamp": datetime.now().isoformat(),
            })
            return state

        prompt = self.ADS_OPTIMIZATION_PROMPT.format(
            ads_data=str(ads_data),
            platform=platform,
            target_roi=target_roi,
        )

        response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        import json

        try:
            analysis = json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, AttributeError):
            analysis = {"keyword_adjustments": [], "budget_adjustments": [], "overall_roi_forecast": 0}

        state["decisions"].append({
            "analyzed_at": datetime.now().isoformat(),
            **analysis,
        })

        # 生成关键词调价动作
        for adj in analysis.get("keyword_adjustments", []):
            if adj.get("action") in ("increase", "decrease"):
                change_pct = abs(adj.get("change_pct", 0))
                risk_level = "high" if change_pct > 20 else "medium" if change_pct > 10 else "low"
                state["actions"].append({
                    "type": "adjust_keyword_bid",
                    "keyword": adj.get("keyword"),
                    "new_bid": adj.get("new_bid"),
                    "change_pct": adj.get("change_pct"),
                    "risk_level": risk_level,
                })

        # 生成预算调整动作（>20%变动需要审批）
        for budget_adj in analysis.get("budget_adjustments", []):
            change_pct = abs(budget_adj.get("change_pct", 0))
            if change_pct > 20:
                budget_adj["risk_level"] = "high"
                state["requires_approval"] = True
            state["actions"].append({
                "type": "adjust_budget",
                "campaign": budget_adj.get("campaign"),
                "new_budget": budget_adj.get("new_budget"),
                "change_pct": budget_adj.get("change_pct"),
                "risk_level": budget_adj.get("risk_level", "low"),
            })

        return state

    async def _execute_action(self, action: dict) -> dict:
        """执行广告动作"""
        action_type = action.get("type")
        if action_type == "adjust_keyword_bid":
            # TODO: RPA执行关键词出价调整
            return {"status": "bid_adjusted", "action": action}
        elif action_type == "adjust_budget":
            # TODO: RPA执行预算调整
            return {"status": "budget_adjusted", "action": action}
        return {"status": "unknown_action"}
