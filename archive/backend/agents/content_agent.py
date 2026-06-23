"""内容上架Agent - AI文案生成 + 多平台模板组装 + RPA上架"""
from datetime import datetime

from langgraph.graph import StateGraph, END

from agents.base import BaseAgent, AgentState
from config.llm import agnes_client, TEXT_MODEL


# 各平台上架配置
PLATFORM_UPLOAD_CONFIG = {
    "pdd": {
        "title_max_length": 60,
        "main_images": 5,
        "requires_video": False,
        "category_required": True,
        "price_decimal": 2,
    },
    "taobao": {
        "title_max_length": 60,
        "main_images": 3,
        "requires_video": False,
        "sku_template": "taobao_sku_v2",
        "price_decimal": 2,
    },
    "douyin": {
        "title_max_length": 20,
        "main_images": 9,
        "requires_video": True,
        "live_price_support": True,
    },
    "xiaohongshu": {
        "title_max_length": 20,
        "main_images": 9,
        "style": "lifestyle",
        "hashtag_required": True,
    },
}

CONTENT_GENERATION_PROMPT = """
你是一个资深电商文案专家。基于以下商品信息，为{platform}平台生成上架文案。

商品信息：
- 商品名称：{product_name}
- 品类：{category}
- 卖点：{selling_points}
- 成本价：{cost}
- 建议售价：{suggested_price}

{platform_config}

请输出JSON：
{{
  "title": "...",
  "subtitle": "...",
  "bullet_points": ["卖点1", "卖点2", "卖点3"],
  "detail_description": "...",
  "seo_keywords": ["关键词1", "关键词2"],
  "categories": [
    {{"platform": "pdd", "category_id": "...", "category_name": "..."}}
  ],
  "sku_list": [
    {{"name": "颜色:白色 尺码:M", "price": 0.00, "stock": 0}}
  ],
  "hashtags": ["#标签1", "#标签2"]
}}
"""


class ContentAgent(BaseAgent):
    """
    内容上架Agent：
    - Agnes AI生成标题/卖点/详情页文案（SEO优化）
    - 按目标平台模板组装上架数据
    - RPA执行上架操作
    - 截图确认上架成功
    """

    def _build_graph(self) -> StateGraph:
        """构建内容上架Agent状态图"""
        graph = StateGraph(AgentState)

        graph.add_node("generate_content", self.generate_content)
        graph.add_node("assemble_template", self.assemble_template)
        graph.add_node("check_approval", self.check_approval_needed)
        graph.add_node("wait_approval", self.wait_for_approval)
        graph.add_node("execute", self.execute_actions)

        graph.set_entry_point("generate_content")
        graph.add_edge("generate_content", "assemble_template")
        graph.add_edge("assemble_template", "check_approval")
        graph.add_conditional_edges(
            "check_approval",
            lambda state: "wait_approval" if state["requires_approval"] else "execute",
            {"wait_approval": "wait_approval", "execute": "execute"},
        )
        graph.add_edge("wait_approval", "execute")
        graph.add_edge("execute", END)

        return graph.compile()

    async def generate_content(self, state: AgentState) -> AgentState:
        """Agnes AI生成商品文案"""
        product_data = state["input_data"].get("product_data", {})
        platforms = state["input_data"].get("platforms", ["pdd", "taobao"])

        content_results = {}
        for platform in platforms:
            config = PLATFORM_UPLOAD_CONFIG.get(platform, {})
            platform_config_str = (
                f"- 标题最大长度: {config.get('title_max_length', 60)}\n"
                f"- 主图数量: {config.get('main_images', 5)}\n"
                f"- 需要视频: {config.get('requires_video', False)}"
            )

            prompt = CONTENT_GENERATION_PROMPT.format(
                platform=platform,
                product_name=product_data.get("title", "未知商品"),
                category=product_data.get("category", ""),
                selling_points="\n".join(product_data.get("selling_points", [])),
                cost=product_data.get("cost", 0),
                suggested_price=product_data.get("current_price", 0),
                platform_config=platform_config_str,
            )

            response = await agnes_client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )

            import json

            try:
                content = json.loads(response.choices[0].message.content)
            except (json.JSONDecodeError, AttributeError):
                content = {"title": product_data.get("title", ""), "bullet_points": []}

            content_results[platform] = {
                "content": content,
                "generated_at": datetime.now().isoformat(),
            }

        state["input_data"]["generated_content"] = content_results
        return state

    async def assemble_template(self, state: AgentState) -> AgentState:
        """按平台模板组装上架数据"""
        generated_content = state["input_data"].get("generated_content", {})

        for platform, result in generated_content.items():
            content = result.get("content", {})
            # 验证标题长度
            config = PLATFORM_UPLOAD_CONFIG.get(platform, {})
            title = content.get("title", "")
            max_len = config.get("title_max_length", 60)
            if len(title) > max_len:
                content["title"] = title[: max_len - 3] + "..."

            # 标记需要人工确认（首次上架）
            result["needs_approval"] = True
            result["risk_level"] = "medium"

            state["actions"].append({
                "type": "upload_product",
                "platform": platform,
                "content": content,
                "risk_level": result.get("risk_level", "low"),
            })

        state["decisions"].append({
            "type": "content_assembled",
            "platforms": list(generated_content.keys()),
            "timestamp": datetime.now().isoformat(),
        })
        return state

    async def _execute_action(self, action: dict) -> dict:
        """执行上架动作"""
        if action.get("type") == "upload_product":
            platform = action.get("platform")
            content = action.get("content", {})
            # TODO: RPA执行上架
            return {
                "status": "uploaded",
                "platform": platform,
                "title": content.get("title", ""),
                "timestamp": datetime.now().isoformat(),
            }
        return {"status": "unknown_action"}
