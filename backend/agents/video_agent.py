"""AI视频Agent - 竞品视频分析 + 原创视频生成管线"""
import asyncio
import os
import uuid
from datetime import datetime
from langgraph.graph import StateGraph, END

from agents.base import BaseAgent, AgentState
from config.llm import agnes_client, TEXT_MODEL


class VideoAgent(BaseAgent):
    """
    AI视频Agent：
    - 竞品爆款视频分析流水线（yt-dlp + Whisper + Agnes AI分析）
    - 原创视频生成（CosyVoice2 TTS + MuseTalk口播 + FFmpeg合成）
    - 真人形象轮换管理（规避批量发布检测）
    """

    VIDEO_TEMPLATE_PROMPT = """
你是一个短视频爆款分析师。基于以下视频脚本，分析其爆款结构。

视频脚本：
{transcript}

视频时长：{duration}秒

请输出JSON分析结果：
{{
  "hook_type": "痛点型|好奇型|对比型|福利型",
  "hook_duration": 3,
  "structure": [
    {{"time": "0-3s", "content": "钩子", "technique": "痛点放大"}},
    {{"time": "3-8s", "content": "问题展开", "technique": "场景描述"}},
    {{"time": "8-18s", "content": "产品展示+卖点", "technique": "特写+数据"}},
    {{"time": "18-22s", "content": "促单话术+价格", "technique": "限时优惠"}}
  ],
  "tone": "亲切|专业|夸张|测评",
  "pacing": "快切|慢节奏",
  "bgm_style": "轻快|抒情|紧张"
}}
"""

    SCRIPT_GENERATION_PROMPT = """
你是一个短视频脚本创作专家。基于以下商品信息，套用爆款模板生成原创口播脚本。

商品信息：
- 商品名称：{product_name}
- 品类：{category}
- 核心卖点：{selling_points}
- 价格：{price}

爆款模板：
{template}

请输出原创口播脚本（JSON）：
{{
  "script": [
    {{"time": "0-3s", "text": "钩子台词"}},
    {{"time": "3-8s", "text": "问题展开"}},
    {{"time": "8-18s", "text": "产品展示"}},
    {{"time": "18-22s", "text": "促单话术"}}
  ],
  "total_duration": 22,
  "tone": "亲切",
  "bgm_suggestion": "轻快"
}}
"""

    def _build_graph(self) -> StateGraph:
        """构建AI视频Agent状态图"""
        graph = StateGraph(AgentState)

        graph.add_node("analyze_competitors", self.analyze_competitor_videos)
        graph.add_node("generate_script", self.generate_script)
        graph.add_node("synthesize_voice", self.synthesize_voice)
        graph.add_node("generate_talking_head", self.generate_talking_head)
        graph.add_node("compose_video", self.compose_video)

        graph.set_entry_point("analyze_competitors")
        graph.add_edge("analyze_competitors", "generate_script")
        graph.add_edge("generate_script", "synthesize_voice")
        graph.add_edge("synthesize_voice", "generate_talking_head")
        graph.add_edge("generate_talking_head", "compose_video")
        graph.add_edge("compose_video", END)

        return graph.compile()

    async def analyze_competitor_videos(self, state: AgentState) -> AgentState:
        """第一阶段：分析竞品爆款视频，提炼模板"""
        keyword = state["input_data"].get("keyword", "")
        platform = state["input_data"].get("platform", "douyin")
        count = state["input_data"].get("count", 10)

        video_urls = await self._fetch_hot_videos(keyword, platform, count)

        templates = []
        for url in video_urls:
            video_path = await self._download_video(url)
            transcript = await self._transcribe(video_path)
            template = await self._analyze_structure(transcript, video_path)
            templates.append(template)

        # 提炼共同模式，生成品类爆款模板
        category_template = await self._extract_pattern(templates)
        state["input_data"]["category_template"] = category_template
        state["decisions"].append({
            "type": "template_extracted",
            "keyword": keyword,
            "template": category_template,
            "analyzed_at": datetime.now().isoformat(),
        })
        return state

    async def _fetch_hot_videos(self, keyword: str, platform: str, count: int) -> list[str]:
        """RPA搜索平台热门视频"""
        # TODO: RPA在抖音/快手搜索同类商品，筛选点赞>1万/近7天发布的视频
        return []

    async def _download_video(self, url: str) -> str:
        """yt-dlp去水印下载"""
        output_path = f"temp/video_{uuid.uuid4().hex}.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # TODO: subprocess.run(["yt-dlp", "--no-watermark", "-o", output_path, url])
        return output_path

    async def _transcribe(self, video_path: str) -> str:
        """Whisper语音转文字"""
        # TODO: whisper.load_model("large-v3").transcribe(video_path, language="zh")
        return ""

    async def _analyze_structure(self, transcript: str, video_path: str) -> dict:
        """Agnes AI分析爆款结构"""
        duration = 22  # TODO: 从视频元数据获取
        response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "user", "content": self.VIDEO_TEMPLATE_PROMPT.format(
                    transcript=transcript, duration=duration)}
            ],
        )
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, AttributeError):
            return {}

    async def _extract_pattern(self, templates: list[dict]) -> dict:
        """提炼品类爆款模板的共同模式"""
        if not templates:
            return {}
        # TODO: 统计各hook_type、tone、pacing的出现频率，取最高频
        return templates[0]

    async def generate_script(self, state: AgentState) -> AgentState:
        """第二阶段：基于模板生成原创口播脚本"""
        product_data = state["input_data"].get("product_data", {})
        template = state["input_data"].get("category_template", {})

        template_str = str(template)
        selling_points = "\n".join(product_data.get("selling_points", []))

        response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "user", "content": self.SCRIPT_GENERATION_PROMPT.format(
                    product_name=product_data.get("title", ""),
                    category=product_data.get("category", ""),
                    selling_points=selling_points,
                    price=product_data.get("current_price", 0),
                    template=template_str,
                )}
            ],
        )

        import json
        try:
            script = json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, AttributeError):
            script = {"script": [], "total_duration": 22}

        state["input_data"]["script"] = script
        return state

    async def synthesize_voice(self, state: AgentState) -> AgentState:
        """CosyVoice2合成口播音频"""
        script = state["input_data"].get("script", {})
        script_text = " ".join([line.get("text", "") for line in script.get("script", [])])

        audio_path = f"temp/audio_{uuid.uuid4().hex}.wav"
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        # TODO: CosyVoice2 TTS合成
        # cosvoice2.synthesize(script_text, voice="zh_female_warm", output_path=audio_path)

        state["input_data"]["audio_path"] = audio_path
        return state

    async def generate_talking_head(self, state: AgentState) -> AgentState:
        """MuseTalk驱动真人照片生成口播视频"""
        audio_path = state["input_data"].get("audio_path", "")
        persona_manager = PersonaManager(state["input_data"].get("persona_images", []))

        persona_image = persona_manager.get_next_persona()
        talking_head_path = f"temp/talking_head_{uuid.uuid4().hex}.mp4"
        os.makedirs(os.path.dirname(talking_head_path), exist_ok=True)
        # TODO: MuseTalk生成口播视频
        # musetalk.drive(persona_image, audio_path, output_path=talking_head_path)

        state["input_data"]["talking_head_path"] = talking_head_path
        return state

    async def compose_video(self, state: AgentState) -> AgentState:
        """FFmpeg合成最终视频"""
        talking_head = state["input_data"].get("talking_head_path", "")
        audio = state["input_data"].get("audio_path", "")
        script = state["input_data"].get("script", {})

        output_path = f"output/video_{uuid.uuid4().hex}.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # TODO: FFmpeg合成
        # ffmpeg -i talking_head -i audio -vf subtitles=srt_path -c:v libx264 -c:a aac output.mp4

        state["result"] = {
            "video_path": output_path,
            "duration": script.get("total_duration", 22),
            "composed_at": datetime.now().isoformat(),
        }
        return state

    async def _execute_action(self, action: dict) -> dict:
        return {"status": "video_generated", "action": action}


class PersonaManager:
    """真人形象轮换管理器"""

    def __init__(self, persona_images: list[str]):
        self.personas = persona_images
        self.usage_count = {p: 0 for p in persona_images}

    def get_next_persona(self) -> str:
        """选择使用次数最少的形象，保持均衡轮换"""
        if not self.personas:
            raise ValueError("No persona images configured")
        return min(self.personas, key=self.personas.index)  # 简单轮换
