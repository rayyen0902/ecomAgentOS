"""客服Agent - 自动回复 + 情绪分析 + 转人工"""
from datetime import datetime

from langgraph.graph import StateGraph, END

from agents.base import BaseAgent, AgentState
from config.llm import agnes_client, TEXT_MODEL


class CustomerServiceAgent(BaseAgent):
    """
    客服Agent：
    - 自主学习商品知识和平台规则
    - 自动回复常见买家问题
    - 情绪分析，负面情绪转人工
    - 生成回复草稿供人工审核
    """

    CS_SYSTEM_PROMPT = """
你是一个专业的电商客服人员。基于以下店铺知识库，回复买家的咨询。

知识库：
{kb}

回复要求：
1. 语气友好、专业
2. 准确引用商品信息
3. 涉及退款/退货时，提示转人工
4. 回复长度控制在100字以内
"""

    SENTIMENT_ANALYSIS_PROMPT = """
分析以下买家消息的情绪：
{message}

请输出JSON：
{{
  "sentiment": "positive|neutral|negative",
  "score": -1.0到1.0之间的浮点数,
  "confidence": 0.0到1.0之间的浮点数,
  "needs_escalation": true/false
}}
"""

    def _build_graph(self) -> StateGraph:
        """构建客服Agent状态图"""
        graph = StateGraph(AgentState)

        graph.add_node("build_knowledge", self.build_knowledge_base)
        graph.add_node("analyze_message", self.analyze_and_reply)
        graph.add_node("check_approval", self.check_approval_needed)
        graph.add_node("wait_approval", self.wait_for_approval)
        graph.add_node("execute", self.execute_actions)

        graph.set_entry_point("build_knowledge")
        graph.add_edge("build_knowledge", "analyze_message")
        graph.add_edge("analyze_message", "check_approval")
        graph.add_conditional_edges(
            "check_approval",
            lambda state: "wait_approval" if state["requires_approval"] else "execute",
            {"wait_approval": "wait_approval", "execute": "execute"},
        )
        graph.add_edge("wait_approval", "execute")
        graph.add_edge("execute", END)

        return graph.compile()

    async def build_knowledge_base(self, state: AgentState) -> AgentState:
        """
        自主学习阶段：构建店铺知识库
        包含商品详情、历史FAQ、平台规则
        """
        # TODO: RPA抓取店铺所有商品详情
        # TODO: RPA抓取历史客服记录（近90天）
        # TODO: RPA抓取平台规则（退货政策、发货时效等）
        # TODO: Agnes AI提炼FAQ
        # TODO: 存入知识库

        state["input_data"]["knowledge_base_built"] = True
        state["input_data"]["kb_updated_at"] = datetime.now().isoformat()
        return state

    async def analyze_and_reply(self, state: AgentState) -> AgentState:
        """分析买家消息并生成回复"""
        message = state["input_data"].get("buyer_message", "")
        if not message:
            state["errors"].append({"error": "没有买家消息", "timestamp": datetime.now().isoformat()})
            return state

        # 情绪分析
        sentiment_response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "user", "content": self.SENTIMENT_ANALYSIS_PROMPT.format(message=message)}
            ],
        )

        import json

        try:
            sentiment = json.loads(sentiment_response.choices[0].message.content)
        except (json.JSONDecodeError, AttributeError):
            sentiment = {"sentiment": "neutral", "score": 0.0, "confidence": 0.5, "needs_escalation": False}

        # 负面情绪 + 投诉关键词 → 需要人工介入
        if sentiment.get("score", 0) < -0.7 or sentiment.get("needs_escalation", False):
            state["actions"].append({
                "type": "escalate_to_human",
                "message": message,
                "reason": "情绪负面或涉及投诉",
                "draft_reply": await self._generate_empathy_reply(message),
                "risk_level": "high",
            })
            state["requires_approval"] = True
            return state

        # 正常问题 → AI自动回复
        kb = state["input_data"].get("knowledge_base", {})
        reply_response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": self.CS_SYSTEM_PROMPT.format(kb=str(kb)),
                },
                {"role": "user", "content": message},
            ],
        )

        reply = reply_response.choices[0].message.content if hasattr(reply_response, "choices") else ""

        state["actions"].append({
            "type": "auto_reply",
            "reply": reply,
            "buyer_message": message,
            "sentiment": sentiment.get("sentiment", "neutral"),
            "confidence": sentiment.get("confidence", 0.5),
            "risk_level": "low",
        })
        state["decisions"].append({
            "action": "auto_reply",
            "reply": reply,
            "sentiment": sentiment,
        })
        return state

    async def _generate_empathy_reply(self, message: str) -> str:
        """生成共情回复草稿"""
        response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的客服主管。生成一句表达理解和歉意的回复，引导用户联系人工客服。",
                },
                {"role": "user", "content": message},
            ],
        )
        return response.choices[0].message.content if hasattr(response, "choices") else ""

    async def _execute_action(self, action: dict) -> dict:
        """执行客服动作"""
        action_type = action.get("type")
        if action_type == "auto_reply":
            # TODO: RPA执行自动回复
            return {"status": "replied", "action": action}
        elif action_type == "escalate_to_human":
            # TODO: 推送人工客服处理
            return {"status": "escalated", "action": action}
        return {"status": "unknown_action"}
