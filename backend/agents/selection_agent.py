"""选品Agent - 1688热销品分析 + 跨平台可行性评估"""
from datetime import datetime

from langgraph.graph import StateGraph, END

from agents.base import BaseAgent, AgentState
from config.llm import agnes_client, TEXT_MODEL


class SelectionAgent(BaseAgent):
    """
    选品Agent：
    - RPA抓取1688热销商品数据
    - LLM分析跨平台销售可行性
    - 生成选品报告（评分 + 推荐理由）
    - 推送手机端供运营确认
    """

    SELECTION_ANALYSIS_PROMPT = """
你是一个资深电商选品顾问。基于以下1688商品数据，分析该商品在各电商平台的销售可行性。

商品数据：
{product_data}

店铺历史爆款：
{shop_history}

当前平台竞品数据：
{competitor_data}

请输出JSON格式分析报告：
{{
  "overall_score": 0-100,
  "platform_scores": {{
    "douyin": {{"score": 0-100, "reason": "...", "suggested_price": 0}},
    "taobao": {{"score": 0-100, "reason": "...", "suggested_price": 0}},
    "pdd": {{"score": 0-100, "reason": "...", "suggested_price": 0}},
    "xiaohongshu": {{"score": 0-100, "reason": "...", "suggested_price": 0}}
  }},
  "profit_estimate": {{"cost": 0, "avg_sell_price": 0, "gross_margin": "0%"}},
  "risks": ["风险1", "风险2"],
  "recommendation": "强烈推荐|推荐|观望|不推荐"
}}
"""

    def _build_graph(self) -> StateGraph:
        """构建选品Agent状态图"""
        graph = StateGraph(AgentState)

        graph.add_node("scrape_1688", self.scrape_hot_products)
        graph.add_node("analyze", self.analyze)
        graph.add_node("check_approval", self.check_approval_needed)
        graph.add_node("wait_approval", self.wait_for_approval)
        graph.add_node("execute", self.execute_actions)

        graph.set_entry_point("scrape_1688")
        graph.add_edge("scrape_1688", "analyze")
        graph.add_edge("analyze", "check_approval")
        graph.add_conditional_edges(
            "check_approval",
            lambda state: "wait_approval" if state["requires_approval"] else "execute",
            {"wait_approval": "wait_approval", "execute": "execute"},
        )
        graph.add_edge("wait_approval", "execute")
        graph.add_edge("execute", END)

        return graph.compile()

    async def scrape_hot_products(self, state: AgentState) -> AgentState:
        """
        RPA抓取1688热销商品数据
        包括：销量/价格/起订量/货期/供货商评分
        """
        keywords = state["input_data"].get("keywords", ["日用百货", "美妆工具", "家居用品"])

        for keyword in keywords:
            # TODO: RPA抓取1688热销商品
            # 参考 rpa/platforms/alibaba_1688.py
            products = await self._fetch_1688_products(keyword)
            state["input_data"].setdefault("hot_products", []).extend(products)

        return state

    async def _fetch_1688_products(self, keyword: str) -> list[dict]:
        """从1688抓取热销商品"""
        # TODO: 实现RPA抓取
        return []

    async def analyze(self, state: AgentState) -> AgentState:
        """LLM分析选品可行性"""
        hot_products = state["input_data"].get("hot_products", [])
        shop_history = state["input_data"].get("shop_history", [])
        competitor_data = state["input_data"].get("competitor_data", {})

        if not hot_products:
            state["errors"].append({
                "error": "没有抓取到1688热销商品",
                "timestamp": datetime.now().isoformat(),
            })
            return state

        # 对每个候选商品进行分析
        recommendations = []
        for product in hot_products[:10]:  # 最多分析10个
            prompt = self.SELECTION_ANALYSIS_PROMPT.format(
                product_data=str(product),
                shop_history=str(shop_history),
                competitor_data=str(competitor_data),
            )

            response = await agnes_client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )

            import json

            try:
                analysis = json.loads(response.choices[0].message.content)
            except (json.JSONDecodeError, AttributeError):
                analysis = {"overall_score": 0, "recommendation": "不推荐", "risks": ["分析失败"]}

            analysis["product"] = product
            analysis["analyzed_at"] = datetime.now().isoformat()
            recommendations.append(analysis)

        # 按综合评分排序
        recommendations.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

        state["decisions"].extend(recommendations[:5])  # 取前5个
        state["actions"].append({
            "type": "push_selection_report",
            "recommendations": recommendations[:5],
            "risk_level": "medium",
        })
        return state

    async def _execute_action(self, action: dict) -> dict:
        """执行选品动作"""
        if action.get("type") == "push_selection_report":
            # TODO: 通过WebSocket推送选品报告到手机端
            return {
                "status": "report_pushed",
                "count": len(action.get("recommendations", [])),
                "timestamp": datetime.now().isoformat(),
            }
        return {"status": "unknown_action"}
