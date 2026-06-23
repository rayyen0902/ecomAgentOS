# 多Agent电商自主运营系统
# 完整开发文档

**版本：** v1.0  
**文档性质：** 完整技术开发文档（可直接用于开发交付）  
**最后更新：** 2025年  

---

## 文档说明

本文档整合了系统从产品设计到技术实现的全部内容，可直接作为开发团队的交付物使用。

**文档结构：**

| 章节 | 内容 | 用途 |
|------|------|------|
| 第一部分 | 产品与系统架构 | 产品经理/架构师参考 |
| 第二部分 | 数据库设计 | 后端开发/DBA参考 |
| 第三部分 | API接口文档 | 前后端开发参考 |
| 第四部分 | Agent详细设计 | AI/后端开发参考 |
| 第五部分 | RPA平台操作手册 | RPA开发参考 |
| 第六部分 | 部署运维手册 | 运维/DevOps参考 |

**技术栈总览：**

| 层级 | 技术选型 |
|------|---------|
| 桌面端 | Tauri2 + Rust |
| 手机端 | PWA（浏览器快捷方式） |
| 服务端 | Python + FastAPI |
| Agent编排 | LangGraph |
| LLM | Agnes AI API（OpenAI兼容） |
| RPA主力 | Playwright + playwright-stealth |
| RPA备选 | DrissionPage |
| 图片生成 | ComfyUI + Stable Diffusion XL |
| 视频生成 | Whisper + CosyVoice2 + MuseTalk + FFmpeg |
| 任务队列 | Celery + Redis |
| 主数据库 | PostgreSQL |
| 本地缓存 | SQLite |
| 虚拟机微信 | QEMU |

---

---

# 第一部分：产品与系统架构


**版本：** v1.0  
**定位：** 商业产品级，面向交付  
**目标客户：** 多平台电商运营团队（5人 → 扩展至30+店铺管理能力）

---

## 一、项目背景与目标

### 1.1 现状

客户现有5人团队，管理11个店铺（2个抖音小店、2个淘宝、6个拼多多、1个小红书），品类以百货和化妆品为主，选品策略跟随热点灵活切换。

| 角色 | 当前工作方式 |
|------|------------|
| 选品专员 | 人工刷平台、看销量，经验判断 |
| 客服专员 | 全天候手动回复，无法覆盖夜间 |
| 广告专员 | 手动调整出价，凭感觉优化 |
| 货源对接 | 微信/电话联系供应商，手动确认 |
| 库房管理 | 手动处理发货，跟踪物流 |

### 1.2 目标

**不是替代这5个人，而是让5个人能管理30+店铺。**

每个人的工作模式从"手工操作"升级为"审批决策 + 异常处理"，系统负责7×24小时的日常运营执行。

### 1.3 核心约束

- **全RPA执行**：不接入任何电商平台官方API，所有操作通过浏览器自动化实现，规避授权壁垒与政策风险
- **商业产品级**：非MVP，需要完整的错误处理、日志、审批流、监控告警
- **本地优先**：桌面端本地运行RPA，数据安全可控

---

## 二、系统总体架构

### 2.1 架构分层

```
┌─────────────────────────────────────────────────────────┐
│                    交互层                                 │
│  桌面端（Tauri2+Rust）        手机端（PWA Web）           │
│  ·店铺管理  ·任务监控          ·审批通知  ·自然语言指令    │
└─────────────────┬───────────────────────┬───────────────┘
                  │ WebSocket / HTTP       │
┌─────────────────▼───────────────────────▼───────────────┐
│                    服务端（FastAPI + Python）              │
│  ·API网关  ·认证鉴权  ·WebSocket推送  ·业务逻辑层         │
└──────┬──────────┬──────────┬────────────┬───────────────┘
       │          │          │            │
┌──────▼──┐ ┌────▼────┐ ┌───▼────┐ ┌────▼──────────────┐
│ Agent层  │ │任务队列  │ │RPA引擎 │ │   数据存储层       │
│LangGraph│ │Celery+  │ │Play-   │ │PostgreSQL         │
│多Agent  │ │Redis    │ │wright  │ │Redis缓存           │
│编排     │ │         │ │DrissionP│ │SQLite(本地)        │
└──────┬──┘ └────┬────┘ └───┬────┘ └───────────────────┘
       │         │           │
       └─────────▼───────────┘
              Agnes AI API
        （文本/图像/视频生成）
```

### 2.2 核心设计原则

**人机协作闭环**：Agent决策 → 高风险操作推送人工审批 → 人工确认/修改 → RPA执行 → 结果反馈Agent

**异步任务驱动**：所有RPA操作均为异步任务，支持优先级、重试、超时、人工介入

**多浏览器并发**：每个店铺独立浏览器实例，互不干扰，支持同时操作11+个店铺

**全链路可观测**：每次RPA操作截图存档，操作日志完整记录，异常实时告警

---

## 三、技术栈详细说明

### 3.1 完整技术选型

| 层级 | 技术 | 版本/说明 |
|------|------|---------|
| 桌面端 | Tauri2 + Rust | 跨平台桌面应用，调用本地RPA |
| 手机端 | PWA（浏览器快捷方式） | 无需安装App，审批+自然语言指令 |
| 服务端框架 | FastAPI + Python | 异步HTTP + WebSocket |
| Agent编排 | LangGraph | 图结构多Agent状态管理 |
| LLM | Agnes AI API | OpenAI兼容，文本/图像/视频 |
| RPA主力 | Playwright + playwright-stealth | 反检测浏览器自动化 |
| RPA备选 | DrissionPage | 针对国内电商平台的专项适配 |
| 任务队列 | Celery + Redis | 异步任务调度、重试、定时 |
| 主数据库 | PostgreSQL | 店铺/商品/订单/Agent决策记录 |
| 缓存 | Redis | 任务队列 + 热数据缓存 |
| 本地缓存 | SQLite | Tauri桌面端本地数据 |
| 虚拟机微信 | QEMU/VirtualBox内置 | 微信登录隔离，RPA控制发消息 |
| 消息推送 | WebSocket（FastAPI原生） | 实时推送审批通知到手机端 |
| 图像生成 | Agnes AI图像API | 商品主图、场景图生成 |
| 视频生成 | Agnes AI视频API | 商品展示短视频生成 |

### 3.2 Agnes AI API接入配置

```python
# config/llm.py
from openai import AsyncOpenAI

agnes_client = AsyncOpenAI(
    api_key="YOUR_AGNES_API_KEY",
    base_url="https://apihub.agnes-ai.com/v1"
)

# 文本模型：用于Agent推理、客服回复、文案生成
TEXT_MODEL = "agnes-2.0-flash"

# 图像模型：用于商品主图生成
IMAGE_MODEL = "agnes-image-v1"  # 以实际文档为准

# 视频模型：用于商品展示视频
VIDEO_MODEL = "agnes-video-v1"  # 以实际文档为准
```

---

## 四、店铺管理模块

### 4.1 店铺接入流程

用户操作路径：**添加店铺 → 选择平台 → 扫码登录 → 绑定成功**

```
用户点击「添加店铺」
    ↓
选择平台（抖音/淘宝/拼多多/小红书）
    ↓
系统启动独立Playwright浏览器实例
    ↓
打开平台登录页，显示二维码
    ↓
用户手机扫码登录
    ↓
系统检测登录态Cookie，保存加密存储
    ↓
绑定成功，店铺加入管理列表
```

### 4.2 店铺数据模型

```sql
-- 店铺表
CREATE TABLE shops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,           -- 店铺名称
    platform VARCHAR(20) NOT NULL,        -- douyin/taobao/pdd/xiaohongshu
    platform_shop_id VARCHAR(100),        -- 平台店铺ID（RPA抓取）
    cookies JSONB,                        -- 加密存储登录态
    cookie_expires_at TIMESTAMP,          -- Cookie过期时间
    status VARCHAR(20) DEFAULT 'active',  -- active/paused/error
    config JSONB,                         -- 店铺个性化配置
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 平台适配器表（记录各平台页面选择器版本）
CREATE TABLE platform_adapters (
    platform VARCHAR(20) PRIMARY KEY,
    version VARCHAR(20),
    selectors JSONB,    -- 页面元素选择器
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4.3 多浏览器并发管理

```python
# rpa/browser_pool.py
class BrowserPool:
    """
    每个店铺维护独立的浏览器上下文
    支持并发操作多个店铺，互不干扰
    """
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.contexts: Dict[str, BrowserContext] = {}  # shop_id -> context

    async def get_context(self, shop_id: str) -> BrowserContext:
        if shop_id not in self.contexts:
            context = await self.browser.new_context(
                **STEALTH_CONFIG,           # 反检测配置
                storage_state=await self.load_cookies(shop_id)
            )
            await stealth_async(context)    # playwright-stealth注入
            self.contexts[shop_id] = context
        return self.contexts[shop_id]

    async def execute(self, shop_id: str, task_func, *args):
        context = await self.get_context(shop_id)
        page = await context.new_page()
        try:
            result = await task_func(page, *args)
            await self.save_cookies(shop_id, context)  # 刷新Cookie
            return result
        except Exception as e:
            await page.screenshot(path=f"logs/error_{shop_id}_{timestamp()}.png")
            raise
        finally:
            await page.close()
```

---

## 五、Agent编排架构

### 5.1 LangGraph多Agent设计

系统包含8个专职Agent，由一个Orchestrator统一调度，通过LangGraph图结构管理状态和依赖。

```
OrchestratorAgent（调度中枢）
    ├── SelectionAgent      选品Agent
    ├── PricingAgent        定价Agent  
    ├── InventoryAgent      库存Agent
    ├── AdsAgent            广告Agent
    ├── CustomerServiceAgent 客服Agent
    ├── ContentAgent        内容上架Agent
    ├── ImageAgent          AI作图Agent
    └── VideoAgent          AI视频Agent
```

### 5.2 Agent基类设计

```python
# agents/base.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    shop_id: str
    task_type: str
    input_data: dict
    decisions: Annotated[list, operator.add]   # 决策记录
    actions: Annotated[list, operator.add]     # 待执行动作
    requires_approval: bool                     # 是否需要人工审批
    approval_status: str                        # pending/approved/rejected
    result: dict
    errors: Annotated[list, operator.add]

class BaseAgent:
    def __init__(self, shop_id: str, llm_client):
        self.shop_id = shop_id
        self.llm = llm_client
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        raise NotImplementedError

    async def analyze(self, state: AgentState) -> AgentState:
        """LLM推理决策"""
        raise NotImplementedError

    async def check_approval_needed(self, state: AgentState) -> AgentState:
        """判断是否需要人工审批"""
        # 高风险操作：大幅改价、批量下架、大额广告预算调整
        risk_actions = [a for a in state["actions"] if a.get("risk_level") == "high"]
        state["requires_approval"] = len(risk_actions) > 0
        return state

    async def wait_for_approval(self, state: AgentState) -> AgentState:
        """推送审批通知，等待人工响应"""
        # 通过WebSocket推送到手机端
        await push_approval_request(self.shop_id, state)
        # 写入数据库等待审批（异步，不阻塞）
        await create_approval_task(state)
        return state
```

### 5.3 Orchestrator调度逻辑

```python
# agents/orchestrator.py
class OrchestratorAgent:
    """
    调度中枢：决定何时触发哪个Agent
    基于事件驱动 + 定时触发双模式
    """
    
    # 定时任务配置
    SCHEDULED_TASKS = {
        "selection_scan":     "0 8 * * *",      # 每天8点选品巡检
        "price_check":        "*/15 * * * *",    # 每15分钟竞品价格检查
        "ads_optimization":   "0 */2 * * *",     # 每2小时广告优化
        "inventory_check":    "0 9,18 * * *",    # 每天9点和18点库存检查
        "order_process":      "*/5 * * * *",     # 每5分钟处理新订单
    }

    async def route(self, event: dict) -> str:
        """根据事件类型路由到对应Agent"""
        event_type = event.get("type")
        routing = {
            "new_order":          "inventory",
            "competitor_price_drop": "pricing",
            "low_stock":          "inventory",
            "negative_review":    "customer_service",
            "user_command":       self._parse_user_intent(event),
        }
        return routing.get(event_type, "orchestrator")

    async def _parse_user_intent(self, event: dict) -> str:
        """
        解析手机端自然语言指令
        例："帮我把拼多多3店的连衣裙降价10%"
             → routing to pricing agent for pdd_shop_3
        """
        response = await self.llm.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": INTENT_PARSE_PROMPT},
                {"role": "user", "content": event["message"]}
            ]
        )
        return parse_intent(response.choices[0].message.content)
```

---

## 六、核心功能模块详细设计

### 6.1 选品模块（SelectionAgent）

**数据来源**：1688（主力）+ 各电商平台热销榜（RPA抓取）

**工作流程**：

```
1688 RPA抓取
    ↓
抓取热销商品数据（销量/价格/起订量/货期/供货商评分）
    ↓
SelectionAgent分析
    ↓
Agnes AI推理：
  · 该品类在各平台的竞争烈度
  · 利润空间预估（1688成本 vs 平台均价）
  · 跟这家店铺历史爆款的相关度
  · 季节性/趋势性评分
    ↓
生成选品报告（带评分和推荐理由）
    ↓
推送到手机端供运营确认
    ↓
确认后触发：ContentAgent上架 + ImageAgent生成主图
```

**RPA抓取关键点**：

```python
# rpa/platforms/alibaba_1688.py
class Alibaba1688Scraper:
    async def search_hot_products(self, keyword: str, page: Page) -> list:
        await page.goto(f"https://s.1688.com/selloffer/offer_search.htm?keywords={keyword}")
        await page.wait_for_load_state("networkidle")
        
        # 模拟人类滚动行为
        await human_scroll(page)
        
        products = await page.evaluate("""
            () => [...document.querySelectorAll('.offer-list-row')]
                .map(el => ({
                    title: el.querySelector('.title')?.textContent,
                    price: el.querySelector('.price')?.textContent,
                    monthly_sales: el.querySelector('.sale-count')?.textContent,
                    supplier_score: el.querySelector('.supplier-score')?.textContent,
                    min_order: el.querySelector('.min-order')?.textContent,
                    url: el.querySelector('a')?.href
                }))
        """)
        return products
    
    async def get_supplier_detail(self, url: str, page: Page) -> dict:
        """获取供应商详情：产能、发货速度、质检报告"""
        await page.goto(url)
        # ... 详情页数据抓取
```

**跨平台可行性分析Prompt**：

```python
SELECTION_ANALYSIS_PROMPT = """
你是一个资深电商选品顾问。基于以下1688商品数据，分析该商品在各电商平台的销售可行性。

商品数据：{product_data}
店铺历史爆款：{shop_history}
当前平台竞品数据：{competitor_data}

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
  "recommendation": "强烈推荐/推荐/观望/不推荐"
}}
"""
```

### 6.2 定价模块（PricingAgent）

**核心能力**：实时跟踪竞品价格，自动触发调价，保护利润底线

```python
# agents/pricing_agent.py
class PricingAgent(BaseAgent):
    
    PRICING_RULES = {
        "follow_competitor":   {"trigger": "competitor drops price", "action": "match or undercut by 1-3%"},
        "protect_margin":      {"min_margin": 0.15, "action": "never price below cost * 1.15"},
        "promotion_window":    {"platform_activity": True, "action": "join auto with approval"},
        "slow_moving":         {"no_sale_days": 7, "action": "drop 5% per cycle, max 20%"},
    }

    async def analyze(self, state: AgentState) -> AgentState:
        competitor_prices = state["input_data"]["competitor_prices"]
        current_price = state["input_data"]["current_price"]
        cost = state["input_data"]["cost"]
        
        prompt = PRICING_PROMPT.format(
            current_price=current_price,
            competitor_prices=competitor_prices,
            cost=cost,
            rules=self.PRICING_RULES,
            shop_strategy=state["input_data"].get("shop_strategy", "balanced")
        )
        
        response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        
        decision = parse_json(response.choices[0].message.content)
        
        # 价格变动超过15%需要审批
        price_change_pct = abs(decision["new_price"] - current_price) / current_price
        if price_change_pct > 0.15:
            decision["risk_level"] = "high"
        
        state["decisions"].append(decision)
        state["actions"].append({
            "type": "update_price",
            "shop_id": self.shop_id,
            "product_id": state["input_data"]["product_id"],
            "new_price": decision["new_price"],
            "risk_level": decision.get("risk_level", "low")
        })
        return state
```

### 6.3 智能客服模块（CustomerServiceAgent）

**设计要点**：自主学习商品知识 + 平台规则，处理常见问题，复杂情况转人工

**知识库构建**：

```python
# agents/customer_service_agent.py
class CustomerServiceAgent(BaseAgent):
    
    async def build_knowledge_base(self, shop_id: str):
        """
        自主学习阶段：RPA抓取店铺所有商品详情、
        历史FAQ、平台规则，构建知识库
        """
        # 1. 抓取所有在售商品详情
        products = await self.rpa.get_all_products(shop_id)
        
        # 2. 抓取历史客服记录（近90天）
        chat_history = await self.rpa.get_chat_history(shop_id, days=90)
        
        # 3. 抓取平台规则（退货政策、发货时效等）
        platform_rules = await self.rpa.get_platform_rules(shop_id)
        
        # 4. Agnes AI提炼FAQ
        faq = await self.extract_faq(products, chat_history, platform_rules)
        
        # 5. 存入知识库
        await self.save_knowledge_base(shop_id, {
            "products": products,
            "faq": faq,
            "platform_rules": platform_rules,
            "updated_at": now()
        })

    async def handle_message(self, message: str, shop_id: str, buyer_id: str) -> dict:
        """处理买家消息"""
        
        # 加载该店铺知识库
        kb = await self.load_knowledge_base(shop_id)
        
        # 情绪分析
        sentiment = await self.analyze_sentiment(message)
        
        # 负面情绪 + 投诉关键词 → 直接转人工
        if sentiment["score"] < -0.7 or self.has_complaint_keywords(message):
            return {
                "action": "escalate_to_human",
                "reason": "情绪负面或涉及投诉",
                "draft_reply": await self.generate_empathy_reply(message)
            }
        
        # 正常问题 → AI回复
        reply = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": CS_SYSTEM_PROMPT.format(kb=kb)},
                {"role": "user", "content": message}
            ]
        )
        
        return {
            "action": "auto_reply",
            "reply": reply.choices[0].message.content,
            "confidence": sentiment["confidence"]
        }
```

### 6.4 内容上架模块（ContentAgent）

**全自动上架流程**：

```
接收商品信息（来自选品Agent或人工输入）
    ↓
Agnes AI生成：标题/卖点/详情页文案（SEO优化）
    ↓
调用ImageAgent生成主图（3-5张）
    ↓
调用VideoAgent生成展示视频（可选）
    ↓
按目标平台模板组装上架数据
    ↓
生成上架预览 → 推送人工确认（首次上架）
    ↓
RPA执行上架操作
    ↓
截图确认上架成功
    ↓
记录商品ID、上架时间到数据库
```

**多平台差异处理**：

```python
# rpa/platforms/uploader.py
PLATFORM_UPLOAD_CONFIG = {
    "pdd": {
        "title_max_length": 60,
        "main_images": 5,
        "requires_video": False,
        "category_required": True,
        "price_decimal": 2
    },
    "taobao": {
        "title_max_length": 60,
        "main_images": 3,
        "requires_video": False,
        "sku_template": "taobao_sku_v2",
        "price_decimal": 2
    },
    "douyin": {
        "title_max_length": 20,  # 抖音标题极短
        "main_images": 9,
        "requires_video": True,   # 抖音强烈建议视频
        "live_price_support": True
    },
    "xiaohongshu": {
        "title_max_length": 20,
        "main_images": 9,
        "style": "lifestyle",     # 小红书需要生活方式风格图
        "hashtag_required": True
    }
}
```

### 6.5 AI作图模块（ImageAgent）

```python
# agents/image_agent.py
class ImageAgent(BaseAgent):
    
    async def generate_product_images(self, product_data: dict, platform: str) -> list:
        """
        生成商品主图套装
        1. 白底主图（必需）
        2. 场景图（根据品类选择场景）
        3. 卖点图（文字+产品）
        """
        results = []
        
        # 1. 白底主图
        white_bg = await self.generate_image(
            prompt=f"Professional product photo, white background, {product_data['title']}, "
                   f"studio lighting, high quality, e-commerce style",
            style="product_white_bg"
        )
        results.append({"type": "main", "url": white_bg})
        
        # 2. 场景图（根据品类）
        scene_prompt = await self.get_scene_prompt(product_data, platform)
        scene_img = await self.generate_image(prompt=scene_prompt, style="lifestyle")
        results.append({"type": "scene", "url": scene_img})
        
        # 3. 平台特殊要求
        if platform == "xiaohongshu":
            # 小红书风格：ins风、高饱和度
            xhs_img = await self.generate_image(
                prompt=scene_prompt + ", instagram style, vibrant colors, trendy",
                style="xiaohongshu"
            )
            results.append({"type": "xhs_style", "url": xhs_img})
        
        return results

    async def generate_image(self, prompt: str, style: str) -> str:
        response = await agnes_client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size="1024x1024",
            quality="hd"
        )
        return response.data[0].url
```

### 6.6 订单管理与发货模块

**自动发货流程**：

```
新订单检测（RPA每5分钟巡检）
    ↓
订单分类：
  ├── 1688代发 → RPA在1688下单，填写买家收货地址
  ├── 自有库存 → 生成打包单，通知库房
  └── 供应商发货 → 虚拟机微信通知供应商
    ↓
物流单号回填（RPA自动填入平台）
    ↓
发货完成，更新订单状态
```

**虚拟机微信发消息方案**：

```python
# rpa/wechat_vm.py
class WeChatVMController:
    """
    通过QEMU虚拟机控制微信
    虚拟机内运行Windows + 微信PC版
    通过VNC协议控制虚拟机桌面
    """
    
    def __init__(self, vm_config: dict):
        self.vnc_host = vm_config["vnc_host"]
        self.vnc_port = vm_config["vnc_port"]
        self.vnc_password = vm_config["vnc_password"]
    
    async def send_supplier_message(self, supplier_name: str, order_info: dict):
        """发送备货/发货指令给供应商"""
        
        # 生成消息内容
        message = self.format_order_message(order_info)
        
        # 连接VNC控制虚拟机内微信
        async with VNCSession(self.vnc_host, self.vnc_port) as vnc:
            # 搜索联系人
            await vnc.click_search()
            await vnc.type_text(supplier_name)
            await vnc.press_enter()
            
            # 发送消息
            await vnc.click_input_box()
            await vnc.type_text(message)
            await vnc.press_enter()
            
            # 截图确认
            screenshot = await vnc.screenshot()
            await self.save_message_record(supplier_name, message, screenshot)
    
    def format_order_message(self, order_info: dict) -> str:
        return f"""
【新订单备货通知】
订单号：{order_info['order_id']}
商品：{order_info['product_name']} × {order_info['quantity']}
规格：{order_info['spec']}
收货人：{order_info['receiver_name']}
地址：{order_info['address']}
电话：{order_info['phone']}
备注：{order_info.get('note', '无')}
请尽快安排发货，谢谢！
        """.strip()
```

### 6.7 广告投放模块（AdsAgent）

```python
# agents/ads_agent.py
class AdsAgent(BaseAgent):
    """
    广告优化逻辑：
    - 每2小时抓取广告数据（点击/展现/转化/花费）
    - Agnes AI分析ROI，给出调价建议
    - 低ROI关键词降价或暂停
    - 高转化关键词加价扩量
    - 重大调整（预算变动>20%）需人工审批
    """
    
    async def optimize(self, shop_id: str, platform: str) -> dict:
        # RPA抓取广告报表数据
        ads_data = await self.rpa.get_ads_report(shop_id, platform, days=7)
        
        response = await agnes_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{
                "role": "user",
                "content": ADS_OPTIMIZATION_PROMPT.format(
                    ads_data=ads_data,
                    platform=platform,
                    target_roi=2.5  # 目标ROI，可配置
                )
            }]
        )
        
        adjustments = parse_json(response.choices[0].message.content)
        
        # 标记高风险调整
        for adj in adjustments:
            if abs(adj["budget_change_pct"]) > 20:
                adj["risk_level"] = "high"
        
        return adjustments
```

---

## 七、手机端（PWA）设计

### 7.1 核心功能

手机端定位：**移动审批台 + 自然语言指令入口**

主要页面：
- **通知中心**：所有待审批决策、异常告警
- **店铺概览**：各店铺实时数据（销量/在线商品/今日订单）
- **指令输入**：自然语言告诉Agent做什么
- **操作日志**：查看Agent最近执行了什么

### 7.2 审批交互设计

```
Agent发现竞品降价20%，建议跟价
    ↓
WebSocket推送到手机端
    ↓
通知卡片展示：
  ┌─────────────────────────────┐
  │ 🏷️ 定价决策审批             │
  │ 拼多多5店 · 连衣裙爆款款    │
  │                             │
  │ 竞品：¥39.9 → ¥31.9(-20%)  │
  │ 建议：¥42.0 → ¥33.9(-19%)  │
  │ 预估影响：+15%点击，+8%转化  │
  │                             │
  │ [✅ 同意] [✏️ 修改] [❌ 拒绝] │
  └─────────────────────────────┘
    ↓
用户点击「同意」
    ↓
RPA执行改价操作
    ↓
截图回传，通知「改价成功」
```

### 7.3 自然语言指令示例

```
用户输入：「把所有拼多多店的连衣裙降价5%，但不能低于30块」

系统处理：
1. Agnes AI解析意图
2. 识别：平台=拼多多, 品类=连衣裙, 操作=降价5%, 底价=30元
3. Orchestrator路由到PricingAgent
4. PricingAgent生成调价列表
5. 推送预览确认：「将影响6个店铺23个SKU，点击确认执行」
6. 用户确认 → RPA批量执行
```

---

## 八、数据库设计

### 8.1 核心表结构

```sql
-- 商品表
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID REFERENCES shops(id),
    platform_product_id VARCHAR(100),
    title VARCHAR(500),
    category VARCHAR(100),
    cost DECIMAL(10,2),           -- 1688采购成本
    current_price DECIMAL(10,2),
    stock_quantity INTEGER,
    status VARCHAR(20),           -- on_sale/off_shelf/draft
    platform_data JSONB,          -- 各平台专属字段
    created_at TIMESTAMP DEFAULT NOW()
);

-- 任务记录表（所有Agent决策和RPA操作）
CREATE TABLE agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID REFERENCES shops(id),
    agent_type VARCHAR(50),       -- selection/pricing/ads/cs/content/image/video
    task_type VARCHAR(100),
    input_data JSONB,
    decision JSONB,               -- Agent决策内容
    actions JSONB,                -- 待执行动作列表
    status VARCHAR(20),           -- pending_approval/approved/executing/done/failed
    approved_by VARCHAR(100),     -- 审批人
    approved_at TIMESTAMP,
    result JSONB,
    screenshot_urls JSONB,        -- 操作截图
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- 订单表
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID REFERENCES shops(id),
    platform_order_id VARCHAR(100) UNIQUE,
    product_id UUID REFERENCES products(id),
    quantity INTEGER,
    sale_price DECIMAL(10,2),
    buyer_info JSONB,             -- 加密存储买家信息
    logistics_no VARCHAR(100),
    fulfillment_type VARCHAR(20), -- 1688_dropship/self_warehouse/supplier
    status VARCHAR(20),
    created_at TIMESTAMP,
    shipped_at TIMESTAMP
);

-- 竞品价格历史表
CREATE TABLE competitor_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    platform VARCHAR(20),
    competitor_shop VARCHAR(100),
    price DECIMAL(10,2),
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- 审批队列表
CREATE TABLE approval_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_task_id UUID REFERENCES agent_tasks(id),
    shop_id UUID REFERENCES shops(id),
    priority INTEGER DEFAULT 5,   -- 1最高优先级
    title VARCHAR(200),
    description TEXT,
    options JSONB,                -- 可选操作
    expires_at TIMESTAMP,         -- 超时自动处理
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 九、RPA反检测策略

### 9.1 核心反检测配置

```python
# rpa/stealth_config.py
STEALTH_CONFIG = {
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "locale": "zh-CN",
    "timezone_id": "Asia/Shanghai",
    "geolocation": {"longitude": 121.4737, "latitude": 31.2304},  # 上海
    "permissions": ["geolocation"],
    "extra_http_headers": {
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
}

async def human_like_behavior(page: Page):
    """模拟人类操作习惯"""
    # 随机延迟（正态分布，均值1秒）
    await asyncio.sleep(random.gauss(1.0, 0.3))
    
    # 随机鼠标移动
    await page.mouse.move(
        random.randint(100, 800),
        random.randint(100, 600),
        steps=random.randint(5, 15)
    )

async def human_type(page: Page, selector: str, text: str):
    """模拟人类打字速度"""
    await page.click(selector)
    for char in text:
        await page.keyboard.type(char)
        await asyncio.sleep(random.uniform(0.05, 0.2))  # 随机按键间隔
```

### 9.2 平台适配策略

| 平台 | 主要风险 | 应对策略 |
|------|---------|---------|
| 拼多多 | 行为检测激进 | DrissionPage + 强化stealth + 低频操作 |
| 淘宝 | 滑块验证码 | 集成打码平台 + 人工介入备案 |
| 抖音小店 | 操作频率限制 | 随机间隔 + 错峰操作 |
| 小红书 | 内容审核严 | 图片去重处理 + 人工发布首篇 |
| 1688 | 相对宽松 | Playwright标准配置即可 |

### 9.3 异常处理机制

```python
# rpa/error_handler.py
class RPAErrorHandler:
    
    RETRY_CONFIG = {
        "max_retries": 3,
        "backoff_factor": 2,       # 指数退避
        "captcha_action": "pause",  # 遇到验证码暂停等人工
        "ban_action": "rotate_ip",  # 疑似封IP时切换
    }
    
    async def handle_error(self, error: Exception, context: dict):
        if isinstance(error, CaptchaDetectedError):
            # 推送告警到手机端，暂停该店铺操作
            await push_alert(context["shop_id"], "需要人工处理验证码")
            await pause_shop_tasks(context["shop_id"])
            
        elif isinstance(error, LoginExpiredError):
            # Cookie过期，提示重新登录
            await push_alert(context["shop_id"], "店铺登录已过期，请重新扫码")
            
        elif isinstance(error, ElementNotFoundError):
            # 页面结构变更，记录日志并通知开发
            await log_selector_failure(context)
            await notify_dev_team("平台页面结构可能已更新")
```

---

## 十、服务端API设计

### 10.1 主要接口

```
# 店铺管理
POST   /api/shops                    添加店铺
GET    /api/shops                    获取店铺列表
GET    /api/shops/{id}/status        店铺实时状态
DELETE /api/shops/{id}               移除店铺

# Agent任务
POST   /api/tasks                    创建任务（手动触发）
GET    /api/tasks                    任务列表
GET    /api/tasks/{id}               任务详情+截图
PATCH  /api/tasks/{id}/approve       审批任务

# 审批队列
GET    /api/approvals/pending        待审批列表
POST   /api/approvals/{id}/decide    审批决策（approve/reject/modify）

# 自然语言指令
POST   /api/commands/natural         自然语言指令入口

# 商品管理
GET    /api/products                 商品列表
POST   /api/products/upload          触发批量上架
GET    /api/products/{id}/competitors 竞品价格

# 订单管理
GET    /api/orders                   订单列表
POST   /api/orders/{id}/ship         手动触发发货

# WebSocket（实时推送）
WS     /ws/{client_id}              手机端实时连接
```

### 10.2 FastAPI项目结构

```
backend/
├── main.py                  # FastAPI入口
├── config/
│   ├── settings.py          # 环境配置
│   └── llm.py               # Agnes AI客户端
├── api/
│   ├── shops.py
│   ├── tasks.py
│   ├── approvals.py
│   ├── commands.py
│   └── websocket.py
├── agents/
│   ├── base.py              # Agent基类
│   ├── orchestrator.py      # 调度中枢
│   ├── selection_agent.py
│   ├── pricing_agent.py
│   ├── inventory_agent.py
│   ├── ads_agent.py
│   ├── cs_agent.py
│   ├── content_agent.py
│   ├── image_agent.py
│   └── video_agent.py
├── rpa/
│   ├── browser_pool.py      # 浏览器池管理
│   ├── stealth_config.py    # 反检测配置
│   ├── error_handler.py     # 异常处理
│   ├── wechat_vm.py         # 虚拟机微信
│   └── platforms/
│       ├── taobao.py
│       ├── pdd.py
│       ├── douyin.py
│       ├── xiaohongshu.py
│       ├── alibaba_1688.py
│       └── base_platform.py
├── tasks/
│   ├── celery_app.py        # Celery配置
│   ├── scheduled.py         # 定时任务
│   └── rpa_tasks.py         # RPA异步任务
├── models/
│   ├── shop.py
│   ├── product.py
│   ├── order.py
│   └── task.py
└── db/
    ├── database.py          # PostgreSQL连接
    └── migrations/          # Alembic迁移
```

---

## 十一、桌面端（Tauri2）设计

### 11.1 Tauri与服务端通信

桌面端通过本地HTTP调用服务端（同机部署），RPA浏览器进程由服务端Python管理，Tauri负责UI展示和用户操作。

```rust
// src-tauri/src/main.rs
// Tauri主要职责：
// 1. 启动Python服务端子进程
// 2. 提供系统托盘（后台运行）
// 3. 管理SQLite本地缓存
// 4. 系统通知推送

#[tauri::command]
async fn start_backend_service() -> Result<(), String> {
    // 启动Python FastAPI服务
    Command::new("python")
        .args(["-m", "uvicorn", "main:app", "--port", "8765"])
        .spawn()
        .map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
async fn get_local_cache(key: String) -> Result<String, String> {
    // 从SQLite读取本地缓存数据
}
```

### 11.2 桌面端主要页面

```
┌─────────────────────────────────────────────────┐
│  🏪 电商运营中心                    [最小化] [×] │
├──────────┬──────────────────────────────────────┤
│          │                                      │
│ 导航栏   │  主内容区                            │
│          │                                      │
│ 📊 总览  │  店铺状态矩阵（11个店铺实时状态）    │
│ 🏪 店铺  │  今日销售/订单/广告花费汇总          │
│ 📦 商品  │  待处理事项（待审批/待发货/异常）    │
│ 📋 订单  │                                      │
│ 🤖 Agent │  Agent运行日志实时滚动               │
│ ⚙️ 设置  │                                      │
│          │                                      │
└──────────┴──────────────────────────────────────┘
```

---

## 十二、系统部署架构

### 12.1 客户端本地部署（标准配置）

```
客户Windows电脑（推荐配置）：
  CPU: 8核+（多浏览器并发需要）
  内存: 32GB+（11个浏览器实例 + 虚拟机）
  硬盘: SSD 500GB+（截图存档）
  网络: 稳定宽带（RPA操作需要稳定连接）

软件栈：
  ├── Tauri桌面应用（用户界面）
  ├── Python服务端（FastAPI + Celery）
  ├── PostgreSQL（主数据库）
  ├── Redis（任务队列+缓存）
  ├── QEMU虚拟机（微信隔离环境）
  └── Chromium浏览器集群（RPA执行）
```

### 12.2 进程管理

```python
# 使用supervisor管理所有进程
# supervisor.conf

[program:fastapi]
command=uvicorn main:app --host 127.0.0.1 --port 8765
autostart=true
autorestart=true

[program:celery_worker]
command=celery -A tasks.celery_app worker --concurrency=4
autostart=true
autorestart=true

[program:celery_beat]
command=celery -A tasks.celery_app beat
autostart=true
autorestart=true
```

---

## 十三、实施计划

### 第一期（Week 1-4）：基础平台

- Tauri桌面框架搭建
- 店铺扫码登录绑定
- RPA浏览器池基础版
- 拼多多/淘宝平台适配器（优先，SKU最多）
- 服务端框架 + 数据库
- 手机端PWA基础版（通知+审批）

**里程碑**：可以用系统管理店铺，手动触发RPA操作，手机端收到通知

### 第二期（Week 5-8）：核心Agent

- LangGraph Agent框架搭建
- 定价Agent上线（竞品跟价）
- 客服Agent上线（FAQ自动回复）
- 选品Agent上线（1688数据抓取+分析）
- 订单自动发货（1688代发路径）
- Agnes AI文案生成集成

**里程碑**：定价和客服实现70%自动化，选品报告可用

### 第三期（Week 9-12）：完整能力

- AI作图Agent（Agnes图像API）
- AI视频Agent（Agnes视频API）
- 内容上架全自动流水线
- 广告投放Agent
- 虚拟机微信通知供应商
- 抖音小店 + 小红书适配器
- 完整监控看板

**里程碑**：全链路自动化，5人团队可管理25+店铺

---

## 十四、风险与应对

| 风险 | 概率 | 影响 | 应对方案 |
|------|------|------|---------|
| 平台更新页面结构 | 高 | 中 | 适配器版本化管理，监控报警，快速修复机制 |
| 账号触发风控 | 中 | 高 | 人工操作频率上限 + IP隔离 + 快速人工接管 |
| Cookie频繁过期 | 中 | 中 | 自动检测+提前提醒重新登录 |
| Agnes API限流 | 低 | 中 | 请求队列 + 本地缓存重复内容 |
| 虚拟机微信封号 | 中 | 中 | 多备份账号 + 企业微信备选方案 |
| RPA被识别封店 | 低 | 极高 | 严格控制操作频率，核心操作保留人工审批 |

---

## 十五、后续扩展方向

1. **多租户SaaS化**：将本系统产品化，支持多个电商团队订阅使用
2. **数据智能**：积累运营数据后，训练专属选品预测模型
3. **供应链打通**：与1688供应商系统深度集成，实现全链路数字化
4. **直播自动化**：抖音/快手直播场景的自动化（弹幕互动、优惠券发放）

---

*文档版本：v1.0 | 技术方案确认后进入详细设计阶段*

---

## 十六、图片生成模块（升级方案）

### 16.1 技术栈

| 工具 | 用途 | 显存要求 |
|------|------|---------|
| ComfyUI | 工作流编排引擎 | - |
| Stable Diffusion XL | 主图生成 | 8GB+ |
| ControlNet | 参考图姿态/构图控制 | +2GB |
| BiRefNet | 商品抠图（去背景） | 4GB |
| IP-Adapter | 风格一致性控制 | +2GB |

**客户电脑显卡要求：RTX 3060 12GB 以上**

### 16.2 电商图片生产工作流

```
原始商品图（供应商提供）
    ↓
BiRefNet 自动抠图（去背景，输出透明PNG）
    ↓
根据平台/品类选择场景模板：
  · 白底图（淘宝/拼多多标准主图）
  · 生活场景图（小红书/抖音风格）
  · 简约渐变图（通用）
    ↓
ControlNet + SD XL 生成场景图
（ControlNet保证商品主体不变形）
    ↓
IP-Adapter 保持品牌风格一致性
    ↓
输出多尺寸：
  · 800×800（淘宝/拼多多主图）
  · 1080×1080（小红书/抖音）
  · 1080×1440（详情页竖版）
    ↓
Agnes AI 视觉合规检测（违禁词/图片合规）
```

### 16.3 ComfyUI Python API调用

```python
# agents/image_agent.py
import aiohttp
import json

COMFYUI_URL = "http://127.0.0.1:8188"

class ImageAgent(BaseAgent):

    async def generate_product_image(
        self,
        product_image_path: str,
        platform: str,
        style: str = "white_bg"
    ) -> list[str]:
        """
        完整图片生产流水线
        1. BiRefNet抠图
        2. SD XL + ControlNet生成场景图
        3. 输出多平台尺寸
        """
        # 步骤1：抠图
        cutout_path = await self.remove_background(product_image_path)

        # 步骤2：选择工作流模板
        workflow = self.load_workflow(platform, style)
        workflow = self.inject_image(workflow, cutout_path)

        # 步骤3：提交ComfyUI生成
        result_images = await self.run_comfyui_workflow(workflow)

        # 步骤4：输出平台适配尺寸
        return await self.resize_for_platform(result_images, platform)

    async def run_comfyui_workflow(self, workflow: dict) -> list[str]:
        async with aiohttp.ClientSession() as session:
            # 提交工作流
            async with session.post(
                f"{COMFYUI_URL}/prompt",
                json={"prompt": workflow}
            ) as resp:
                data = await resp.json()
                prompt_id = data["prompt_id"]

            # 轮询等待结果
            while True:
                async with session.get(
                    f"{COMFYUI_URL}/history/{prompt_id}"
                ) as resp:
                    history = await resp.json()
                    if prompt_id in history:
                        return self.extract_images(history[prompt_id])
                await asyncio.sleep(1)

    async def remove_background(self, image_path: str) -> str:
        """调用BiRefNet抠图"""
        # BiRefNet本地API（ComfyUI节点内置）
        workflow = self.load_workflow("birefnet_cutout")
        workflow = self.inject_image(workflow, image_path)
        results = await self.run_comfyui_workflow(workflow)
        return results[0]
```

### 16.4 各平台图片规范配置

```python
PLATFORM_IMAGE_CONFIG = {
    "pdd": {
        "main_image": {"size": (800, 800), "bg": "white", "count": 5},
        "style_prompt": "clean white background, professional product photo, studio lighting"
    },
    "taobao": {
        "main_image": {"size": (800, 800), "bg": "white", "count": 3},
        "style_prompt": "clean white background, e-commerce product photo"
    },
    "douyin": {
        "main_image": {"size": (1080, 1080), "bg": "scene", "count": 9},
        "style_prompt": "lifestyle scene, trendy, vibrant colors, young aesthetic"
    },
    "xiaohongshu": {
        "main_image": {"size": (1080, 1080), "bg": "scene", "count": 9},
        "style_prompt": "instagram style, warm tones, minimalist, lifestyle photography"
    }
}
```

---

## 十七、视频生成模块（完整方案）

### 17.1 技术栈

| 工具 | 用途 | 显存要求 |
|------|------|---------|
| yt-dlp | 竞品视频下载去水印 | 无 |
| Whisper large-v3 | 语音转文字提取脚本 | 6GB |
| Agnes AI | 爆款结构分析 + 新脚本生成 | - |
| CosyVoice2 | 中文TTS语音合成 | 4GB |
| MuseTalk | 真人照片驱动口播视频 | 8GB |
| FFmpeg | 视频合成/剪辑/字幕/BGM | 无 |

**总显存需求：建议RTX 4070 16GB，可分步推理降低峰值占用**

### 17.2 完整视频生产流水线

```
【第一阶段：竞品爆款分析】

RPA在抖音/快手搜索同类商品
    ↓
筛选条件：点赞>1万 / 近7天发布 / 同品类
    ↓
yt-dlp 批量下载去水印视频
    ↓
Whisper large-v3 语音转文字
    ↓
Agnes AI 分析爆款结构：
  {
    "hook_type": "痛点型/好奇型/对比型/福利型",
    "hook_duration": "前3秒内容",
    "structure": [
      {"time": "0-3s", "content": "钩子", "technique": "痛点放大"},
      {"time": "3-8s", "content": "问题展开"},
      {"time": "8-18s", "content": "产品展示+卖点"},
      {"time": "18-22s", "content": "促单话术+价格"}
    ],
    "tone": "亲切/专业/夸张/测评",
    "pacing": "快切/慢节奏",
    "bgm_style": "轻快/抒情/紧张"
  }
    ↓
沉淀为该品类「爆款模板库」

【第二阶段：原创视频生成】

输入：商品信息 + 爆款模板
    ↓
Agnes AI 套模板生成口播脚本
（完全原创，换入自己商品卖点）
    ↓
CosyVoice2 合成口播音频
（支持多种音色，自然度高）
    ↓
MuseTalk 驱动真人照片生成口播视频
（客户提供3-5张不同真人形象轮换使用）
    ↓
ComfyUI 生成商品展示素材图/动效
    ↓
FFmpeg 合成最终视频：
  · 口播视频（主画面）
  · 商品素材穿插（按脚本节点切换）
  · 自动添加字幕（Whisper反向生成SRT）
  · BGM混音（预置音乐库匹配风格）
    ↓
输出多平台格式：
  · 抖音/快手：9:16 竖屏 1080×1920
  · 小红书：1:1 方形 1080×1080
  · 视频时长：15-60秒可配置
```

### 17.3 核心代码结构

```python
# agents/video_agent.py
class VideoAgent(BaseAgent):

    async def analyze_competitor_videos(
        self,
        keyword: str,
        platform: str = "douyin",
        count: int = 10
    ) -> dict:
        """第一阶段：分析竞品爆款，提炼模板"""

        # RPA抓取爆款视频URL列表
        video_urls = await self.rpa.get_hot_videos(keyword, platform, count)

        templates = []
        for url in video_urls:
            # 下载去水印
            video_path = await self.download_video(url)

            # 语音转文字
            transcript = await self.transcribe(video_path)

            # Agnes AI分析结构
            template = await self.analyze_structure(transcript, video_path)
            templates.append(template)

        # 提炼共同模式，生成品类爆款模板
        category_template = await self.extract_pattern(templates)
        await self.save_template(keyword, category_template)
        return category_template

    async def generate_video(
        self,
        product_data: dict,
        template: dict,
        persona_image: str  # 真人照片路径
    ) -> str:
        """第二阶段：基于模板生成原创口播视频"""

        # 1. 生成口播脚本
        script = await self.generate_script(product_data, template)

        # 2. TTS合成音频
        audio_path = await self.synthesize_voice(script)

        # 3. MuseTalk生成口播视频
        talking_head_path = await self.generate_talking_head(
            persona_image, audio_path
        )

        # 4. 生成商品素材
        product_clips = await self.image_agent.generate_product_image(
            product_data["image"], platform="douyin"
        )

        # 5. FFmpeg合成
        final_video = await self.compose_video(
            talking_head=talking_head_path,
            product_clips=product_clips,
            audio=audio_path,
            script=script,
            template=template
        )
        return final_video

    async def download_video(self, url: str) -> str:
        """yt-dlp去水印下载"""
        import subprocess
        output_path = f"temp/video_{uuid4()}.mp4"
        subprocess.run([
            "yt-dlp",
            "--no-watermark",
            "-o", output_path,
            url
        ], check=True)
        return output_path

    async def transcribe(self, video_path: str) -> str:
        """Whisper语音转文字"""
        import whisper
        model = whisper.load_model("large-v3")
        result = model.transcribe(video_path, language="zh")
        return result["text"]

    async def compose_video(self, **kwargs) -> str:
        """FFmpeg合成最终视频"""
        # 字幕生成
        srt_path = await self.generate_srt(kwargs["script"], kwargs["audio"])

        # FFmpeg合成命令
        output_path = f"output/video_{uuid4()}.mp4"
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", kwargs["talking_head"],
            "-i", kwargs["audio"],
            "-vf", f"subtitles={srt_path}",
            "-c:v", "libx264",
            "-c:a", "aac",
            output_path
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        return output_path
```

### 17.4 真人形象管理建议

客户需提供3-5张不同真人形象照片轮换使用，规避抖音批量发布检测：

```python
# 形象轮换策略
class PersonaManager:
    def __init__(self, persona_images: list[str]):
        self.personas = persona_images
        self.usage_count = {p: 0 for p in persona_images}

    def get_next_persona(self) -> str:
        """选择使用次数最少的形象，保持均衡轮换"""
        return min(self.usage_count, key=self.usage_count.get)
```

---

## 十八、多租户架构设计

### 18.1 设计原则

- **数据隔离**：所有业务表携带 `tenant_id`，查询层强制过滤
- **资源隔离**：每个租户独立Celery队列，防止相互影响
- **配置隔离**：套餐功能、资源上限按租户独立配置
- **共享基础设施**：PostgreSQL、Redis、ComfyUI等服务共享，降低成本

### 18.2 租户数据模型

```sql
-- 租户表
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    phone VARCHAR(20),
    plan VARCHAR(20) NOT NULL DEFAULT 'starter',
    -- starter/basic/growth/pro/enterprise
    status VARCHAR(20) DEFAULT 'active',
    -- active/suspended/cancelled
    trial_ends_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 租户配置表（套餐权益）
CREATE TABLE tenant_configs (
    tenant_id UUID PRIMARY KEY REFERENCES tenants(id),
    max_shops INTEGER NOT NULL,           -- 最大店铺数
    max_monthly_images INTEGER,           -- 每月图片生成额度
    max_monthly_videos INTEGER,           -- 每月视频生成额度
    features_enabled JSONB DEFAULT '{}',  -- 功能开关
    -- {"selection": true, "pricing": true, "cs": true, ...}
    celery_queue VARCHAR(50),             -- 专属任务队列名
    api_rate_limit INTEGER DEFAULT 100,   -- API调用频率限制/分钟
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 订阅记录表
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    plan VARCHAR(20) NOT NULL,
    price_monthly DECIMAL(10,2),
    price_paid DECIMAL(10,2),             -- 实际支付金额
    billing_cycle VARCHAR(10),            -- monthly/yearly
    starts_at TIMESTAMP NOT NULL,
    ends_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    payment_method VARCHAR(20),           -- wechat/alipay
    created_at TIMESTAMP DEFAULT NOW()
);

-- 用量记录表
CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    resource_type VARCHAR(50),
    -- images/videos/api_calls/rpa_operations
    quantity INTEGER DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- 所有业务表统一加 tenant_id（示例）
ALTER TABLE shops ADD COLUMN tenant_id UUID REFERENCES tenants(id);
ALTER TABLE products ADD COLUMN tenant_id UUID REFERENCES tenants(id);
ALTER TABLE orders ADD COLUMN tenant_id UUID REFERENCES tenants(id);
ALTER TABLE agent_tasks ADD COLUMN tenant_id UUID REFERENCES tenants(id);

-- 所有业务表加行级安全策略（PostgreSQL RLS）
ALTER TABLE shops ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON shops
    USING (tenant_id = current_setting('app.tenant_id')::UUID);
```

### 18.3 Celery多租户队列隔离

```python
# tasks/celery_app.py
from celery import Celery

app = Celery("ecommerce_agent")

# 每个租户独立队列，按套餐分配并发数
PLAN_CONCURRENCY = {
    "starter":    2,   # 新手版：2并发
    "basic":      4,   # 入门版：4并发
    "growth":     8,   # 成长版：8并发
    "pro":        16,  # 专业版：16并发
    "enterprise": 32,  # 旗舰版：32并发
}

def get_tenant_queue(tenant_id: str) -> str:
    return f"tenant_{tenant_id}"

def get_tenant_worker_concurrency(plan: str) -> int:
    return PLAN_CONCURRENCY.get(plan, 2)

# 任务路由：自动路由到租户专属队列
@app.task(bind=True)
def rpa_task(self, tenant_id: str, task_type: str, payload: dict):
    queue = get_tenant_queue(tenant_id)
    # 执行RPA任务...
```

### 18.4 租户中间件（FastAPI）

```python
# middleware/tenant.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    """
    从JWT Token中提取tenant_id
    注入到请求上下文和数据库会话
    """
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if token:
            payload = decode_jwt(token)
            tenant_id = payload.get("tenant_id")

            if not tenant_id:
                raise HTTPException(status_code=401, detail="Invalid token")

            # 注入tenant_id到请求状态
            request.state.tenant_id = tenant_id

            # PostgreSQL RLS：设置当前租户
            await db.execute(
                f"SET app.tenant_id = '{tenant_id}'"
            )

        return await call_next(request)
```

---

## 十九、定价体系与套餐设计

### 19.1 套餐分级

| 套餐 | 店铺数上限 | 月付 | 年付 | 适合人群 |
|------|-----------|------|------|---------|
| 新手版 | 2个店铺 | ¥99 | ¥999 | 个人卖家体验，完整功能 |
| 入门版 | 5个店铺 | ¥599 | ¥5,999 | 小型店铺团队 |
| 成长版 | 15个店铺 | ¥1,299 | ¥12,999 | 中型多平台团队 |
| 专业版 | 30个店铺 | ¥2,499 | ¥24,999 | 规模化店群运营 |
| 旗舰版 | 无限制 | ¥4,999 | ¥49,999 | 大型电商公司 |

**所有套餐功能全开放**，升级驱动力来自店铺数量。

### 19.2 AI内容按量计费（叠加在套餐之上）

每个套餐每月赠送基础额度，超出按量付费：

| 资源类型 | 新手版赠送 | 入门版赠送 | 成长版+ | 超出单价 |
|---------|-----------|-----------|--------|---------|
| AI生成图片 | 50张/月 | 200张/月 | 500张/月 | ¥0.5/张 |
| AI生成视频 | 5条/月 | 20条/月 | 50条/月 | ¥5/条 |
| 竞品视频分析 | 20条/月 | 100条/月 | 300条/月 | ¥0.2/条 |

### 19.3 数据库套餐配置

```python
PLAN_CONFIGS = {
    "starter": {
        "max_shops": 2,
        "max_monthly_images": 50,
        "max_monthly_videos": 5,
        "max_monthly_video_analysis": 20,
        "celery_concurrency": 2,
        "price_monthly": 99,
        "price_yearly": 999,
    },
    "basic": {
        "max_shops": 5,
        "max_monthly_images": 200,
        "max_monthly_videos": 20,
        "max_monthly_video_analysis": 100,
        "celery_concurrency": 4,
        "price_monthly": 599,
        "price_yearly": 5999,
    },
    "growth": {
        "max_shops": 15,
        "max_monthly_images": 500,
        "max_monthly_videos": 50,
        "max_monthly_video_analysis": 300,
        "celery_concurrency": 8,
        "price_monthly": 1299,
        "price_yearly": 12999,
    },
    "pro": {
        "max_shops": 30,
        "max_monthly_images": 1500,
        "max_monthly_videos": 150,
        "max_monthly_video_analysis": 1000,
        "celery_concurrency": 16,
        "price_monthly": 2499,
        "price_yearly": 24999,
    },
    "enterprise": {
        "max_shops": -1,  # 无限制
        "max_monthly_images": 5000,
        "max_monthly_videos": 500,
        "max_monthly_video_analysis": -1,  # 无限制
        "celery_concurrency": 32,
        "price_monthly": 4999,
        "price_yearly": 49999,
    },
}
```

---

## 二十、官网与用户系统设计

### 20.1 官网技术栈

```
官网：Next.js 14（静态生成，SEO友好）
部署：Vercel 或阿里云OSS + CDN
域名：独立域名，SSL证书
```

### 20.2 官网页面结构

```
首页
  ├── Hero区：核心价值主张 + CTA（免费试用）
  ├── 痛点共鸣：3大电商运营痛点
  ├── 产品演示：功能动图/视频展示
  ├── 核心功能：8大Agent卡片
  ├── 数据背书：关键指标（7×24h/60%降本/3分钟出图）
  ├── 客户案例：真实案例（上线后补充）
  └── 定价页面入口

定价页
  ├── 5档套餐对比表
  ├── AI内容按量计费说明
  ├── 年付优惠说明（约省2个月）
  └── 常见问题FAQ

功能页（各模块详细介绍）
登录/注册页
```

### 20.3 用户系统功能

```
注册/登录
  ├── 邮箱注册 + 手机号验证
  ├── 微信扫码登录（可选）
  └── 新注册赠送7天成长版试用

控制台（用户Dashboard）
  ├── 套餐状态与用量
  ├── 升级/续费入口
  ├── 发票申请
  └── 下载桌面端客户端

支付系统
  ├── 微信支付 + 支付宝（接入官方SDK）
  ├── 订阅自动续费
  ├── 按量消费充值余额
  └── 开票（增值税电子发票）
```

### 20.4 管理后台（内部使用）

```
租户管理
  ├── 租户列表/搜索/状态管理
  ├── 手动调整套餐/额度
  ├── 封禁/解封账户
  └── 用量查看

运营数据
  ├── 注册/付费转化漏斗
  ├── 各套餐用户分布
  ├── AI内容用量统计
  └── 收入报表

系统监控
  ├── RPA任务成功率
  ├── Agent响应时间
  ├── 各平台适配器健康状态
  └── 异常告警
```

### 20.5 服务端架构扩展（SaaS化）

原有单客户部署模式升级为云端SaaS：

```
用户注册 → 创建租户记录 → 分配Celery队列
    ↓
用户在控制台下载桌面端（Tauri）
    ↓
桌面端安装后，输入账号登录
    ↓
桌面端连接云端服务（FastAPI）
    ↓
RPA在用户本地电脑执行
（浏览器自动化在本地跑，数据上传云端存储）
```

**关键设计**：RPA执行在用户本地，保证账号安全；Agent决策和数据存储在云端，保证多设备同步。

---

## 二十一、更新后的实施计划（含SaaS化）

### 第一期（Week 1-4）：核心产品
- 基础架构 + 多租户数据层
- 店铺扫码绑定
- 拼多多/淘宝RPA适配器
- 定价/客服/选品Agent基础版
- 手机端PWA

### 第二期（Week 5-8）：完整功能
- ComfyUI图片生产流水线
- 视频爆款分析 + 口播视频生成
- 内容上架全自动
- 广告Agent
- 订单自动发货 + 虚拟机微信
- 抖音/小红书适配器

### 第三期（Week 9-12）：SaaS化上线
- 官网开发（Next.js）
- 用户注册/登录/支付系统
- 管理后台
- 多租户资源隔离完整版
- 公测上线，首批用户导入

---

*文档版本：v2.0 | 新增：图片/视频完整方案、多租户架构、定价体系、官网设计*

---

# 第二部分：数据库设计

## ER图（Mermaid格式）

> 可将以下代码粘贴到 [Mermaid Live Editor](https://mermaid.live) 渲染完整ER图

```mermaid
erDiagram

    %% ─────────────────────────────────────────
    %% 一、租户与用户域
    %% ─────────────────────────────────────────

    TENANTS {
        uuid id PK
        string name
        string email UK
        string phone
        string status "active/suspended/cancelled"
        timestamp trial_ends_at
        timestamp created_at
    }

    USERS {
        uuid id PK
        uuid tenant_id FK
        string name
        string email UK
        string phone
        string role "owner/admin/operator"
        string password_hash
        string status "active/inactive"
        timestamp last_login_at
        timestamp created_at
    }

    PLANS {
        string code PK "starter/basic/growth/pro/enterprise"
        string name
        integer max_shops
        integer max_monthly_images
        integer max_monthly_videos
        integer max_monthly_video_analysis
        integer celery_concurrency
        decimal price_monthly
        decimal price_yearly
        jsonb features
        timestamp created_at
    }

    TENANT_CONFIGS {
        uuid tenant_id PK FK
        string plan_code FK
        integer max_shops
        integer max_monthly_images
        integer max_monthly_videos
        integer max_monthly_video_analysis
        integer celery_concurrency
        string celery_queue
        integer api_rate_limit
        jsonb features_enabled
        timestamp updated_at
    }

    SUBSCRIPTIONS {
        uuid id PK
        uuid tenant_id FK
        string plan_code FK
        string billing_cycle "monthly/yearly"
        decimal price_paid
        string status "active/expired/cancelled"
        string payment_method "wechat/alipay"
        string payment_trade_no
        timestamp starts_at
        timestamp ends_at
        timestamp created_at
    }

    INVOICES {
        uuid id PK
        uuid tenant_id FK
        uuid subscription_id FK
        string invoice_no UK
        decimal amount
        string type "ordinary/special"
        string status "pending/issued/cancelled"
        string receiver_name
        string receiver_email
        string tax_no
        timestamp issued_at
        timestamp created_at
    }

    USAGE_RECORDS {
        uuid id PK
        uuid tenant_id FK
        string resource_type "images/videos/video_analysis/rpa_ops/api_calls"
        integer quantity
        uuid reference_id "关联的任务ID"
        timestamp recorded_at
    }

    RECHARGE_RECORDS {
        uuid id PK
        uuid tenant_id FK
        string resource_type
        integer quantity
        decimal amount_paid
        string payment_method
        string payment_trade_no
        string status "pending/success/failed"
        timestamp created_at
    }

    %% ─────────────────────────────────────────
    %% 二、店铺域
    %% ─────────────────────────────────────────

    SHOPS {
        uuid id PK
        uuid tenant_id FK
        string name
        string platform "douyin/taobao/pdd/xiaohongshu"
        string platform_shop_id
        string platform_shop_name
        text cookies_encrypted "AES加密存储"
        timestamp cookie_expires_at
        string status "active/paused/cookie_expired/error"
        jsonb config "店铺个性化配置"
        timestamp last_synced_at
        timestamp created_at
        timestamp updated_at
    }

    PLATFORM_ADAPTERS {
        string platform PK
        string version
        jsonb selectors "页面元素选择器"
        jsonb operation_flows "操作流程定义"
        boolean is_healthy
        timestamp last_checked_at
        timestamp updated_at
    }

    SHOP_METRICS {
        uuid id PK
        uuid shop_id FK
        date metric_date
        integer total_orders
        decimal total_revenue
        integer total_visitors
        decimal conversion_rate
        decimal refund_rate
        decimal ads_spend
        decimal ads_roi
        timestamp recorded_at
    }

    %% ─────────────────────────────────────────
    %% 三、商品域
    %% ─────────────────────────────────────────

    PRODUCTS {
        uuid id PK
        uuid tenant_id FK
        uuid shop_id FK
        string platform_product_id
        string title
        string category_id FK
        text description
        decimal cost "1688采购成本"
        decimal current_price
        string status "on_sale/off_shelf/draft/deleted"
        string source_url "1688商品链接"
        jsonb platform_data "平台专属字段"
        integer total_sales
        decimal avg_rating
        timestamp listed_at
        timestamp created_at
        timestamp updated_at
    }

    PRODUCT_CATEGORIES {
        uuid id PK
        uuid tenant_id FK
        string name
        uuid parent_id FK "自关联，支持多级分类"
        integer level
        timestamp created_at
    }

    SKUS {
        uuid id PK
        uuid product_id FK
        string platform_sku_id
        jsonb attributes "颜色/尺码等规格"
        decimal price
        decimal cost
        integer stock
        string barcode
        string status "active/inactive"
        timestamp created_at
        timestamp updated_at
    }

    COMPETITOR_PRICES {
        uuid id PK
        uuid product_id FK
        string platform
        string competitor_shop_id
        string competitor_shop_name
        string competitor_product_id
        decimal price
        integer monthly_sales
        decimal rating
        timestamp recorded_at
    }

    SELECTION_REPORTS {
        uuid id PK
        uuid tenant_id FK
        string source_url "1688链接"
        string keyword
        jsonb product_data "原始商品数据"
        integer overall_score
        jsonb platform_scores "各平台评分"
        jsonb profit_estimate
        jsonb risks
        string recommendation "strong_buy/buy/hold/pass"
        string status "pending/reviewed/adopted/rejected"
        uuid reviewed_by FK
        timestamp reviewed_at
        timestamp created_at
    }

    %% ─────────────────────────────────────────
    %% 四、订单域
    %% ─────────────────────────────────────────

    ORDERS {
        uuid id PK
        uuid tenant_id FK
        uuid shop_id FK
        uuid product_id FK
        uuid sku_id FK
        string platform_order_id UK
        integer quantity
        decimal sale_price
        decimal total_amount
        decimal refund_amount
        string status "pending/paid/shipped/completed/refunding/refunded/cancelled"
        string fulfillment_type "1688_dropship/self_warehouse/supplier_direct"
        string buyer_encrypted "加密买家信息"
        timestamp paid_at
        timestamp shipped_at
        timestamp completed_at
        timestamp created_at
    }

    LOGISTICS {
        uuid id PK
        uuid order_id FK
        string carrier "快递公司"
        string tracking_no
        string status "pending/picked_up/in_transit/delivered/exception"
        jsonb tracking_history
        timestamp shipped_at
        timestamp delivered_at
        timestamp updated_at
    }

    SUPPLIERS {
        uuid id PK
        uuid tenant_id FK
        string name
        string platform "1688/wechat/offline"
        string platform_supplier_id "1688店铺ID"
        string contact_name
        string contact_wechat
        string contact_phone
        decimal avg_ship_days
        decimal quality_score
        string status "active/inactive"
        timestamp created_at
    }

    PRODUCT_SUPPLIERS {
        uuid id PK
        uuid product_id FK
        uuid supplier_id FK
        decimal supply_price
        integer min_order_qty
        integer lead_days
        boolean is_primary
        timestamp created_at
    }

    SHIPMENT_RECORDS {
        uuid id PK
        uuid order_id FK
        uuid supplier_id FK
        string channel "1688_auto/wechat_notify/manual"
        string status "pending/notified/confirmed/shipped"
        text message_content "通知内容"
        string screenshot_url "通知截图"
        timestamp notified_at
        timestamp confirmed_at
        timestamp created_at
    }

    %% ─────────────────────────────────────────
    %% 五、Agent任务域
    %% ─────────────────────────────────────────

    AGENT_TASKS {
        uuid id PK
        uuid tenant_id FK
        uuid shop_id FK
        string agent_type "selection/pricing/inventory/ads/cs/content/image/video"
        string task_type "具体任务类型"
        string trigger "scheduled/event/manual/user_command"
        jsonb input_data
        jsonb decisions "Agent决策内容"
        jsonb actions "待执行动作列表"
        string status "pending/pending_approval/approved/executing/done/failed/cancelled"
        integer retry_count
        text error_message
        jsonb result
        timestamp started_at
        timestamp completed_at
        timestamp created_at
    }

    APPROVAL_TASKS {
        uuid id PK
        uuid tenant_id FK
        uuid agent_task_id FK
        uuid shop_id FK
        integer priority "1最高"
        string title
        text description
        jsonb options "可选操作"
        string status "pending/approved/rejected/modified/expired"
        uuid decided_by FK
        jsonb decision_detail "审批结果详情"
        timestamp expires_at
        timestamp decided_at
        timestamp created_at
    }

    RPA_OPERATIONS {
        uuid id PK
        uuid tenant_id FK
        uuid agent_task_id FK
        uuid shop_id FK
        string platform
        string operation_type "click/input/navigate/scrape/screenshot"
        jsonb operation_params
        string status "pending/running/success/failed/retrying"
        string screenshot_url
        integer retry_count
        text error_message
        integer duration_ms
        timestamp started_at
        timestamp completed_at
    }

    OPERATION_LOGS {
        uuid id PK
        uuid tenant_id FK
        uuid rpa_operation_id FK
        string level "info/warn/error"
        text message
        jsonb context
        timestamp logged_at
    }

    USER_COMMANDS {
        uuid id PK
        uuid tenant_id FK
        uuid user_id FK
        string channel "mobile/desktop"
        text raw_input "用户原始输入"
        jsonb parsed_intent "解析结果"
        string target_agent
        uuid agent_task_id FK "触发的任务"
        string status "parsing/dispatched/done/failed"
        timestamp created_at
    }

    %% ─────────────────────────────────────────
    %% 六、内容域
    %% ─────────────────────────────────────────

    PRODUCT_IMAGES {
        uuid id PK
        uuid tenant_id FK
        uuid product_id FK
        string type "main/scene/white_bg/detail/xhs_style"
        string platform "pdd/taobao/douyin/xiaohongshu/universal"
        string url
        string storage_path
        integer width
        integer height
        string generation_method "comfyui/manual"
        jsonb generation_params "ComfyUI工作流参数"
        string status "generating/ready/rejected"
        timestamp created_at
    }

    PRODUCT_VIDEOS {
        uuid id PK
        uuid tenant_id FK
        uuid product_id FK
        string type "oral/showcase/composite"
        string platform "douyin/kuaishou/xiaohongshu"
        string url
        string storage_path
        integer duration_seconds
        string aspect_ratio "9:16/1:1/16:9"
        uuid persona_id FK "使用的数字人形象"
        uuid script_id FK "使用的口播脚本"
        uuid template_id FK "使用的爆款模板"
        string status "generating/ready/published/rejected"
        timestamp created_at
    }

    ORAL_SCRIPTS {
        uuid id PK
        uuid tenant_id FK
        uuid product_id FK
        uuid template_id FK
        text script_content "口播脚本正文"
        integer duration_seconds "预估时长"
        string tone "亲切/专业/夸张/测评"
        string status "draft/approved/used"
        uuid created_by FK
        timestamp created_at
    }

    VIRAL_TEMPLATES {
        uuid id PK
        uuid tenant_id FK
        string category "品类"
        string platform "douyin/kuaishou"
        string hook_type "痛点型/好奇型/对比型/福利型"
        jsonb structure "视频结构定义"
        string tone
        string pacing "fast/slow"
        string bgm_style
        integer usage_count
        decimal avg_performance_score
        jsonb source_videos "参考的竞品视频"
        timestamp created_at
        timestamp updated_at
    }

    COMPETITOR_VIDEOS {
        uuid id PK
        uuid tenant_id FK
        string platform
        string original_url
        string local_path
        string transcript "Whisper转写文字"
        integer likes_count
        integer comments_count
        integer shares_count
        uuid analyzed_template_id FK
        string status "downloaded/transcribed/analyzed"
        timestamp published_at
        timestamp downloaded_at
        timestamp created_at
    }

    PERSONAS {
        uuid id PK
        uuid tenant_id FK
        string name "形象名称"
        string image_url "真人照片URL"
        string image_path
        integer usage_count
        timestamp last_used_at
        string status "active/inactive"
        timestamp created_at
    }

    COPYWRITING {
        uuid id PK
        uuid tenant_id FK
        uuid product_id FK
        string platform
        string type "title/description/bullet_points/seo_tags"
        text content
        string status "draft/approved/published"
        uuid created_by FK
        timestamp created_at
    }

    %% ─────────────────────────────────────────
    %% 七、广告域
    %% ─────────────────────────────────────────

    AD_CAMPAIGNS {
        uuid id PK
        uuid tenant_id FK
        uuid shop_id FK
        string platform_campaign_id
        string name
        string platform
        string type "search/display/live"
        string status "active/paused/ended"
        decimal daily_budget
        decimal total_budget
        date start_date
        date end_date
        timestamp created_at
        timestamp updated_at
    }

    AD_GROUPS {
        uuid id PK
        uuid campaign_id FK
        string platform_group_id
        string name
        decimal bid_price
        string bid_strategy "manual/auto/target_roi"
        decimal target_roi
        string status "active/paused"
        timestamp created_at
        timestamp updated_at
    }

    AD_KEYWORDS {
        uuid id PK
        uuid ad_group_id FK
        string keyword
        string match_type "exact/phrase/broad"
        decimal bid_price
        string status "active/paused/negative"
        timestamp created_at
    }

    AD_STATS {
        uuid id PK
        uuid tenant_id FK
        uuid campaign_id FK
        uuid ad_group_id FK
        date stat_date
        integer impressions
        integer clicks
        decimal spend
        integer conversions
        decimal revenue
        decimal ctr
        decimal cvr
        decimal roi
        decimal cpc
        timestamp recorded_at
    }

    AD_OPTIMIZATION_RECORDS {
        uuid id PK
        uuid tenant_id FK
        uuid agent_task_id FK
        uuid campaign_id FK
        string action_type "bid_adjust/pause_keyword/add_keyword/budget_adjust"
        jsonb before_state
        jsonb after_state
        string reason "优化依据"
        string status "pending_approval/executed/rolled_back"
        timestamp executed_at
        timestamp created_at
    }

    %% ─────────────────────────────────────────
    %% 八、客服域
    %% ─────────────────────────────────────────

    CS_SESSIONS {
        uuid id PK
        uuid tenant_id FK
        uuid shop_id FK
        string platform_session_id
        string buyer_id "平台买家ID（脱敏）"
        string status "open/ai_handling/escalated/closed"
        string escalation_reason
        uuid assigned_to FK "转人工后的处理人"
        decimal sentiment_score "情绪评分-1到1"
        integer message_count
        timestamp opened_at
        timestamp closed_at
        timestamp created_at
    }

    CS_MESSAGES {
        uuid id PK
        uuid session_id FK
        string sender_type "buyer/ai/human"
        text content
        string reply_type "auto/manual/template"
        decimal confidence_score "AI回复置信度"
        boolean was_edited "人工是否修改过"
        timestamp sent_at
    }

    CS_KNOWLEDGE_BASE {
        uuid id PK
        uuid shop_id FK
        string type "product_info/platform_rule/faq/return_policy"
        string title
        text content
        jsonb metadata
        integer hit_count
        string status "active/outdated"
        timestamp last_updated_at
        timestamp created_at
    }

    CS_FAQ {
        uuid id PK
        uuid shop_id FK
        uuid knowledge_base_id FK
        text question
        text answer
        jsonb question_variants "问法变体"
        integer hit_count
        decimal avg_satisfaction
        string status "active/inactive"
        timestamp created_at
        timestamp updated_at
    }

    CS_REVIEWS {
        uuid id PK
        uuid tenant_id FK
        uuid shop_id FK
        uuid order_id FK
        string platform_review_id
        integer rating "1-5"
        text content
        string sentiment "positive/neutral/negative"
        string status "normal/needs_attention/replied"
        text reply_content
        boolean is_auto_replied
        timestamp review_at
        timestamp replied_at
        timestamp created_at
    }

    %% ─────────────────────────────────────────
    %% 关系定义
    %% ─────────────────────────────────────────

    TENANTS ||--o{ USERS : "has"
    TENANTS ||--|| TENANT_CONFIGS : "has"
    TENANTS ||--o{ SUBSCRIPTIONS : "has"
    TENANTS ||--o{ INVOICES : "has"
    TENANTS ||--o{ USAGE_RECORDS : "has"
    TENANTS ||--o{ RECHARGE_RECORDS : "has"
    TENANTS ||--o{ SHOPS : "owns"
    TENANTS ||--o{ AGENT_TASKS : "has"
    TENANTS ||--o{ USER_COMMANDS : "has"

    PLANS ||--o{ TENANT_CONFIGS : "applied_to"
    PLANS ||--o{ SUBSCRIPTIONS : "used_in"

    SUBSCRIPTIONS ||--o{ INVOICES : "generates"

    SHOPS ||--o{ PRODUCTS : "sells"
    SHOPS ||--o{ ORDERS : "has"
    SHOPS ||--o{ SHOP_METRICS : "tracks"
    SHOPS ||--o{ AD_CAMPAIGNS : "runs"
    SHOPS ||--o{ CS_SESSIONS : "handles"
    SHOPS ||--o{ AGENT_TASKS : "triggers"

    PLATFORM_ADAPTERS ||--o{ SHOPS : "supports"

    PRODUCTS ||--o{ SKUS : "has"
    PRODUCTS ||--o{ COMPETITOR_PRICES : "tracks"
    PRODUCTS ||--o{ PRODUCT_IMAGES : "has"
    PRODUCTS ||--o{ PRODUCT_VIDEOS : "has"
    PRODUCTS ||--o{ ORAL_SCRIPTS : "has"
    PRODUCTS ||--o{ COPYWRITING : "has"
    PRODUCTS ||--o{ ORDERS : "in"
    PRODUCTS ||--o{ PRODUCT_SUPPLIERS : "supplied_by"

    PRODUCT_CATEGORIES ||--o{ PRODUCTS : "categorizes"
    PRODUCT_CATEGORIES ||--o{ PRODUCT_CATEGORIES : "parent_of"

    SKUS ||--o{ ORDERS : "ordered_in"

    SUPPLIERS ||--o{ PRODUCT_SUPPLIERS : "supplies"
    SUPPLIERS ||--o{ SHIPMENT_RECORDS : "notified_in"

    ORDERS ||--|| LOGISTICS : "has"
    ORDERS ||--o{ SHIPMENT_RECORDS : "triggers"
    ORDERS ||--o{ CS_REVIEWS : "reviewed_in"

    AGENT_TASKS ||--o{ APPROVAL_TASKS : "may_require"
    AGENT_TASKS ||--o{ RPA_OPERATIONS : "executes"
    AGENT_TASKS ||--o{ AD_OPTIMIZATION_RECORDS : "creates"

    RPA_OPERATIONS ||--o{ OPERATION_LOGS : "logs"

    USER_COMMANDS ||--o{ AGENT_TASKS : "triggers"

    VIRAL_TEMPLATES ||--o{ PRODUCT_VIDEOS : "used_in"
    VIRAL_TEMPLATES ||--o{ ORAL_SCRIPTS : "guides"
    VIRAL_TEMPLATES ||--o{ COMPETITOR_VIDEOS : "derived_from"

    ORAL_SCRIPTS ||--o{ PRODUCT_VIDEOS : "used_in"

    PERSONAS ||--o{ PRODUCT_VIDEOS : "appears_in"

    AD_CAMPAIGNS ||--o{ AD_GROUPS : "contains"
    AD_CAMPAIGNS ||--o{ AD_STATS : "tracks"
    AD_CAMPAIGNS ||--o{ AD_OPTIMIZATION_RECORDS : "optimized_by"

    AD_GROUPS ||--o{ AD_KEYWORDS : "contains"
    AD_GROUPS ||--o{ AD_STATS : "tracks"

    CS_SESSIONS ||--o{ CS_MESSAGES : "contains"

    CS_KNOWLEDGE_BASE ||--o{ CS_FAQ : "contains"

    APPROVAL_TASKS ||--o{ USERS : "decided_by"

    SELECTION_REPORTS ||--o{ PRODUCTS : "leads_to"
```

---

**版本：** v1.0  
**数据库：** PostgreSQL 15+  
**总表数：** 46张表，覆盖8个业务域

---

## 设计规范

- 所有主键使用 `UUID`，`DEFAULT gen_random_uuid()`
- 所有业务表携带 `tenant_id`，启用 PostgreSQL RLS 行级隔离
- 敏感字段（买家信息、Cookie）AES-256加密存储
- 时间字段统一使用 `TIMESTAMP WITH TIME ZONE`，存储UTC
- 软删除字段：`status` 枚举包含 `deleted`，不物理删除
- JSON字段统一用 `JSONB`（支持索引查询）

---

## 一、租户与用户域（8张表）

### 1.1 TENANTS — 租户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 租户唯一ID |
| name | VARCHAR(100) | 租户名称（公司/个人名） |
| email | VARCHAR(200) UNIQUE | 注册邮箱，登录凭证 |
| phone | VARCHAR(20) | 手机号 |
| status | VARCHAR(20) | active/suspended/cancelled |
| trial_ends_at | TIMESTAMP | 试用期结束时间，NULL表示非试用 |
| created_at | TIMESTAMP | 注册时间 |

**索引：** `email`（唯一）

---

### 1.2 USERS — 用户表

一个租户可以有多个用户（对应5个运营人员各自账号）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 用户ID |
| tenant_id | UUID FK | 所属租户 |
| name | VARCHAR(100) | 用户姓名 |
| email | VARCHAR(200) UNIQUE | 登录邮箱 |
| phone | VARCHAR(20) | 手机号（接收短信验证码） |
| role | VARCHAR(20) | owner/admin/operator |
| password_hash | TEXT | bcrypt哈希，不存明文 |
| status | VARCHAR(20) | active/inactive |
| last_login_at | TIMESTAMP | 最后登录时间 |
| created_at | TIMESTAMP | 创建时间 |

**角色说明：**
- `owner`：租户所有者，可管理套餐和成员
- `admin`：管理员，可配置Agent策略
- `operator`：操作员，只能审批和查看

---

### 1.3 PLANS — 套餐表（系统预置，不含tenant_id）

| 字段 | 类型 | 说明 |
|------|------|------|
| code | VARCHAR(20) PK | starter/basic/growth/pro/enterprise |
| name | VARCHAR(50) | 套餐显示名称 |
| max_shops | INTEGER | 最大店铺数，-1为无限制 |
| max_monthly_images | INTEGER | 每月图片生成额度 |
| max_monthly_videos | INTEGER | 每月视频生成额度 |
| max_monthly_video_analysis | INTEGER | 每月竞品视频分析额度 |
| celery_concurrency | INTEGER | Celery并发Worker数 |
| price_monthly | DECIMAL(10,2) | 月付价格（元） |
| price_yearly | DECIMAL(10,2) | 年付价格（元） |
| features | JSONB | 功能开关配置 |

**PLANS预置数据：**
```
starter:    2店/50图/5视频  ¥99/月   ¥999/年
basic:      5店/200图/20视频  ¥599/月  ¥5999/年
growth:     15店/500图/50视频  ¥1299/月 ¥12999/年
pro:        30店/1500图/150视频 ¥2499/月 ¥24999/年
enterprise: 无限/5000图/500视频 ¥4999/月 ¥49999/年
```

---

### 1.4 TENANT_CONFIGS — 租户配置表

每个租户一条记录，存储当前生效的资源配置。与PLANS的关系：初始从PLANS复制，管理员可手动调整（如给特定租户加额度）。

| 字段 | 类型 | 说明 |
|------|------|------|
| tenant_id | UUID PK FK | 租户ID |
| plan_code | VARCHAR FK | 当前套餐 |
| max_shops | INTEGER | 当前生效的店铺上限 |
| max_monthly_images | INTEGER | 当前生效的图片额度 |
| max_monthly_videos | INTEGER | 当前生效的视频额度 |
| max_monthly_video_analysis | INTEGER | 当前生效的视频分析额度 |
| celery_concurrency | INTEGER | 并发数 |
| celery_queue | VARCHAR(50) | 专属队列名，格式：`tenant_{id}` |
| api_rate_limit | INTEGER | API调用频率限制（次/分钟） |
| features_enabled | JSONB | `{"selection":true,"ads":true,...}` |
| updated_at | TIMESTAMP | 最后更新时间 |

---

### 1.5 SUBSCRIPTIONS — 订阅记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 订阅ID |
| tenant_id | UUID FK | 租户ID |
| plan_code | VARCHAR FK | 套餐 |
| billing_cycle | VARCHAR(10) | monthly/yearly |
| price_paid | DECIMAL(10,2) | 实际支付金额（可能有优惠） |
| status | VARCHAR(20) | active/expired/cancelled |
| payment_method | VARCHAR(20) | wechat/alipay |
| payment_trade_no | VARCHAR(100) | 第三方支付流水号 |
| starts_at | TIMESTAMP | 订阅开始时间 |
| ends_at | TIMESTAMP | 订阅结束时间 |
| created_at | TIMESTAMP | 创建时间 |

**索引：** `(tenant_id, status)`

---

### 1.6 INVOICES — 发票表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 发票ID |
| tenant_id | UUID FK | 租户ID |
| subscription_id | UUID FK | 关联订阅 |
| invoice_no | VARCHAR(50) UNIQUE | 发票号码 |
| amount | DECIMAL(10,2) | 开票金额 |
| type | VARCHAR(20) | ordinary/special（普票/专票） |
| status | VARCHAR(20) | pending/issued/cancelled |
| receiver_name | VARCHAR(100) | 抬头名称 |
| receiver_email | VARCHAR(200) | 接收邮箱 |
| tax_no | VARCHAR(50) | 税号（专票必填） |
| issued_at | TIMESTAMP | 开票时间 |
| created_at | TIMESTAMP | 申请时间 |

---

### 1.7 USAGE_RECORDS — 用量记录表

每次消耗资源时写入一条记录，用于月度用量统计和超额判断。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 记录ID |
| tenant_id | UUID FK | 租户ID |
| resource_type | VARCHAR(50) | images/videos/video_analysis/rpa_ops/api_calls |
| quantity | INTEGER | 消耗数量（通常为1） |
| reference_id | UUID | 关联任务ID（可追溯来源） |
| recorded_at | TIMESTAMP | 记录时间 |

**查询示例：** 统计当月图片用量
```sql
SELECT SUM(quantity) FROM usage_records
WHERE tenant_id = $1
  AND resource_type = 'images'
  AND recorded_at >= date_trunc('month', NOW());
```

---

### 1.8 RECHARGE_RECORDS — 充值记录表

按量付费的充值记录（超出套餐额度后充值）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 充值ID |
| tenant_id | UUID FK | 租户ID |
| resource_type | VARCHAR(50) | 充值的资源类型 |
| quantity | INTEGER | 充值数量 |
| amount_paid | DECIMAL(10,2) | 支付金额 |
| payment_method | VARCHAR(20) | wechat/alipay |
| payment_trade_no | VARCHAR(100) | 支付流水号 |
| status | VARCHAR(20) | pending/success/failed |
| created_at | TIMESTAMP | 创建时间 |

---

## 二、店铺域（3张表）

### 2.1 SHOPS — 店铺表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 店铺ID |
| tenant_id | UUID FK | 所属租户 |
| name | VARCHAR(100) | 店铺名称（用户自定义备注） |
| platform | VARCHAR(20) | douyin/taobao/pdd/xiaohongshu |
| platform_shop_id | VARCHAR(100) | 平台分配的店铺ID（RPA抓取） |
| platform_shop_name | VARCHAR(200) | 平台上的店铺名称 |
| cookies_encrypted | TEXT | AES-256加密的登录Cookie JSON |
| cookie_expires_at | TIMESTAMP | Cookie预估过期时间 |
| status | VARCHAR(20) | active/paused/cookie_expired/error |
| config | JSONB | 店铺个性化配置（定价策略/广告预算上限等） |
| last_synced_at | TIMESTAMP | 最后一次数据同步时间 |
| created_at | TIMESTAMP | 绑定时间 |
| updated_at | TIMESTAMP | 更新时间 |

**config字段示例：**
```json
{
  "min_margin": 0.15,
  "max_ads_daily_budget": 500,
  "auto_price_follow": true,
  "cs_auto_reply": true,
  "price_floor": 10.0
}
```

---

### 2.2 PLATFORM_ADAPTERS — 平台适配器表

存储各平台的页面选择器和操作流程，页面结构变更时只需更新这张表，无需改代码。

| 字段 | 类型 | 说明 |
|------|------|------|
| platform | VARCHAR(20) PK | 平台标识 |
| version | VARCHAR(20) | 适配器版本号 |
| selectors | JSONB | CSS/XPath选择器配置 |
| operation_flows | JSONB | 操作流程步骤定义 |
| is_healthy | BOOLEAN | 当前是否正常可用 |
| last_checked_at | TIMESTAMP | 最后健康检查时间 |
| updated_at | TIMESTAMP | 更新时间 |

**selectors字段示例（拼多多）：**
```json
{
  "login_qrcode": "#loginQrcode img",
  "product_title": ".goods-name input",
  "product_price": ".price-input",
  "submit_button": ".submit-btn",
  "order_list": ".order-table tbody tr"
}
```

---

### 2.3 SHOP_METRICS — 店铺日报表

每天一条记录，记录店铺核心经营指标。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 记录ID |
| shop_id | UUID FK | 店铺ID |
| metric_date | DATE | 统计日期 |
| total_orders | INTEGER | 当日订单数 |
| total_revenue | DECIMAL(12,2) | 当日销售额 |
| total_visitors | INTEGER | 访客数（UV） |
| conversion_rate | DECIMAL(5,4) | 转化率 |
| refund_rate | DECIMAL(5,4) | 退款率 |
| ads_spend | DECIMAL(10,2) | 广告花费 |
| ads_roi | DECIMAL(8,4) | 广告ROI |
| recorded_at | TIMESTAMP | 记录时间 |

**唯一索引：** `(shop_id, metric_date)`

---

## 三、商品域（5张表）

### 3.1 PRODUCTS — 商品表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 商品ID |
| tenant_id | UUID FK | 租户ID |
| shop_id | UUID FK | 所属店铺 |
| platform_product_id | VARCHAR(100) | 平台商品ID（上架后回填） |
| title | VARCHAR(500) | 商品标题 |
| category_id | UUID FK | 分类ID |
| description | TEXT | 商品描述 |
| cost | DECIMAL(10,2) | 1688采购成本 |
| current_price | DECIMAL(10,2) | 当前售价 |
| status | VARCHAR(20) | on_sale/off_shelf/draft/deleted |
| source_url | TEXT | 1688来源链接 |
| platform_data | JSONB | 平台专属字段（各平台差异字段） |
| total_sales | INTEGER | 累计销量 |
| avg_rating | DECIMAL(3,2) | 平均评分 |
| listed_at | TIMESTAMP | 上架时间 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

### 3.2 PRODUCT_CATEGORIES — 商品分类表

支持多级分类，自关联设计。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 分类ID |
| tenant_id | UUID FK | 租户ID |
| name | VARCHAR(100) | 分类名称 |
| parent_id | UUID FK | 父分类ID，NULL为顶级分类 |
| level | INTEGER | 层级深度（1/2/3） |
| created_at | TIMESTAMP | 创建时间 |

---

### 3.3 SKUS — SKU表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | SKU ID |
| product_id | UUID FK | 所属商品 |
| platform_sku_id | VARCHAR(100) | 平台SKU ID |
| attributes | JSONB | `{"颜色":"红色","尺码":"M"}` |
| price | DECIMAL(10,2) | SKU售价 |
| cost | DECIMAL(10,2) | SKU成本（不同规格可能不同） |
| stock | INTEGER | 库存数量 |
| barcode | VARCHAR(50) | 条形码 |
| status | VARCHAR(20) | active/inactive |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

### 3.4 COMPETITOR_PRICES — 竞品价格表

定价Agent的核心数据源，每次巡检写入一条新记录（保留历史）。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 记录ID |
| product_id | UUID FK | 我方商品ID |
| platform | VARCHAR(20) | 竞品所在平台 |
| competitor_shop_id | VARCHAR(100) | 竞品店铺ID |
| competitor_shop_name | VARCHAR(200) | 竞品店铺名 |
| competitor_product_id | VARCHAR(100) | 竞品商品ID |
| price | DECIMAL(10,2) | 竞品价格 |
| monthly_sales | INTEGER | 竞品月销量 |
| rating | DECIMAL(3,2) | 竞品评分 |
| recorded_at | TIMESTAMP | 采集时间 |

**索引：** `(product_id, recorded_at DESC)`（用于获取最新竞品价）

---

### 3.5 SELECTION_REPORTS — 选品报告表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 报告ID |
| tenant_id | UUID FK | 租户ID |
| source_url | TEXT | 1688商品链接 |
| keyword | VARCHAR(200) | 搜索关键词 |
| product_data | JSONB | 原始1688商品数据 |
| overall_score | INTEGER | 综合评分0-100 |
| platform_scores | JSONB | 各平台分析评分 |
| profit_estimate | JSONB | 利润预估 |
| risks | JSONB | 风险列表 |
| recommendation | VARCHAR(20) | strong_buy/buy/hold/pass |
| status | VARCHAR(20) | pending/reviewed/adopted/rejected |
| reviewed_by | UUID FK | 审核人ID |
| reviewed_at | TIMESTAMP | 审核时间 |
| created_at | TIMESTAMP | 创建时间 |

---

## 四、订单域（5张表）

### 4.1 ORDERS — 订单表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 订单ID |
| tenant_id | UUID FK | 租户ID |
| shop_id | UUID FK | 店铺ID |
| product_id | UUID FK | 商品ID |
| sku_id | UUID FK | SKU ID |
| platform_order_id | VARCHAR(100) UNIQUE | 平台订单号 |
| quantity | INTEGER | 购买数量 |
| sale_price | DECIMAL(10,2) | 成交单价 |
| total_amount | DECIMAL(10,2) | 订单总金额 |
| refund_amount | DECIMAL(10,2) | 退款金额，默认0 |
| status | VARCHAR(20) | pending/paid/shipped/completed/refunding/refunded/cancelled |
| fulfillment_type | VARCHAR(20) | 1688_dropship/self_warehouse/supplier_direct |
| buyer_encrypted | TEXT | AES加密的买家信息（姓名/地址/电话） |
| paid_at | TIMESTAMP | 付款时间 |
| shipped_at | TIMESTAMP | 发货时间 |
| completed_at | TIMESTAMP | 确认收货时间 |
| created_at | TIMESTAMP | 订单创建时间 |

---

### 4.2 LOGISTICS — 物流表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 物流ID |
| order_id | UUID FK | 订单ID（一对一） |
| carrier | VARCHAR(50) | 快递公司（顺丰/韵达等） |
| tracking_no | VARCHAR(100) | 快递单号 |
| status | VARCHAR(20) | pending/picked_up/in_transit/delivered/exception |
| tracking_history | JSONB | 物流轨迹记录数组 |
| shipped_at | TIMESTAMP | 揽收时间 |
| delivered_at | TIMESTAMP | 签收时间 |
| updated_at | TIMESTAMP | 状态更新时间 |

---

### 4.3 SUPPLIERS — 供应商表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 供应商ID |
| tenant_id | UUID FK | 租户ID |
| name | VARCHAR(100) | 供应商名称 |
| platform | VARCHAR(20) | 1688/wechat/offline |
| platform_supplier_id | VARCHAR(100) | 1688店铺ID |
| contact_name | VARCHAR(50) | 联系人姓名 |
| contact_wechat | VARCHAR(50) | 微信账号（用于虚拟机通知） |
| contact_phone | VARCHAR(20) | 联系电话 |
| avg_ship_days | DECIMAL(4,1) | 平均发货天数 |
| quality_score | DECIMAL(3,2) | 质量评分1-5 |
| status | VARCHAR(20) | active/inactive |
| created_at | TIMESTAMP | 创建时间 |

---

### 4.4 PRODUCT_SUPPLIERS — 商品供应商关联表

一个商品可以有多个供应商，支持主供应商和备用供应商。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 关联ID |
| product_id | UUID FK | 商品ID |
| supplier_id | UUID FK | 供应商ID |
| supply_price | DECIMAL(10,2) | 该供应商的供货价 |
| min_order_qty | INTEGER | 最小起订量 |
| lead_days | INTEGER | 备货周期（天） |
| is_primary | BOOLEAN | 是否为主供应商 |
| created_at | TIMESTAMP | 创建时间 |

---

### 4.5 SHIPMENT_RECORDS — 发货通知记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 记录ID |
| order_id | UUID FK | 订单ID |
| supplier_id | UUID FK | 通知的供应商 |
| channel | VARCHAR(20) | 1688_auto/wechat_notify/manual |
| status | VARCHAR(20) | pending/notified/confirmed/shipped |
| message_content | TEXT | 发送的通知内容 |
| screenshot_url | TEXT | 操作截图URL（微信发消息截图） |
| notified_at | TIMESTAMP | 通知发出时间 |
| confirmed_at | TIMESTAMP | 供应商确认时间 |
| created_at | TIMESTAMP | 创建时间 |

---

## 五、Agent任务域（5张表）

### 5.1 AGENT_TASKS — Agent任务表

系统中所有Agent决策的主记录表。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 任务ID |
| tenant_id | UUID FK | 租户ID |
| shop_id | UUID FK | 关联店铺（可为NULL，如全局选品任务） |
| agent_type | VARCHAR(50) | selection/pricing/inventory/ads/cs/content/image/video |
| task_type | VARCHAR(100) | 具体任务类型（如`price_follow`/`batch_upload`） |
| trigger | VARCHAR(20) | scheduled/event/manual/user_command |
| input_data | JSONB | 任务输入数据 |
| decisions | JSONB | Agent推理决策内容 |
| actions | JSONB | 待执行动作列表（含risk_level） |
| status | VARCHAR(20) | pending/pending_approval/approved/executing/done/failed/cancelled |
| retry_count | INTEGER | 重试次数，默认0 |
| error_message | TEXT | 失败原因 |
| result | JSONB | 执行结果 |
| started_at | TIMESTAMP | 开始执行时间 |
| completed_at | TIMESTAMP | 完成时间 |
| created_at | TIMESTAMP | 创建时间 |

**索引：** `(tenant_id, status, created_at DESC)`

---

### 5.2 APPROVAL_TASKS — 审批队列表

高风险Agent决策在执行前推入审批队列，等待人工确认。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 审批ID |
| tenant_id | UUID FK | 租户ID |
| agent_task_id | UUID FK | 关联的Agent任务 |
| shop_id | UUID FK | 关联店铺 |
| priority | INTEGER | 优先级，1最高，5默认 |
| title | VARCHAR(200) | 审批标题（推送到手机端显示） |
| description | TEXT | 决策详情说明 |
| options | JSONB | `[{"label":"同意","action":"approve"},...]` |
| status | VARCHAR(20) | pending/approved/rejected/modified/expired |
| decided_by | UUID FK | 审批人用户ID |
| decision_detail | JSONB | 审批结果及修改内容 |
| expires_at | TIMESTAMP | 超时时间（超时自动执行默认策略） |
| decided_at | TIMESTAMP | 审批时间 |
| created_at | TIMESTAMP | 创建时间 |

**索引：** `(tenant_id, status, priority, created_at)`

---

### 5.3 RPA_OPERATIONS — RPA操作记录表

每一个具体的RPA操作（点击、输入、截图等）记录一条。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 操作ID |
| tenant_id | UUID FK | 租户ID |
| agent_task_id | UUID FK | 所属Agent任务 |
| shop_id | UUID FK | 操作的店铺 |
| platform | VARCHAR(20) | 操作的平台 |
| operation_type | VARCHAR(50) | click/type/navigate/scrape/screenshot/wait |
| operation_params | JSONB | 操作参数（选择器/输入内容等） |
| status | VARCHAR(20) | pending/running/success/failed/retrying |
| screenshot_url | TEXT | 操作结果截图URL |
| retry_count | INTEGER | 重试次数 |
| error_message | TEXT | 错误信息 |
| duration_ms | INTEGER | 操作耗时（毫秒） |
| started_at | TIMESTAMP | 开始时间 |
| completed_at | TIMESTAMP | 完成时间 |

---

### 5.4 OPERATION_LOGS — 操作日志表

RPA操作的详细日志，用于调试和审计。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 日志ID |
| tenant_id | UUID FK | 租户ID |
| rpa_operation_id | UUID FK | 关联RPA操作 |
| level | VARCHAR(10) | info/warn/error |
| message | TEXT | 日志内容 |
| context | JSONB | 额外上下文信息 |
| logged_at | TIMESTAMP | 记录时间 |

**保留策略：** 日志保留90天，定期归档。

---

### 5.5 USER_COMMANDS — 用户自然语言指令表

记录用户通过手机端输入的自然语言指令及解析结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 指令ID |
| tenant_id | UUID FK | 租户ID |
| user_id | UUID FK | 发出指令的用户 |
| channel | VARCHAR(20) | mobile/desktop |
| raw_input | TEXT | 用户原始输入文字 |
| parsed_intent | JSONB | Agnes AI解析结果（意图/参数/目标店铺） |
| target_agent | VARCHAR(50) | 路由到的Agent类型 |
| agent_task_id | UUID FK | 触发创建的任务ID |
| status | VARCHAR(20) | parsing/dispatched/done/failed |
| created_at | TIMESTAMP | 创建时间 |

---

## 六、内容域（7张表）

### 6.1 PRODUCT_IMAGES — 商品图片表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 图片ID |
| tenant_id | UUID FK | 租户ID |
| product_id | UUID FK | 商品ID |
| type | VARCHAR(30) | main/scene/white_bg/detail/xhs_style |
| platform | VARCHAR(20) | 适用平台（universal=通用） |
| url | TEXT | CDN访问URL |
| storage_path | TEXT | 对象存储路径 |
| width | INTEGER | 图片宽度（px） |
| height | INTEGER | 图片高度（px） |
| generation_method | VARCHAR(20) | comfyui/manual |
| generation_params | JSONB | ComfyUI工作流参数快照 |
| status | VARCHAR(20) | generating/ready/rejected |
| created_at | TIMESTAMP | 创建时间 |

---

### 6.2 PRODUCT_VIDEOS — 商品视频表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 视频ID |
| tenant_id | UUID FK | 租户ID |
| product_id | UUID FK | 商品ID |
| type | VARCHAR(20) | oral/showcase/composite |
| platform | VARCHAR(20) | 适用平台 |
| url | TEXT | CDN访问URL |
| storage_path | TEXT | 存储路径 |
| duration_seconds | INTEGER | 视频时长（秒） |
| aspect_ratio | VARCHAR(10) | 9:16/1:1/16:9 |
| persona_id | UUID FK | 使用的数字人形象ID |
| script_id | UUID FK | 使用的口播脚本ID |
| template_id | UUID FK | 参考的爆款模板ID |
| status | VARCHAR(20) | generating/ready/published/rejected |
| created_at | TIMESTAMP | 创建时间 |

---

### 6.3 ORAL_SCRIPTS — 口播脚本表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 脚本ID |
| tenant_id | UUID FK | 租户ID |
| product_id | UUID FK | 商品ID |
| template_id | UUID FK | 参考的爆款模板ID |
| script_content | TEXT | 口播脚本正文 |
| duration_seconds | INTEGER | 预估时长（秒） |
| tone | VARCHAR(20) | 亲切/专业/夸张/测评 |
| status | VARCHAR(20) | draft/approved/used |
| created_by | UUID FK | 创建人（AI生成时为NULL） |
| created_at | TIMESTAMP | 创建时间 |

---

### 6.4 VIRAL_TEMPLATES — 爆款视频模板表

由竞品视频分析后提炼，存储可复用的视频结构模板。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 模板ID |
| tenant_id | UUID FK | 租户ID |
| category | VARCHAR(100) | 适用品类（化妆品/百货等） |
| platform | VARCHAR(20) | 来源平台 |
| hook_type | VARCHAR(30) | 痛点型/好奇型/对比型/福利型 |
| structure | JSONB | 视频分段结构定义 |
| tone | VARCHAR(20) | 整体风格 |
| pacing | VARCHAR(20) | fast/slow |
| bgm_style | VARCHAR(50) | 背景音乐风格 |
| usage_count | INTEGER | 使用次数 |
| avg_performance_score | DECIMAL(5,2) | 基于此模板生成视频的平均表现分 |
| source_videos | JSONB | 参考的竞品视频ID列表 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

### 6.5 COMPETITOR_VIDEOS — 竞品视频表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 视频ID |
| tenant_id | UUID FK | 租户ID |
| platform | VARCHAR(20) | 来源平台 |
| original_url | TEXT | 原始视频URL |
| local_path | TEXT | 本地存储路径 |
| transcript | TEXT | Whisper转写的文字内容 |
| likes_count | INTEGER | 点赞数 |
| comments_count | INTEGER | 评论数 |
| shares_count | INTEGER | 分享数 |
| analyzed_template_id | UUID FK | 分析后生成的模板ID |
| status | VARCHAR(20) | downloaded/transcribed/analyzed |
| published_at | TIMESTAMP | 原视频发布时间 |
| downloaded_at | TIMESTAMP | 下载时间 |
| created_at | TIMESTAMP | 创建时间 |

---

### 6.6 PERSONAS — 数字人形象表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 形象ID |
| tenant_id | UUID FK | 租户ID |
| name | VARCHAR(50) | 形象名称（客户自定义） |
| image_url | TEXT | 照片CDN URL |
| image_path | TEXT | 存储路径 |
| usage_count | INTEGER | 使用次数 |
| last_used_at | TIMESTAMP | 最后使用时间（用于轮换策略） |
| status | VARCHAR(20) | active/inactive |
| created_at | TIMESTAMP | 创建时间 |

---

### 6.7 COPYWRITING — 文案表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 文案ID |
| tenant_id | UUID FK | 租户ID |
| product_id | UUID FK | 商品ID |
| platform | VARCHAR(20) | 适用平台 |
| type | VARCHAR(30) | title/description/bullet_points/seo_tags |
| content | TEXT | 文案内容 |
| status | VARCHAR(20) | draft/approved/published |
| created_by | UUID FK | 创建人（NULL=AI生成） |
| created_at | TIMESTAMP | 创建时间 |

---

## 七、广告域（4张表）

### 7.1 AD_CAMPAIGNS — 广告计划表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 计划ID |
| tenant_id | UUID FK | 租户ID |
| shop_id | UUID FK | 店铺ID |
| platform_campaign_id | VARCHAR(100) | 平台广告计划ID（RPA抓取） |
| name | VARCHAR(200) | 计划名称 |
| platform | VARCHAR(20) | 平台 |
| type | VARCHAR(20) | search/display/live |
| status | VARCHAR(20) | active/paused/ended |
| daily_budget | DECIMAL(10,2) | 日预算（元） |
| total_budget | DECIMAL(10,2) | 总预算（元） |
| start_date | DATE | 开始日期 |
| end_date | DATE | 结束日期 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

### 7.2 AD_GROUPS — 广告组表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 广告组ID |
| campaign_id | UUID FK | 所属计划 |
| platform_group_id | VARCHAR(100) | 平台广告组ID |
| name | VARCHAR(200) | 广告组名称 |
| bid_price | DECIMAL(10,2) | 出价（元） |
| bid_strategy | VARCHAR(20) | manual/auto/target_roi |
| target_roi | DECIMAL(8,4) | 目标ROI（target_roi策略时生效） |
| status | VARCHAR(20) | active/paused |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

### 7.3 AD_KEYWORDS — 广告关键词表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 关键词ID |
| ad_group_id | UUID FK | 所属广告组 |
| keyword | VARCHAR(200) | 关键词文本 |
| match_type | VARCHAR(10) | exact/phrase/broad |
| bid_price | DECIMAL(10,2) | 关键词出价（覆盖组出价） |
| status | VARCHAR(20) | active/paused/negative（否定关键词） |
| created_at | TIMESTAMP | 创建时间 |

---

### 7.4 AD_STATS — 广告数据统计表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 统计ID |
| tenant_id | UUID FK | 租户ID |
| campaign_id | UUID FK | 广告计划ID |
| ad_group_id | UUID FK | 广告组ID（可为NULL，计划级汇总） |
| stat_date | DATE | 统计日期 |
| impressions | INTEGER | 展现量 |
| clicks | INTEGER | 点击量 |
| spend | DECIMAL(10,2) | 花费（元） |
| conversions | INTEGER | 转化数 |
| revenue | DECIMAL(12,2) | 转化金额 |
| ctr | DECIMAL(8,6) | 点击率 |
| cvr | DECIMAL(8,6) | 转化率 |
| roi | DECIMAL(8,4) | ROI |
| cpc | DECIMAL(10,4) | 平均点击成本 |
| recorded_at | TIMESTAMP | 记录时间 |

**唯一索引：** `(campaign_id, ad_group_id, stat_date)`

---

### 7.5 AD_OPTIMIZATION_RECORDS — 广告优化记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 记录ID |
| tenant_id | UUID FK | 租户ID |
| agent_task_id | UUID FK | 关联Agent任务 |
| campaign_id | UUID FK | 广告计划 |
| action_type | VARCHAR(30) | bid_adjust/pause_keyword/add_keyword/budget_adjust |
| before_state | JSONB | 调整前状态快照 |
| after_state | JSONB | 调整后状态 |
| reason | TEXT | 优化依据（AI生成） |
| status | VARCHAR(20) | pending_approval/executed/rolled_back |
| executed_at | TIMESTAMP | 执行时间 |
| created_at | TIMESTAMP | 创建时间 |

---

## 八、客服域（5张表）

### 8.1 CS_SESSIONS — 客服会话表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 会话ID |
| tenant_id | UUID FK | 租户ID |
| shop_id | UUID FK | 店铺ID |
| platform_session_id | VARCHAR(100) | 平台会话ID |
| buyer_id | VARCHAR(100) | 平台买家ID（脱敏处理） |
| status | VARCHAR(20) | open/ai_handling/escalated/closed |
| escalation_reason | VARCHAR(200) | 转人工原因 |
| assigned_to | UUID FK | 转人工后的处理人ID |
| sentiment_score | DECIMAL(4,3) | 情绪评分（-1.0到1.0） |
| message_count | INTEGER | 消息总数 |
| opened_at | TIMESTAMP | 会话开始时间 |
| closed_at | TIMESTAMP | 会话结束时间 |
| created_at | TIMESTAMP | 创建时间 |

---

### 8.2 CS_MESSAGES — 客服消息表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 消息ID |
| session_id | UUID FK | 所属会话 |
| sender_type | VARCHAR(10) | buyer/ai/human |
| content | TEXT | 消息内容 |
| reply_type | VARCHAR(20) | auto/manual/template（AI回复分类） |
| confidence_score | DECIMAL(4,3) | AI回复置信度（0-1） |
| was_edited | BOOLEAN | 人工是否修改过AI回复 |
| sent_at | TIMESTAMP | 发送时间 |

---

### 8.3 CS_KNOWLEDGE_BASE — 客服知识库表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 知识ID |
| shop_id | UUID FK | 所属店铺 |
| type | VARCHAR(30) | product_info/platform_rule/faq/return_policy |
| title | VARCHAR(200) | 知识标题 |
| content | TEXT | 知识内容 |
| metadata | JSONB | 额外元数据（来源/有效期等） |
| hit_count | INTEGER | 被引用次数 |
| status | VARCHAR(20) | active/outdated |
| last_updated_at | TIMESTAMP | 内容最后更新时间 |
| created_at | TIMESTAMP | 创建时间 |

---

### 8.4 CS_FAQ — 常见问题表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | FAQ ID |
| shop_id | UUID FK | 所属店铺 |
| knowledge_base_id | UUID FK | 关联知识库 |
| question | TEXT | 标准问题 |
| answer | TEXT | 标准答案 |
| question_variants | JSONB | 问法变体列表（用于模糊匹配） |
| hit_count | INTEGER | 匹配命中次数 |
| avg_satisfaction | DECIMAL(3,2) | 平均满意度评分 |
| status | VARCHAR(20) | active/inactive |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

### 8.5 CS_REVIEWS — 评价管理表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 评价ID |
| tenant_id | UUID FK | 租户ID |
| shop_id | UUID FK | 店铺ID |
| order_id | UUID FK | 关联订单 |
| platform_review_id | VARCHAR(100) | 平台评价ID |
| rating | INTEGER | 星级评分（1-5） |
| content | TEXT | 评价内容 |
| sentiment | VARCHAR(20) | positive/neutral/negative |
| status | VARCHAR(20) | normal/needs_attention/replied |
| reply_content | TEXT | 回复内容 |
| is_auto_replied | BOOLEAN | 是否AI自动回复 |
| review_at | TIMESTAMP | 买家评价时间 |
| replied_at | TIMESTAMP | 回复时间 |
| created_at | TIMESTAMP | 创建时间 |

---

## 附录：索引策略汇总

```sql
-- 高频查询索引
CREATE INDEX idx_shops_tenant ON shops(tenant_id, status);
CREATE INDEX idx_products_shop ON products(shop_id, status);
CREATE INDEX idx_orders_shop_status ON orders(shop_id, status, created_at DESC);
CREATE INDEX idx_agent_tasks_tenant_status ON agent_tasks(tenant_id, status, created_at DESC);
CREATE INDEX idx_approval_tasks_pending ON approval_tasks(tenant_id, status, priority) WHERE status = 'pending';
CREATE INDEX idx_competitor_prices_product ON competitor_prices(product_id, recorded_at DESC);
CREATE INDEX idx_usage_records_tenant_type ON usage_records(tenant_id, resource_type, recorded_at DESC);
CREATE INDEX idx_cs_sessions_shop_status ON cs_sessions(shop_id, status);
CREATE INDEX idx_ad_stats_campaign_date ON ad_stats(campaign_id, stat_date DESC);
CREATE INDEX idx_rpa_ops_task ON rpa_operations(agent_task_id, status);

-- PostgreSQL RLS行级安全策略（关键业务表）
ALTER TABLE shops ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_tasks ENABLE ROW LEVEL SECURITY;

-- RLS策略示例
CREATE POLICY tenant_isolation_shops ON shops
    USING (tenant_id = current_setting('app.tenant_id')::UUID);
```

---

*文档版本：v1.0 | 共46张表，8个业务域 | 配合ER图-完整数据库设计.mermaid使用*

---

# 第三部分：API接口文档

**版本：** v1.0  
**Base URL：** `http://localhost:8765/api/v1`（本地部署）  
**协议：** HTTP/1.1 + WebSocket  
**认证：** JWT Bearer Token  
**数据格式：** JSON  

---

## 通用规范

### 请求头

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Tenant-ID: <tenant_id>   # 可选，JWT中已包含，调试用
```

### 统一响应结构

```json
// 成功
{
  "code": 0,
  "message": "success",
  "data": { ... }
}

// 失败
{
  "code": 40001,
  "message": "店铺数量已达套餐上限",
  "data": null
}
```

### 错误码规范

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 40001 | 参数错误 |
| 40100 | 未登录/Token无效 |
| 40300 | 无权限 |
| 40400 | 资源不存在 |
| 42900 | 套餐限制（店铺数/额度不足） |
| 50000 | 服务器内部错误 |
| 50100 | RPA执行失败 |
| 50200 | Agent推理失败 |

### 分页规范

```json
// 请求
GET /api/v1/products?page=1&page_size=20&sort=created_at&order=desc

// 响应
{
  "code": 0,
  "data": {
    "items": [ ... ],
    "total": 156,
    "page": 1,
    "page_size": 20,
    "total_pages": 8
  }
}
```

---

## 一、认证模块 `/auth`

### 1.1 注册

```
POST /auth/register
```

**Request:**
```json
{
  "name": "张三电商",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "password": "Abc123456",
  "invite_code": "XXXX"    // 可选，邀请码
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "tenant_id": "uuid",
    "user_id": "uuid",
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "expires_in": 86400,
    "trial_ends_at": "2024-02-01T00:00:00Z"  // 7天试用
  }
}
```

---

### 1.2 登录

```
POST /auth/login
```

**Request:**
```json
{
  "email": "zhangsan@example.com",
  "password": "Abc123456"
}
```

**Response:** 同注册，返回Token信息

---

### 1.3 刷新Token

```
POST /auth/refresh
```

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "access_token": "eyJ...",
    "expires_in": 86400
  }
}
```

---

### 1.4 获取当前用户信息

```
GET /auth/me
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "user_id": "uuid",
    "tenant_id": "uuid",
    "name": "张三",
    "email": "zhangsan@example.com",
    "role": "owner",
    "tenant": {
      "name": "张三电商",
      "status": "active",
      "plan": "growth",
      "trial_ends_at": null
    },
    "quota": {
      "shops": { "used": 8, "max": 15 },
      "images": { "used": 320, "max": 500 },
      "videos": { "used": 12, "max": 50 },
      "video_analysis": { "used": 45, "max": 300 }
    }
  }
}
```

---

### 1.5 修改密码

```
POST /auth/change-password
```

**Request:**
```json
{
  "old_password": "Abc123456",
  "new_password": "Xyz789012"
}
```

---

## 二、店铺模块 `/shops`

### 2.1 获取店铺列表

```
GET /shops
```

**Query Params:**
```
platform=pdd              // 可选，按平台筛选
status=active             // 可选，按状态筛选
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "我的拼多多3店",
        "platform": "pdd",
        "platform_shop_name": "好货优选旗舰店",
        "status": "active",
        "cookie_expires_at": "2024-03-01T00:00:00Z",
        "last_synced_at": "2024-01-15T08:30:00Z",
        "today_metrics": {
          "orders": 23,
          "revenue": 1580.50,
          "visitors": 456
        }
      }
    ],
    "total": 11
  }
}
```

---

### 2.2 发起店铺绑定（获取登录二维码）

```
POST /shops/bind/init
```

**Request:**
```json
{
  "platform": "pdd",
  "name": "拼多多7号店"    // 用户自定义备注名
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "session_id": "uuid",          // 绑定会话ID，后续轮询用
    "qrcode_base64": "data:image/png;base64,iVBOR...",
    "qrcode_expires_in": 120       // 二维码有效期（秒）
  }
}
```

---

### 2.3 轮询绑定状态

```
GET /shops/bind/status/{session_id}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "status": "waiting",   // waiting/scanned/success/expired/failed
    "shop_id": null,       // 成功后返回shop_id
    "message": "等待扫码"
  }
}
```

**status流转：** `waiting` → `scanned`（已扫码未确认）→ `success` / `expired` / `failed`

---

### 2.4 获取店铺详情

```
GET /shops/{shop_id}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "name": "拼多多3店",
    "platform": "pdd",
    "platform_shop_id": "12345678",
    "platform_shop_name": "好货优选旗舰店",
    "status": "active",
    "cookie_expires_at": "2024-03-01T00:00:00Z",
    "config": {
      "min_margin": 0.15,
      "max_ads_daily_budget": 500,
      "auto_price_follow": true,
      "cs_auto_reply": true,
      "price_floor": 10.0
    },
    "last_synced_at": "2024-01-15T08:30:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### 2.5 更新店铺配置

```
PATCH /shops/{shop_id}/config
```

**Request:**
```json
{
  "min_margin": 0.20,
  "auto_price_follow": false,
  "max_ads_daily_budget": 300
}
```

---

### 2.6 暂停/恢复店铺Agent

```
POST /shops/{shop_id}/pause
POST /shops/{shop_id}/resume
```

---

### 2.7 重新绑定（Cookie过期时）

```
POST /shops/{shop_id}/rebind
```

**Response:** 同 2.2，返回新二维码

---

### 2.8 解绑店铺

```
DELETE /shops/{shop_id}
```

**Response:**
```json
{
  "code": 0,
  "data": { "message": "店铺已解绑" }
}
```

---

### 2.9 获取店铺日报数据

```
GET /shops/{shop_id}/metrics
```

**Query Params:**
```
start_date=2024-01-01
end_date=2024-01-15
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "metric_date": "2024-01-15",
        "total_orders": 23,
        "total_revenue": 1580.50,
        "total_visitors": 456,
        "conversion_rate": 0.0504,
        "refund_rate": 0.0087,
        "ads_spend": 120.00,
        "ads_roi": 3.25
      }
    ]
  }
}
```

---

## 三、商品模块 `/products`

### 3.1 获取商品列表

```
GET /products
```

**Query Params:**
```
shop_id=uuid
status=on_sale
category_id=uuid
keyword=连衣裙
page=1
page_size=20
sort=total_sales
order=desc
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "shop_id": "uuid",
        "platform_product_id": "123456",
        "title": "夏季新款连衣裙女",
        "current_price": 49.90,
        "cost": 22.00,
        "status": "on_sale",
        "total_sales": 1580,
        "avg_rating": 4.8,
        "main_image_url": "https://cdn.example.com/...",
        "listed_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 156,
    "page": 1,
    "page_size": 20,
    "total_pages": 8
  }
}
```

---

### 3.2 获取商品详情

```
GET /products/{product_id}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "shop_id": "uuid",
    "title": "夏季新款连衣裙女",
    "description": "...",
    "cost": 22.00,
    "current_price": 49.90,
    "status": "on_sale",
    "source_url": "https://detail.1688.com/...",
    "skus": [
      {
        "id": "uuid",
        "attributes": { "颜色": "红色", "尺码": "M" },
        "price": 49.90,
        "stock": 100
      }
    ],
    "images": [
      {
        "id": "uuid",
        "type": "main",
        "url": "https://cdn.example.com/..."
      }
    ],
    "competitor_prices": [
      {
        "competitor_shop_name": "竞品店铺A",
        "price": 45.00,
        "monthly_sales": 2300,
        "recorded_at": "2024-01-15T08:00:00Z"
      }
    ],
    "total_sales": 1580,
    "avg_rating": 4.8,
    "listed_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### 3.3 创建商品（从1688链接导入）

```
POST /products/import
```

**Request:**
```json
{
  "shop_id": "uuid",
  "source_url": "https://detail.1688.com/offer/123456.html",
  "cost_override": 22.00,       // 可选，覆盖1688价格
  "auto_generate_content": true  // 是否自动触发AI生成图片/文案
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "product_id": "uuid",
    "task_id": "uuid",    // 内容生成任务ID
    "status": "importing"
  }
}
```

---

### 3.4 批量上架

```
POST /products/batch-upload
```

**Request:**
```json
{
  "product_ids": ["uuid1", "uuid2", "uuid3"],
  "platforms": ["pdd", "taobao"],   // 可选，不传则上架到商品所属店铺
  "schedule_at": null               // 可选，定时上架时间
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "task_id": "uuid",
    "total": 3,
    "message": "批量上架任务已创建，预计10分钟内完成"
  }
}
```

---

### 3.5 更新商品价格

```
PATCH /products/{product_id}/price
```

**Request:**
```json
{
  "price": 45.90,
  "sku_prices": [           // 可选，SKU级别定价
    {
      "sku_id": "uuid",
      "price": 45.90
    }
  ]
}
```

---

### 3.6 下架商品

```
POST /products/{product_id}/off-shelf
```

---

### 3.7 获取选品报告列表

```
GET /products/selection-reports
```

**Query Params:**
```
status=pending
recommendation=strong_buy
page=1
page_size=20
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "keyword": "夏季连衣裙",
        "overall_score": 82,
        "recommendation": "strong_buy",
        "profit_estimate": {
          "cost": 22.00,
          "avg_sell_price": 49.90,
          "gross_margin": "55.9%"
        },
        "platform_scores": {
          "pdd": { "score": 85, "suggested_price": 39.90 },
          "taobao": { "score": 78, "suggested_price": 49.90 },
          "douyin": { "score": 72, "suggested_price": 55.00 }
        },
        "status": "pending",
        "created_at": "2024-01-15T08:00:00Z"
      }
    ]
  }
}
```

---

### 3.8 审核选品报告

```
POST /products/selection-reports/{report_id}/review
```

**Request:**
```json
{
  "status": "adopted",    // adopted/rejected
  "note": "好品，安排上架",
  "target_shops": ["uuid1", "uuid2"]  // adopted时指定上架店铺
}
```

---

## 四、订单模块 `/orders`

### 4.1 获取订单列表

```
GET /orders
```

**Query Params:**
```
shop_id=uuid
status=paid
fulfillment_type=1688_dropship
start_date=2024-01-01
end_date=2024-01-15
page=1
page_size=20
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "platform_order_id": "PDD20240115001",
        "shop_name": "拼多多3店",
        "product_title": "夏季新款连衣裙女",
        "sku_attributes": { "颜色": "红色", "尺码": "M" },
        "quantity": 2,
        "total_amount": 99.80,
        "status": "paid",
        "fulfillment_type": "1688_dropship",
        "paid_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 89,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

---

### 4.2 获取订单详情

```
GET /orders/{order_id}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "platform_order_id": "PDD20240115001",
    "shop": { "id": "uuid", "name": "拼多多3店" },
    "product": { "id": "uuid", "title": "夏季新款连衣裙女" },
    "sku": { "attributes": { "颜色": "红色", "尺码": "M" } },
    "quantity": 2,
    "sale_price": 49.90,
    "total_amount": 99.80,
    "status": "paid",
    "fulfillment_type": "1688_dropship",
    "logistics": null,
    "shipment_records": [],
    "paid_at": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-15T10:28:00Z"
  }
}
```

---

### 4.3 手动触发发货

```
POST /orders/{order_id}/ship
```

**Request:**
```json
{
  "fulfillment_type": "supplier_direct",
  "supplier_id": "uuid",
  "note": "加急处理"
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "shipment_record_id": "uuid",
    "task_id": "uuid",
    "message": "发货任务已创建"
  }
}
```

---

### 4.4 回填物流单号

```
POST /orders/{order_id}/logistics
```

**Request:**
```json
{
  "carrier": "韵达",
  "tracking_no": "YD1234567890"
}
```

---

### 4.5 订单统计汇总

```
GET /orders/summary
```

**Query Params:**
```
shop_id=uuid        // 可选
start_date=2024-01-01
end_date=2024-01-15
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "total_orders": 89,
    "total_revenue": 8920.50,
    "total_cost": 4100.00,
    "gross_profit": 4820.50,
    "gross_margin": "54.0%",
    "avg_order_value": 100.23,
    "refund_rate": "1.2%",
    "by_status": {
      "paid": 12,
      "shipped": 45,
      "completed": 28,
      "refunding": 4
    },
    "by_fulfillment": {
      "1688_dropship": 60,
      "self_warehouse": 20,
      "supplier_direct": 9
    }
  }
}
```

---

## 五、Agent任务模块 `/tasks`

### 5.1 获取任务列表

```
GET /tasks
```

**Query Params:**
```
agent_type=pricing
status=pending_approval
shop_id=uuid
page=1
page_size=20
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "shop_name": "拼多多3店",
        "agent_type": "pricing",
        "task_type": "price_follow",
        "trigger": "scheduled",
        "status": "pending_approval",
        "summary": "检测到竞品降价，建议跟价3个SKU",
        "created_at": "2024-01-15T14:00:00Z"
      }
    ],
    "total": 34,
    "page": 1,
    "page_size": 20,
    "total_pages": 2
  }
}
```

---

### 5.2 获取任务详情

```
GET /tasks/{task_id}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "shop": { "id": "uuid", "name": "拼多多3店" },
    "agent_type": "pricing",
    "task_type": "price_follow",
    "trigger": "scheduled",
    "input_data": {
      "product_id": "uuid",
      "current_price": 49.90,
      "competitor_prices": [
        { "shop": "竞品A", "price": 39.90 }
      ]
    },
    "decisions": {
      "analysis": "竞品A降价20%，当前价格竞争力不足",
      "suggested_price": 41.90,
      "confidence": 0.85
    },
    "actions": [
      {
        "type": "update_price",
        "product_id": "uuid",
        "current_price": 49.90,
        "new_price": 41.90,
        "change_pct": -16.0,
        "risk_level": "high"
      }
    ],
    "status": "pending_approval",
    "rpa_operations": [],
    "created_at": "2024-01-15T14:00:00Z"
  }
}
```

---

### 5.3 手动触发Agent任务

```
POST /tasks
```

**Request:**
```json
{
  "shop_id": "uuid",
  "agent_type": "selection",
  "task_type": "scan_1688",
  "params": {
    "keyword": "夏季连衣裙",
    "max_results": 20
  }
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "task_id": "uuid",
    "status": "pending",
    "estimated_duration": "3-5分钟"
  }
}
```

---

### 5.4 获取任务RPA操作记录

```
GET /tasks/{task_id}/operations
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "operation_type": "navigate",
        "operation_params": { "url": "https://seller.pinduoduo.com/..." },
        "status": "success",
        "screenshot_url": "https://cdn.example.com/screenshots/...",
        "duration_ms": 1240,
        "started_at": "2024-01-15T14:01:00Z"
      }
    ]
  }
}
```

---

### 5.5 取消任务

```
POST /tasks/{task_id}/cancel
```

---

## 六、审批模块 `/approvals`

### 6.1 获取待审批列表

```
GET /approvals/pending
```

**Query Params:**
```
shop_id=uuid     // 可选
priority=1       // 可选，筛选高优先级
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "agent_task_id": "uuid",
        "shop_name": "拼多多3店",
        "priority": 2,
        "title": "定价调整审批",
        "description": "竞品降价20%，建议将「夏季连衣裙」从¥49.9调整至¥41.9",
        "options": [
          { "label": "同意", "action": "approve" },
          { "label": "修改价格", "action": "modify" },
          { "label": "拒绝", "action": "reject" }
        ],
        "expires_at": "2024-01-15T16:00:00Z",
        "created_at": "2024-01-15T14:00:00Z"
      }
    ],
    "total": 5
  }
}
```

---

### 6.2 审批决策

```
POST /approvals/{approval_id}/decide
```

**Request:**
```json
{
  "action": "approve",
  "note": "同意跟价",
  "modifications": null   // action=modify时传入修改内容
}
```

**modifications示例（修改价格）：**
```json
{
  "modifications": {
    "new_price": 43.90    // 人工改为43.9而非Agent建议的41.9
  }
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "approval_id": "uuid",
    "action": "approve",
    "agent_task_id": "uuid",
    "message": "审批通过，RPA将在30秒内执行"
  }
}
```

---

### 6.3 批量审批

```
POST /approvals/batch-decide
```

**Request:**
```json
{
  "approval_ids": ["uuid1", "uuid2", "uuid3"],
  "action": "approve",
  "note": "批量同意"
}
```

---

### 6.4 获取审批历史

```
GET /approvals/history
```

**Query Params:**
```
start_date=2024-01-01
end_date=2024-01-15
action=approve
page=1
page_size=20
```

---

## 七、自然语言指令模块 `/commands`

### 7.1 发送自然语言指令

```
POST /commands/natural
```

**Request:**
```json
{
  "input": "把所有拼多多店的连衣裙降价5%，但不能低于30块",
  "channel": "mobile"
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "command_id": "uuid",
    "parsed_intent": {
      "action": "batch_price_adjust",
      "platform": "pdd",
      "category": "连衣裙",
      "adjustment": "-5%",
      "price_floor": 30.0,
      "target_shops": ["uuid1", "uuid2", "uuid3"],
      "affected_skus": 23
    },
    "confirmation_required": true,
    "confirmation_message": "将对6个拼多多店铺的23个连衣裙SKU降价5%，最低不低于¥30，是否确认执行？",
    "status": "awaiting_confirmation"
  }
}
```

---

### 7.2 确认执行指令

```
POST /commands/{command_id}/confirm
```

**Request:**
```json
{
  "confirmed": true
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "task_id": "uuid",
    "message": "已创建批量调价任务，预计5分钟内完成"
  }
}
```

---

### 7.3 获取指令历史

```
GET /commands/history
```

**Query Params:**
```
page=1
page_size=20
```

---

## 八、内容模块 `/content`

### 8.1 触发AI图片生成

```
POST /content/images/generate
```

**Request:**
```json
{
  "product_id": "uuid",
  "types": ["main", "scene", "white_bg"],
  "platforms": ["pdd", "taobao", "douyin"],
  "style_overrides": {
    "scene_description": "夏日海边度假场景",
    "color_tone": "warm"
  }
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "task_id": "uuid",
    "estimated_duration": "2-3分钟",
    "quota_used": 3,
    "quota_remaining": 177
  }
}
```

---

### 8.2 获取商品图片列表

```
GET /content/images
```

**Query Params:**
```
product_id=uuid
type=main
platform=pdd
status=ready
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "type": "main",
        "platform": "pdd",
        "url": "https://cdn.example.com/...",
        "width": 800,
        "height": 800,
        "status": "ready",
        "created_at": "2024-01-15T10:00:00Z"
      }
    ]
  }
}
```

---

### 8.3 触发口播视频生成

```
POST /content/videos/generate
```

**Request:**
```json
{
  "product_id": "uuid",
  "platform": "douyin",
  "persona_id": "uuid",
  "template_id": "uuid",     // 可选，不传则自动选最优模板
  "script_override": null,   // 可选，手动输入脚本跳过AI生成
  "duration": 30             // 目标时长（秒），15/30/60
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "task_id": "uuid",
    "estimated_duration": "5-8分钟",
    "quota_used": 1,
    "quota_remaining": 49
  }
}
```

---

### 8.4 触发竞品视频分析

```
POST /content/videos/analyze-competitor
```

**Request:**
```json
{
  "platform": "douyin",
  "keyword": "夏季连衣裙",
  "count": 10,
  "min_likes": 10000
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "task_id": "uuid",
    "estimated_duration": "10-15分钟",
    "quota_used": 10,
    "quota_remaining": 290
  }
}
```

---

### 8.5 获取爆款模板列表

```
GET /content/viral-templates
```

**Query Params:**
```
category=化妆品
platform=douyin
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "category": "化妆品",
        "platform": "douyin",
        "hook_type": "痛点型",
        "tone": "亲切",
        "usage_count": 12,
        "avg_performance_score": 78.5,
        "structure": [
          { "time": "0-3s", "content": "痛点钩子" },
          { "time": "3-8s", "content": "问题展开" },
          { "time": "8-18s", "content": "产品展示" },
          { "time": "18-22s", "content": "促单话术" }
        ]
      }
    ]
  }
}
```

---

### 8.6 数字人形象管理

```
GET    /content/personas              // 获取形象列表
POST   /content/personas              // 上传新形象
DELETE /content/personas/{persona_id} // 删除形象
```

**POST Request:**
```json
{
  "name": "小王",
  "image_base64": "data:image/jpeg;base64,..."
}
```

---

### 8.7 获取文案列表

```
GET /content/copywriting
```

**Query Params:**
```
product_id=uuid
type=title
platform=pdd
status=approved
```

---

### 8.8 生成商品文案

```
POST /content/copywriting/generate
```

**Request:**
```json
{
  "product_id": "uuid",
  "types": ["title", "description", "seo_tags"],
  "platforms": ["pdd", "taobao"],
  "tone": "亲切",
  "keywords": ["夏季", "显瘦", "连衣裙"]
}
```

---

## 九、广告模块 `/ads`

### 9.1 获取广告计划列表

```
GET /ads/campaigns
```

**Query Params:**
```
shop_id=uuid
platform=pdd
status=active
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "夏季连衣裙推广",
        "platform": "pdd",
        "type": "search",
        "status": "active",
        "daily_budget": 200.00,
        "today_stats": {
          "spend": 85.30,
          "clicks": 234,
          "conversions": 12,
          "roi": 3.8
        }
      }
    ]
  }
}
```

---

### 9.2 获取广告数据统计

```
GET /ads/stats
```

**Query Params:**
```
shop_id=uuid
campaign_id=uuid    // 可选
start_date=2024-01-01
end_date=2024-01-15
granularity=day     // day/week/month
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "summary": {
      "total_spend": 1250.00,
      "total_clicks": 3420,
      "total_conversions": 156,
      "total_revenue": 7800.00,
      "avg_roi": 3.24,
      "avg_cpc": 0.37
    },
    "items": [
      {
        "stat_date": "2024-01-15",
        "spend": 120.00,
        "clicks": 320,
        "conversions": 15,
        "revenue": 750.00,
        "roi": 3.25
      }
    ]
  }
}
```

---

### 9.3 获取广告优化记录

```
GET /ads/optimizations
```

**Query Params:**
```
campaign_id=uuid
status=executed
page=1
page_size=20
```

---

### 9.4 手动触发广告优化

```
POST /ads/campaigns/{campaign_id}/optimize
```

---

## 十、客服模块 `/cs`

### 10.1 获取会话列表

```
GET /cs/sessions
```

**Query Params:**
```
shop_id=uuid
status=escalated    // open/ai_handling/escalated/closed
page=1
page_size=20
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "shop_name": "拼多多3店",
        "status": "escalated",
        "escalation_reason": "买家要求退款，情绪激动",
        "sentiment_score": -0.82,
        "message_count": 8,
        "opened_at": "2024-01-15T14:30:00Z",
        "last_message": "我要投诉你们！"
      }
    ],
    "total": 3
  }
}
```

---

### 10.2 获取会话消息记录

```
GET /cs/sessions/{session_id}/messages
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "sender_type": "buyer",
        "content": "这个裙子质量不好",
        "sent_at": "2024-01-15T14:30:00Z"
      },
      {
        "id": "uuid",
        "sender_type": "ai",
        "content": "非常抱歉给您带来不好的购物体验...",
        "reply_type": "auto",
        "confidence_score": 0.72,
        "was_edited": false,
        "sent_at": "2024-01-15T14:30:05Z"
      }
    ]
  }
}
```

---

### 10.3 人工接管并回复

```
POST /cs/sessions/{session_id}/reply
```

**Request:**
```json
{
  "content": "您好，我是人工客服，请问有什么可以帮到您？",
  "take_over": true    // 是否接管（将status改为escalated由人工处理）
}
```

---

### 10.4 关闭会话

```
POST /cs/sessions/{session_id}/close
```

---

### 10.5 获取评价列表

```
GET /cs/reviews
```

**Query Params:**
```
shop_id=uuid
sentiment=negative
status=needs_attention
page=1
page_size=20
```

---

### 10.6 回复评价

```
POST /cs/reviews/{review_id}/reply
```

**Request:**
```json
{
  "content": "感谢您的反馈，我们会持续改进...",
  "use_ai_suggestion": false
}
```

---

### 10.7 获取AI回复建议

```
GET /cs/reviews/{review_id}/ai-suggestion
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "suggestion": "亲爱的买家，非常感谢您的购买和反馈！对于您提到的质量问题，我们深感抱歉...",
    "tone": "诚恳致歉",
    "confidence": 0.88
  }
}
```

---

### 10.8 知识库管理

```
GET    /cs/knowledge-base/{shop_id}           // 获取知识库
POST   /cs/knowledge-base/{shop_id}/refresh   // 触发RPA重新学习商品知识
GET    /cs/knowledge-base/{shop_id}/faq       // 获取FAQ列表
POST   /cs/knowledge-base/{shop_id}/faq       // 手动添加FAQ
PATCH  /cs/knowledge-base/{shop_id}/faq/{id}  // 更新FAQ
DELETE /cs/knowledge-base/{shop_id}/faq/{id}  // 删除FAQ
```

---

## 十一、供应商模块 `/suppliers`

### 11.1 获取供应商列表

```
GET /suppliers
```

### 11.2 添加供应商

```
POST /suppliers
```

**Request:**
```json
{
  "name": "杭州美莱服饰",
  "platform": "1688",
  "platform_supplier_id": "b2b-123456",
  "contact_name": "李老板",
  "contact_wechat": "laoban_weixin",
  "contact_phone": "13912345678"
}
```

### 11.3 更新供应商

```
PATCH /suppliers/{supplier_id}
```

### 11.4 绑定商品与供应商

```
POST /suppliers/{supplier_id}/products
```

**Request:**
```json
{
  "product_id": "uuid",
  "supply_price": 22.00,
  "min_order_qty": 1,
  "lead_days": 3,
  "is_primary": true
}
```

---

## 十二、套餐与计费模块 `/billing`

### 12.1 获取套餐列表

```
GET /billing/plans
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "code": "starter",
        "name": "新手版",
        "max_shops": 2,
        "monthly_images": 50,
        "monthly_videos": 5,
        "monthly_video_analysis": 20,
        "price_monthly": 99,
        "price_yearly": 999,
        "yearly_discount": "约省2个月"
      }
    ]
  }
}
```

---

### 12.2 创建订阅（发起支付）

```
POST /billing/subscribe
```

**Request:**
```json
{
  "plan_code": "growth",
  "billing_cycle": "yearly",
  "payment_method": "wechat"
}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "order_id": "uuid",
    "amount": 12999.00,
    "payment_method": "wechat",
    "qrcode_url": "weixin://...",     // 微信支付二维码
    "qrcode_base64": "data:image/png;base64,...",
    "expires_in": 300
  }
}
```

---

### 12.3 查询支付状态

```
GET /billing/orders/{order_id}/status
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "status": "success",   // pending/success/failed/expired
    "paid_at": "2024-01-15T10:00:00Z"
  }
}
```

---

### 12.4 按量充值

```
POST /billing/recharge
```

**Request:**
```json
{
  "resource_type": "images",
  "quantity": 200,
  "payment_method": "alipay"
}
```

---

### 12.5 获取用量统计

```
GET /billing/usage
```

**Query Params:**
```
year_month=2024-01    // 格式：YYYY-MM
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "period": "2024-01",
    "quota": {
      "shops": { "used": 8, "max": 15 },
      "images": { "used": 320, "max": 500, "overage": 0 },
      "videos": { "used": 12, "max": 50, "overage": 0 },
      "video_analysis": { "used": 45, "max": 300, "overage": 0 }
    },
    "overage_charges": 0.00
  }
}
```

---

### 12.6 申请开票

```
POST /billing/invoices
```

**Request:**
```json
{
  "subscription_id": "uuid",
  "type": "ordinary",
  "receiver_name": "张三电商有限公司",
  "receiver_email": "finance@example.com",
  "tax_no": "91310000XXXXXXXXX"    // 专票必填
}
```

---

## 十三、仪表盘模块 `/dashboard`

### 13.1 获取总览数据

```
GET /dashboard/overview
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "today": {
      "total_orders": 89,
      "total_revenue": 8920.50,
      "total_ads_spend": 450.00,
      "total_ads_roi": 3.24,
      "pending_approvals": 5,
      "error_shops": 1
    },
    "shops_status": [
      {
        "id": "uuid",
        "name": "拼多多3店",
        "platform": "pdd",
        "status": "active",
        "today_orders": 23,
        "today_revenue": 1580.50,
        "agent_running": true
      }
    ],
    "recent_tasks": [
      {
        "id": "uuid",
        "agent_type": "pricing",
        "summary": "自动跟价：连衣裙 ¥49.9→¥41.9",
        "status": "done",
        "created_at": "2024-01-15T14:00:00Z"
      }
    ],
    "alerts": [
      {
        "type": "cookie_expiring",
        "shop_name": "淘宝1店",
        "message": "登录Cookie将在3天后过期，请及时重新扫码",
        "level": "warning"
      }
    ]
  }
}
```

---

## 十四、WebSocket实时推送 `/ws`

### 14.1 连接

```
WS /ws/{client_id}?token=<jwt_token>
```

连接后服务端主动推送以下类型消息：

---

### 14.2 消息格式

```json
{
  "type": "消息类型",
  "data": { ... },
  "timestamp": "2024-01-15T14:00:00Z"
}
```

---

### 14.3 消息类型定义

**审批通知（手机端核心）**
```json
{
  "type": "approval_required",
  "data": {
    "approval_id": "uuid",
    "priority": 1,
    "title": "定价调整审批",
    "description": "竞品降价20%，建议将「夏季连衣裙」从¥49.9调整至¥41.9",
    "shop_name": "拼多多3店",
    "expires_at": "2024-01-15T16:00:00Z"
  }
}
```

**任务状态更新**
```json
{
  "type": "task_status_changed",
  "data": {
    "task_id": "uuid",
    "agent_type": "pricing",
    "old_status": "executing",
    "new_status": "done",
    "summary": "已完成3个SKU调价"
  }
}
```

**RPA异常告警**
```json
{
  "type": "rpa_alert",
  "data": {
    "shop_id": "uuid",
    "shop_name": "拼多多3店",
    "alert_type": "captcha_detected",
    "message": "检测到验证码，该店铺操作已暂停，请人工处理",
    "level": "error"
  }
}
```

**Cookie过期告警**
```json
{
  "type": "cookie_expired",
  "data": {
    "shop_id": "uuid",
    "shop_name": "淘宝1店",
    "platform": "taobao",
    "message": "登录已过期，请重新扫码绑定"
  }
}
```

**内容生成完成**
```json
{
  "type": "content_generated",
  "data": {
    "task_id": "uuid",
    "content_type": "video",
    "product_id": "uuid",
    "product_title": "夏季新款连衣裙",
    "result_url": "https://cdn.example.com/videos/...",
    "platform": "douyin"
  }
}
```

**客服转人工**
```json
{
  "type": "cs_escalation",
  "data": {
    "session_id": "uuid",
    "shop_name": "拼多多3店",
    "reason": "买家情绪激动，要求退款",
    "sentiment_score": -0.92,
    "last_message": "我要投诉！"
  }
}
```

**用量预警**
```json
{
  "type": "quota_warning",
  "data": {
    "resource_type": "images",
    "used": 480,
    "max": 500,
    "usage_pct": 96,
    "message": "图片生成额度仅剩20张，建议充值"
  }
}
```

---

### 14.4 客户端心跳

```json
// 客户端每30秒发送
{ "type": "ping" }

// 服务端响应
{ "type": "pong", "timestamp": "2024-01-15T14:00:00Z" }
```

---

## 附录：Tauri桌面端调用说明

桌面端通过 `http://127.0.0.1:8765` 调用本地服务端，所有接口相同。

Rust侧调用示例：

```rust
// src-tauri/src/api.rs
use reqwest::Client;
use serde_json::Value;

pub async fn get_dashboard_overview(token: &str) -> Result<Value, String> {
    let client = Client::new();
    let resp = client
        .get("http://127.0.0.1:8765/api/v1/dashboard/overview")
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await
        .map_err(|e| e.to_string())?;

    let data: Value = resp.json().await.map_err(|e| e.to_string())?;
    Ok(data)
}
```

WebSocket连接（桌面端）：

```rust
// 使用 tokio-tungstenite
use tokio_tungstenite::connect_async;

let url = format!("ws://127.0.0.1:8765/ws/desktop-{}?token={}", client_id, token);
let (ws_stream, _) = connect_async(url).await.unwrap();
```

---

*文档版本：v1.0 | 共14个模块，覆盖所有前后端交互接口*

---

# 第四部分：Agent详细设计

**版本：** v1.0  
**框架：** LangGraph 0.2+  
**LLM：** Agnes AI API（OpenAI兼容）  
**覆盖：** 9个Agent完整图结构 + Prompt模板 + 状态定义  

---

## 一、整体架构设计

### 1.1 Agent层次结构

```
OrchestratorAgent（调度中枢）
    │
    ├── SelectionAgent       选品Agent
    ├── PricingAgent         定价Agent
    ├── InventoryAgent       库存Agent
    ├── AdsAgent             广告Agent
    ├── CustomerServiceAgent 客服Agent
    ├── ContentAgent         内容上架Agent
    ├── ImageAgent           AI作图Agent
    └── VideoAgent           AI视频Agent
```

### 1.2 Agent运行模式

```
事件驱动模式：
  平台数据变动 → Orchestrator感知 → 路由到对应Agent → 执行 → 反馈

定时巡检模式：
  Celery Beat定时任务 → 触发Orchestrator → 分发巡检任务

用户指令模式：
  手机端自然语言 → Orchestrator解析意图 → 路由执行 → 结果推送
```

### 1.3 公共状态定义

```python
# agents/state.py
from typing import TypedDict, Annotated, Optional
from langgraph.graph import MessagesState
import operator

class AgentState(TypedDict):
    # 任务基础信息
    task_id:          str
    tenant_id:        str
    shop_id:          Optional[str]
    agent_type:       str
    task_type:        str
    trigger:          str           # scheduled/event/manual/user_command

    # 输入数据
    input_data:       dict

    # Agent推理过程
    messages:         Annotated[list, operator.add]   # LLM对话历史
    decisions:        Annotated[list, operator.add]   # 决策记录
    tool_calls:       Annotated[list, operator.add]   # 工具调用记录

    # 执行动作
    actions:          list          # 待执行动作列表
    requires_approval: bool         # 是否需要人工审批
    approval_id:      Optional[str] # 审批任务ID
    approval_status:  str           # pending/approved/rejected/modified

    # 结果
    result:           dict
    errors:           Annotated[list, operator.add]
    status:           str           # running/pending_approval/done/failed
```

### 1.4 Agent基类

```python
# agents/base_agent.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from openai import AsyncOpenAI
from .state import AgentState

agnes_client = AsyncOpenAI(
    api_key=settings.AGNES_API_KEY,
    base_url="https://apihub.agnes-ai.com/v1"
)

TEXT_MODEL  = "agnes-2.0-flash"
FAST_MODEL  = "agnes-2.0-flash"        # 快速推理，客服/意图解析
THINK_MODEL = "agnes-r1"               # 深度推理，选品分析/策略制定

class BaseAgent:
    def __init__(self):
        self.llm = agnes_client
        self.graph = self._build_graph()
        self.checkpointer = PostgresSaver.from_conn_string(settings.DATABASE_URL)

    def _build_graph(self) -> StateGraph:
        raise NotImplementedError

    async def run(self, initial_state: AgentState) -> AgentState:
        config = {"configurable": {"thread_id": initial_state["task_id"]}}
        result = await self.graph.ainvoke(initial_state, config=config)
        return result

    async def _llm_call(
        self,
        system_prompt: str,
        user_content: str,
        model: str = None,
        json_mode: bool = True
    ) -> str:
        response = await self.llm.chat.completions.create(
            model=model or TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"} if json_mode else None,
            temperature=0.3,
        )
        return response.choices[0].message.content

    async def _check_approval_needed(self, state: AgentState) -> AgentState:
        """判断是否需要人工审批"""
        high_risk = [a for a in state["actions"] if a.get("risk_level") == "high"]
        state["requires_approval"] = len(high_risk) > 0
        return state

    async def _create_approval_task(self, state: AgentState) -> AgentState:
        """创建审批任务，推送到手机端"""
        approval = await db.create_approval_task({
            "agent_task_id": state["task_id"],
            "tenant_id":     state["tenant_id"],
            "shop_id":       state["shop_id"],
            "title":         self._build_approval_title(state),
            "description":   self._build_approval_description(state),
            "options":       self._build_approval_options(state),
            "priority":      self._calculate_priority(state),
            "expires_at":    datetime.now() + timedelta(hours=4),
        })
        state["approval_id"] = approval.id
        state["status"] = "pending_approval"

        # WebSocket推送到手机端
        await ws_manager.push_to_tenant(state["tenant_id"], {
            "type": "approval_required",
            "data": {
                "approval_id": approval.id,
                "title":       approval.title,
                "description": approval.description,
                "shop_name":   await db.get_shop_name(state["shop_id"]),
                "expires_at":  approval.expires_at.isoformat(),
            }
        })
        return state

    def _route_approval(self, state: AgentState) -> str:
        """审批路由"""
        if not state["requires_approval"]:
            return "execute"
        return "create_approval"

    def _route_after_approval(self, state: AgentState) -> str:
        """审批结果路由"""
        status = state["approval_status"]
        if status == "approved":
            return "execute"
        elif status == "modified":
            return "execute"   # 使用修改后的参数执行
        elif status == "rejected":
            return "end"
        else:
            return "wait"      # 继续等待
```

---

## 二、Orchestrator调度中枢

### 2.1 图结构

```
START
  ↓
[感知输入]  parse_trigger
  ↓
[意图理解]  understand_intent
  ↓
[路由决策]  route_to_agent
  ↓
[并发分发]  dispatch_agents（可并发多个Agent）
  ↓
[结果聚合]  aggregate_results
  ↓
END
```

### 2.2 完整实现

```python
# agents/orchestrator.py
from langgraph.graph import StateGraph, END
from langgraph.types import Send

class OrchestratorAgent(BaseAgent):

    # 定时任务配置
    SCHEDULED_TASKS = {
        "price_check":       {"cron": "*/15 * * * *",   "agent": "pricing",   "task": "competitor_scan"},
        "order_process":     {"cron": "*/5 * * * *",    "agent": "inventory", "task": "process_new_orders"},
        "selection_scan":    {"cron": "0 8 * * *",      "agent": "selection", "task": "daily_hot_scan"},
        "ads_optimization":  {"cron": "0 */2 * * *",    "agent": "ads",       "task": "optimize_all"},
        "inventory_check":   {"cron": "0 9,18 * * *",   "agent": "inventory", "task": "stock_alert"},
        "cs_check":          {"cron": "*/3 * * * *",    "agent": "cs",        "task": "fetch_new_messages"},
        "cookie_check":      {"cron": "0 */6 * * *",    "agent": "system",    "task": "health_check"},
    }

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("parse_trigger",      self._parse_trigger)
        graph.add_node("understand_intent",  self._understand_intent)
        graph.add_node("route_to_agent",     self._route_to_agent)
        graph.add_node("dispatch_agents",    self._dispatch_agents)
        graph.add_node("aggregate_results",  self._aggregate_results)

        graph.set_entry_point("parse_trigger")
        graph.add_edge("parse_trigger", "understand_intent")
        graph.add_edge("understand_intent", "route_to_agent")
        graph.add_edge("route_to_agent", "dispatch_agents")
        graph.add_edge("dispatch_agents", "aggregate_results")
        graph.add_edge("aggregate_results", END)

        return graph.compile(checkpointer=self.checkpointer)

    async def _parse_trigger(self, state: AgentState) -> AgentState:
        """解析触发源：定时/事件/用户指令"""
        trigger = state["trigger"]
        input_data = state["input_data"]

        if trigger == "scheduled":
            state["input_data"]["parsed"] = {
                "type": "scheduled",
                "task": input_data.get("task_type"),
                "shops": await db.get_active_shops(state["tenant_id"]),
            }
        elif trigger == "event":
            state["input_data"]["parsed"] = {
                "type": "event",
                "event_type": input_data.get("event_type"),
                "shop_id": input_data.get("shop_id"),
                "payload": input_data.get("payload"),
            }
        elif trigger == "user_command":
            # 自然语言指令需要LLM解析
            state["input_data"]["raw_command"] = input_data.get("command")

        return state

    async def _understand_intent(self, state: AgentState) -> AgentState:
        """理解用户意图（仅user_command触发时需要）"""
        if state["trigger"] != "user_command":
            return state

        raw_command = state["input_data"]["raw_command"]
        shops = await db.get_active_shops(state["tenant_id"])

        result = await self._llm_call(
            system_prompt=ORCHESTRATOR_INTENT_PROMPT,
            user_content=f"""
用户指令：{raw_command}

可用店铺列表：
{json.dumps([{"id": s.id, "name": s.name, "platform": s.platform} for s in shops], ensure_ascii=False)}

当前时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}
""",
            model=FAST_MODEL
        )

        intent = json.loads(result)
        state["input_data"]["parsed_intent"] = intent
        state["decisions"].append({
            "step": "intent_understanding",
            "raw_command": raw_command,
            "parsed_intent": intent,
        })
        return state

    async def _route_to_agent(self, state: AgentState) -> AgentState:
        """决定路由到哪些Agent"""
        trigger = state["trigger"]
        parsed = state["input_data"].get("parsed", {})
        intent = state["input_data"].get("parsed_intent", {})

        routes = []

        if trigger == "scheduled":
            task = parsed.get("task")
            config = next(
                (v for v in self.SCHEDULED_TASKS.values() if v["task"] == task),
                None
            )
            if config:
                for shop in parsed.get("shops", []):
                    routes.append({
                        "agent": config["agent"],
                        "shop_id": shop.id,
                        "task_type": task,
                        "params": {}
                    })

        elif trigger == "event":
            event_type = parsed.get("event_type")
            agent_map = {
                "competitor_price_drop":  "pricing",
                "new_order":              "inventory",
                "low_stock":              "inventory",
                "new_cs_message":         "cs",
                "negative_review":        "cs",
                "ads_performance_drop":   "ads",
            }
            agent = agent_map.get(event_type)
            if agent:
                routes.append({
                    "agent": agent,
                    "shop_id": parsed.get("shop_id"),
                    "task_type": event_type,
                    "params": parsed.get("payload", {})
                })

        elif trigger == "user_command":
            agent = intent.get("target_agent")
            target_shops = intent.get("target_shops", [])
            for shop_id in target_shops:
                routes.append({
                    "agent": agent,
                    "shop_id": shop_id,
                    "task_type": intent.get("action"),
                    "params": intent.get("params", {})
                })

        state["input_data"]["routes"] = routes
        return state

    async def _dispatch_agents(self, state: AgentState) -> AgentState:
        """并发分发到各Agent"""
        routes = state["input_data"].get("routes", [])

        AGENT_MAP = {
            "selection":  SelectionAgent,
            "pricing":    PricingAgent,
            "inventory":  InventoryAgent,
            "ads":        AdsAgent,
            "cs":         CustomerServiceAgent,
            "content":    ContentAgent,
            "image":      ImageAgent,
            "video":      VideoAgent,
        }

        # 并发执行所有子Agent任务
        tasks = []
        for route in routes:
            agent_class = AGENT_MAP.get(route["agent"])
            if agent_class:
                agent_state = AgentState(
                    task_id=str(uuid4()),
                    tenant_id=state["tenant_id"],
                    shop_id=route["shop_id"],
                    agent_type=route["agent"],
                    task_type=route["task_type"],
                    trigger=state["trigger"],
                    input_data=route["params"],
                    messages=[], decisions=[], tool_calls=[],
                    actions=[], requires_approval=False,
                    approval_id=None, approval_status="",
                    result={}, errors=[], status="running"
                )
                agent = agent_class()
                tasks.append(agent.run(agent_state))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        state["input_data"]["agent_results"] = [
            r if not isinstance(r, Exception) else {"error": str(r)}
            for r in results
        ]
        return state

    async def _aggregate_results(self, state: AgentState) -> AgentState:
        """聚合所有Agent执行结果"""
        results = state["input_data"].get("agent_results", [])
        success = sum(1 for r in results if not r.get("error"))
        failed = len(results) - success

        state["result"] = {
            "total_tasks": len(results),
            "success": success,
            "failed": failed,
            "details": results,
        }
        state["status"] = "done"
        return state
```

### 2.3 Orchestrator意图解析Prompt

```python
ORCHESTRATOR_INTENT_PROMPT = """
你是一个电商运营系统的调度助手。用户会用自然语言描述他想要执行的操作。
你需要将用户指令解析为结构化的任务配置。

可用Agent类型：
- selection：选品分析（从1688选品、分析竞品）
- pricing：定价策略（调整价格、跟进竞品）
- inventory：库存管理（补货、发货）
- ads：广告投放（调整出价、优化关键词）
- cs：客服（回复消息、处理评价）
- content：内容上架（上架商品、更新详情）
- image：AI作图（生成商品图片）
- video：AI视频（生成口播视频）

请输出JSON格式（严格JSON，不要有任何多余文字）：
{
  "target_agent": "agent类型",
  "action": "具体操作",
  "target_shops": ["shop_id列表，根据用户描述匹配，如果说所有拼多多店则列出所有pdd的shop_id"],
  "params": {
    "具体操作参数"
  },
  "confirmation_message": "向用户确认的中文描述，说明将要执行什么操作影响哪些店铺"
}

示例：
用户：把所有拼多多店的连衣裙降价5%，不低于30块
输出：
{
  "target_agent": "pricing",
  "action": "batch_price_adjust",
  "target_shops": ["pdd店铺ID1", "pdd店铺ID2", ...],
  "params": {
    "category_keyword": "连衣裙",
    "adjustment_type": "percentage",
    "adjustment_value": -5,
    "price_floor": 30.0
  },
  "confirmation_message": "将对6个拼多多店铺中所有包含「连衣裙」的商品降价5%，价格下限¥30，预计影响23个SKU，是否确认？"
}
"""
```

---

## 三、SelectionAgent — 选品Agent

### 3.1 图结构

```
START
  ↓
[抓取1688数据]  scrape_1688
  ↓
[采集竞品数据]  scrape_competitors
  ↓
[AI综合分析]   analyze_viability
  ↓
[生成选品报告] generate_report
  ↓
[推送审核]     notify_review
  ↓
END
```

### 3.2 实现

```python
# agents/selection_agent.py

class SelectionAgent(BaseAgent):

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("scrape_1688",        self._scrape_1688)
        graph.add_node("scrape_competitors", self._scrape_competitors)
        graph.add_node("analyze_viability",  self._analyze_viability)
        graph.add_node("generate_report",    self._generate_report)
        graph.add_node("notify_review",      self._notify_review)

        graph.set_entry_point("scrape_1688")
        graph.add_edge("scrape_1688",        "scrape_competitors")
        graph.add_edge("scrape_competitors", "analyze_viability")
        graph.add_edge("analyze_viability",  "generate_report")
        graph.add_edge("generate_report",    "notify_review")
        graph.add_edge("notify_review",      END)

        return graph.compile(checkpointer=self.checkpointer)

    async def _scrape_1688(self, state: AgentState) -> AgentState:
        """RPA抓取1688商品数据"""
        keyword = state["input_data"].get("keyword", "")
        source_url = state["input_data"].get("source_url")

        rpa = get_rpa_executor()

        if source_url:
            # 直接抓取指定商品
            products = [await rpa.alibaba_get_product_detail(source_url)]
        else:
            # 关键词搜索
            products = await rpa.alibaba_search_products(keyword, max_pages=3)
            # 获取前10个商品的详情
            for i, p in enumerate(products[:10]):
                detail = await rpa.alibaba_get_product_detail(p["url"])
                products[i].update(detail)

        state["input_data"]["alibaba_products"] = products
        return state

    async def _scrape_competitors(self, state: AgentState) -> AgentState:
        """抓取各平台竞品数据"""
        products = state["input_data"]["alibaba_products"]
        shop = await db.get_shop(state["shop_id"])
        rpa = get_rpa_executor()

        competitor_data = {}
        for product in products[:5]:  # 只深度分析前5个
            keyword = product["title"][:20]
            competitor_data[product["url"]] = {}

            # 根据店铺平台抓取对应竞品
            platforms_to_check = ["pdd", "taobao"]
            if shop.platform == "douyin":
                platforms_to_check.append("douyin")

            for platform in platforms_to_check:
                try:
                    competitors = await rpa.scrape_competitor_prices(
                        platform, keyword, max_results=10
                    )
                    competitor_data[product["url"]][platform] = competitors
                except Exception as e:
                    state["errors"].append(f"竞品抓取失败 {platform}: {e}")

        state["input_data"]["competitor_data"] = competitor_data
        return state

    async def _analyze_viability(self, state: AgentState) -> AgentState:
        """Agnes AI综合分析可行性"""
        products = state["input_data"]["alibaba_products"]
        competitors = state["input_data"]["competitor_data"]
        shop_history = await db.get_shop_hot_products(state["shop_id"], limit=20)

        analyses = []
        for product in products[:10]:
            comp_data = competitors.get(product.get("url", ""), {})

            result = await self._llm_call(
                system_prompt=SELECTION_ANALYSIS_PROMPT,
                user_content=f"""
商品信息：
{json.dumps(product, ensure_ascii=False, indent=2)}

各平台竞品数据：
{json.dumps(comp_data, ensure_ascii=False, indent=2)}

本店历史爆款（参考品类和价格带）：
{json.dumps(shop_history, ensure_ascii=False, indent=2)}

当前日期：{datetime.now().strftime("%Y-%m-%d")}
""",
                model=THINK_MODEL
            )

            analysis = json.loads(result)
            analysis["product"] = product
            analyses.append(analysis)

        # 按综合评分排序
        analyses.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        state["input_data"]["analyses"] = analyses
        return state

    async def _generate_report(self, state: AgentState) -> AgentState:
        """生成并存储选品报告"""
        analyses = state["input_data"]["analyses"]
        reports = []

        for analysis in analyses:
            report = await db.create_selection_report({
                "tenant_id":       state["tenant_id"],
                "source_url":      analysis["product"].get("url"),
                "keyword":         state["input_data"].get("keyword"),
                "product_data":    analysis["product"],
                "overall_score":   analysis["overall_score"],
                "platform_scores": analysis["platform_scores"],
                "profit_estimate": analysis["profit_estimate"],
                "risks":           analysis["risks"],
                "recommendation":  analysis["recommendation"],
                "status":          "pending",
            })
            reports.append(report)

        state["result"]["reports"] = [r.id for r in reports]
        state["result"]["top_recommendation"] = analyses[0] if analyses else None
        return state

    async def _notify_review(self, state: AgentState) -> AgentState:
        """推送选品报告到手机端审核"""
        top = state["result"].get("top_recommendation")
        if top and top.get("overall_score", 0) >= 70:
            await ws_manager.push_to_tenant(state["tenant_id"], {
                "type": "selection_report_ready",
                "data": {
                    "report_count": len(state["result"]["reports"]),
                    "top_score": top["overall_score"],
                    "top_recommendation": top["recommendation"],
                    "top_product_title": top["product"]["title"],
                }
            })
        state["status"] = "done"
        return state
```

### 3.3 选品分析Prompt

```python
SELECTION_ANALYSIS_PROMPT = """
你是一个资深电商选品顾问，专注于国内多平台电商运营。

分析维度：
1. 利润空间：1688成本 vs 各平台市场均价，扣除平台佣金后的净利润率
2. 竞争烈度：竞品数量、头部商家销量集中度、新卖家突围难度
3. 需求趋势：当前是否处于季节性旺季、热度是否持续
4. 供应链质量：供应商评分、发货速度、起订量门槛
5. 平台适配度：该品类在各平台的运营逻辑差异

评分标准（0-100分）：
- 90-100：强烈推荐，利润高、竞争适中、趋势好
- 70-89：推荐，综合条件良好
- 50-69：观望，有机会但有明显风险
- 0-49：不推荐，利润薄或竞争过激

请严格输出JSON格式：
{
  "overall_score": 整数0-100,
  "recommendation": "strong_buy/buy/hold/pass",
  "platform_scores": {
    "pdd": {
      "score": 整数0-100,
      "suggested_price": 建议售价(数字),
      "estimated_monthly_sales": 预估月销量,
      "reason": "该平台适合/不适合的理由"
    },
    "taobao": {...},
    "douyin": {...},
    "xiaohongshu": {...}
  },
  "profit_estimate": {
    "cost": 1688采购价(数字),
    "pdd_price": 拼多多建议售价,
    "pdd_margin": "利润率百分比字符串如15%",
    "taobao_price": 淘宝建议售价,
    "taobao_margin": "利润率百分比"
  },
  "supply_chain": {
    "score": 整数0-100,
    "min_order": 最小起订量,
    "lead_days": 备货周期天数,
    "risk": "供应链风险描述"
  },
  "risks": ["风险点1", "风险点2", "风险点3"],
  "opportunities": ["机会点1", "机会点2"],
  "summary": "100字以内的综合评价"
}
"""
```

---

## 四、PricingAgent — 定价Agent

### 4.1 图结构

```
START
  ↓
[抓取竞品价格] fetch_competitor_prices
  ↓
[分析定价策略] analyze_pricing_strategy
  ↓
[生成调价方案] generate_price_actions
  ↓
[风险评估]     assess_risk
  ↓
[审批路由] ──→ [创建审批] → [等待审批] → [执行]
               ↓ (无需审批)
             [直接执行] → [RPA改价] → [验证结果]
  ↓
END
```

### 4.2 实现

```python
# agents/pricing_agent.py

class PricingAgent(BaseAgent):

    # 定价规则配置
    PRICING_RULES = {
        "auto_follow_threshold":   0.05,   # 竞品降价超过5%自动跟进
        "approval_threshold":      0.15,   # 价格变动超过15%需要审批
        "min_margin":              0.12,   # 最低利润率12%
        "max_daily_price_changes": 3,      # 每件商品每天最多改价3次
        "slow_moving_days":        7,      # 超过7天无销量视为滞销
        "slow_moving_drop_pct":    0.05,   # 滞销商品每次降5%
        "slow_moving_max_drop":    0.20,   # 滞销最多降20%
    }

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("fetch_competitor_prices",    self._fetch_competitor_prices)
        graph.add_node("analyze_pricing_strategy",   self._analyze_pricing_strategy)
        graph.add_node("generate_price_actions",     self._generate_price_actions)
        graph.add_node("assess_risk",                self._assess_risk)
        graph.add_node("check_approval",             self._check_approval_needed)
        graph.add_node("create_approval",            self._create_approval_task)
        graph.add_node("wait_approval",              self._wait_for_approval)
        graph.add_node("execute_price_changes",      self._execute_price_changes)
        graph.add_node("verify_results",             self._verify_results)

        graph.set_entry_point("fetch_competitor_prices")
        graph.add_edge("fetch_competitor_prices",  "analyze_pricing_strategy")
        graph.add_edge("analyze_pricing_strategy", "generate_price_actions")
        graph.add_edge("generate_price_actions",   "assess_risk")
        graph.add_edge("assess_risk",              "check_approval")

        # 条件路由：是否需要审批
        graph.add_conditional_edges(
            "check_approval",
            self._route_approval,
            {
                "execute":         "execute_price_changes",
                "create_approval": "create_approval",
            }
        )
        graph.add_edge("create_approval", "wait_approval")

        # 审批结果路由
        graph.add_conditional_edges(
            "wait_approval",
            self._route_after_approval,
            {
                "execute": "execute_price_changes",
                "end":     END,
                "wait":    "wait_approval",
            }
        )

        graph.add_edge("execute_price_changes", "verify_results")
        graph.add_edge("verify_results", END)

        return graph.compile(checkpointer=self.checkpointer)

    async def _fetch_competitor_prices(self, state: AgentState) -> AgentState:
        """RPA抓取竞品最新价格"""
        shop = await db.get_shop(state["shop_id"])
        products = await db.get_shop_products(state["shop_id"], status="on_sale")

        rpa = get_rpa_executor()
        competitor_data = []

        for product in products:
            try:
                competitors = await rpa.scrape_competitor_prices(
                    shop.platform, product.title[:20]
                )
                # 存入数据库
                for comp in competitors:
                    await db.save_competitor_price({
                        "product_id": product.id,
                        "platform": shop.platform,
                        **comp,
                        "recorded_at": datetime.now()
                    })

                competitor_data.append({
                    "product": product,
                    "competitors": competitors,
                })
            except Exception as e:
                state["errors"].append(f"竞品价格抓取失败 {product.id}: {e}")

        state["input_data"]["competitor_data"] = competitor_data
        return state

    async def _analyze_pricing_strategy(self, state: AgentState) -> AgentState:
        """Agnes AI分析每个商品的定价策略"""
        competitor_data = state["input_data"]["competitor_data"]
        shop_config = await db.get_shop_config(state["shop_id"])
        analyses = []

        for item in competitor_data:
            product = item["product"]
            competitors = item["competitors"]

            # 计算竞品价格统计
            prices = [c["price"] for c in competitors if c.get("price")]
            if not prices:
                continue

            comp_stats = {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "median_price": sorted(prices)[len(prices)//2],
            }

            result = await self._llm_call(
                system_prompt=PRICING_STRATEGY_PROMPT,
                user_content=f"""
商品信息：
- 标题：{product.title}
- 当前售价：¥{product.current_price}
- 采购成本：¥{product.cost}
- 当前利润率：{((product.current_price - product.cost) / product.current_price * 100):.1f}%
- 近7天销量：{product.recent_sales or 0}件

竞品价格统计：
- 最低价：¥{comp_stats['min_price']}
- 最高价：¥{comp_stats['max_price']}
- 均价：¥{comp_stats['avg_price']:.2f}
- 竞品数量：{len(competitors)}家

定价规则约束：
- 最低利润率：{self.PRICING_RULES['min_margin']*100}%
- 价格底线：¥{product.cost * (1 + self.PRICING_RULES['min_margin']):.2f}
- 店铺配置价格底线：¥{shop_config.get('price_floor', 0)}
""",
                model=FAST_MODEL
            )

            analysis = json.loads(result)
            analysis["product_id"] = str(product.id)
            analysis["current_price"] = float(product.current_price)
            analysis["cost"] = float(product.cost)
            analyses.append(analysis)

        state["input_data"]["price_analyses"] = analyses
        return state

    async def _generate_price_actions(self, state: AgentState) -> AgentState:
        """生成具体调价动作"""
        analyses = state["input_data"]["price_analyses"]
        actions = []

        for analysis in analyses:
            if analysis.get("action") == "no_change":
                continue

            change_pct = abs(
                analysis["suggested_price"] - analysis["current_price"]
            ) / analysis["current_price"]

            action = {
                "type":            "update_price",
                "product_id":      analysis["product_id"],
                "current_price":   analysis["current_price"],
                "new_price":       analysis["suggested_price"],
                "change_pct":      change_pct * 100,
                "change_direction": "down" if analysis["suggested_price"] < analysis["current_price"] else "up",
                "reason":          analysis["reason"],
                "risk_level":      "high" if change_pct > self.PRICING_RULES["approval_threshold"] else "low",
            }
            actions.append(action)

        state["actions"] = actions
        return state

    async def _assess_risk(self, state: AgentState) -> AgentState:
        """评估整体风险"""
        actions = state["actions"]
        high_risk = [a for a in actions if a["risk_level"] == "high"]
        total_change_value = sum(
            abs(a["new_price"] - a["current_price"]) for a in actions
        )

        state["decisions"].append({
            "step": "risk_assessment",
            "total_actions": len(actions),
            "high_risk_actions": len(high_risk),
            "total_price_impact": total_change_value,
            "requires_approval": len(high_risk) > 0,
        })
        return state

    async def _execute_price_changes(self, state: AgentState) -> AgentState:
        """RPA执行改价"""
        shop = await db.get_shop(state["shop_id"])
        rpa = get_rpa_executor()

        # 如果审批时修改了价格，使用修改后的值
        if state["approval_status"] == "modified":
            modifications = await db.get_approval_modifications(state["approval_id"])
            for action in state["actions"]:
                if action["product_id"] in modifications:
                    action["new_price"] = modifications[action["product_id"]]["new_price"]

        results = []
        for action in state["actions"]:
            try:
                await rate_limiter.acquire(state["shop_id"], shop.platform, "price_update")

                result = await rpa.update_product_price(
                    shop_id=state["shop_id"],
                    platform=shop.platform,
                    product_id=action["product_id"],
                    new_price=action["new_price"],
                )

                # 更新数据库价格
                if result["success"]:
                    await db.update_product_price(
                        action["product_id"], action["new_price"]
                    )

                results.append({**action, "rpa_result": result})
                await asyncio.sleep(random.uniform(2, 5))

            except Exception as e:
                results.append({**action, "rpa_result": {"success": False, "error": str(e)}})

        state["result"]["price_changes"] = results
        state["result"]["success_count"] = sum(1 for r in results if r["rpa_result"]["success"])
        return state

    async def _verify_results(self, state: AgentState) -> AgentState:
        """验证改价结果，等待1分钟后二次确认"""
        await asyncio.sleep(60)

        shop = await db.get_shop(state["shop_id"])
        rpa = get_rpa_executor()
        verified = []

        for change in state["result"]["price_changes"]:
            if not change["rpa_result"]["success"]:
                continue
            actual_price = await rpa.get_product_current_price(
                state["shop_id"], shop.platform, change["product_id"]
            )
            verified.append({
                "product_id": change["product_id"],
                "expected_price": change["new_price"],
                "actual_price": actual_price,
                "verified": abs(actual_price - change["new_price"]) < 0.01,
            })

        state["result"]["verification"] = verified
        state["status"] = "done"
        return state
```

### 4.3 定价策略Prompt

```python
PRICING_STRATEGY_PROMPT = """
你是一个专业的电商定价策略顾问。基于商品和竞品数据，给出最优定价建议。

定价决策逻辑：
1. 若竞品均价比当前价低10%以上 → 考虑降价跟进（但不低于成本×1.12）
2. 若当前价低于竞品均价20%以上 → 考虑适当涨价以提升利润
3. 若近7天零销量 → 视为滞销，建议降价5%刺激销售
4. 若竞品数量少于5家 → 蓝海品类，可保持或微涨价
5. 价格变动尽量控制在±15%以内，避免触发平台监控

请严格输出JSON格式：
{
  "action": "decrease/increase/no_change",
  "suggested_price": 建议价格(数字，保留2位小数),
  "change_percentage": 变动幅度百分比(数字，正数涨价负数降价),
  "reason": "调价理由，50字以内",
  "confidence": 0到1之间的置信度,
  "alternative_price": 备选价格(数字),
  "strategy": "follow_competitor/protect_margin/clear_inventory/blue_ocean"
}
"""
```

---

## 五、InventoryAgent — 库存Agent

### 5.1 图结构

```
START
  ↓
[抓取订单数据]   fetch_orders
  ↓
[处理待发货订单] process_pending_orders
  ├── 1688代发 → [1688自动下单]
  ├── 微信通知 → [虚拟机微信发消息]
  └── 自有库存 → [生成发货单]
  ↓
[库存预警检查]   check_stock_alerts
  ↓
[生成补货建议]   generate_restock_suggestions
  ↓
END
```

### 5.2 实现

```python
# agents/inventory_agent.py

class InventoryAgent(BaseAgent):

    STOCK_ALERT_THRESHOLD = 10  # 库存低于10件触发预警

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("fetch_orders",                self._fetch_orders)
        graph.add_node("process_pending_orders",      self._process_pending_orders)
        graph.add_node("handle_1688_dropship",        self._handle_1688_dropship)
        graph.add_node("handle_wechat_notify",        self._handle_wechat_notify)
        graph.add_node("handle_self_warehouse",       self._handle_self_warehouse)
        graph.add_node("check_stock_alerts",          self._check_stock_alerts)
        graph.add_node("generate_restock_suggestions",self._generate_restock_suggestions)
        graph.add_node("notify_alerts",               self._notify_alerts)

        graph.set_entry_point("fetch_orders")
        graph.add_edge("fetch_orders", "process_pending_orders")

        graph.add_conditional_edges(
            "process_pending_orders",
            self._route_fulfillment,
            {
                "1688_dropship":    "handle_1688_dropship",
                "wechat_notify":    "handle_wechat_notify",
                "self_warehouse":   "handle_self_warehouse",
                "done":             "check_stock_alerts",
            }
        )

        for node in ["handle_1688_dropship", "handle_wechat_notify", "handle_self_warehouse"]:
            graph.add_edge(node, "check_stock_alerts")

        graph.add_edge("check_stock_alerts",           "generate_restock_suggestions")
        graph.add_edge("generate_restock_suggestions", "notify_alerts")
        graph.add_edge("notify_alerts",                END)

        return graph.compile(checkpointer=self.checkpointer)

    async def _fetch_orders(self, state: AgentState) -> AgentState:
        """RPA抓取新订单"""
        shop = await db.get_shop(state["shop_id"])
        rpa = get_rpa_executor()

        new_orders = await rpa.fetch_orders(
            shop_id=state["shop_id"],
            platform=shop.platform,
            status="wait_ship"
        )

        # 过滤已处理的订单
        existing_ids = await db.get_existing_order_ids(state["shop_id"])
        new_orders = [o for o in new_orders if o["platform_order_id"] not in existing_ids]

        # 保存新订单
        saved_orders = []
        for order_data in new_orders:
            order = await db.create_order({
                "tenant_id": state["tenant_id"],
                "shop_id": state["shop_id"],
                "status": "paid",
                **order_data
            })
            saved_orders.append(order)

        state["input_data"]["new_orders"] = saved_orders
        return state

    async def _process_pending_orders(self, state: AgentState) -> AgentState:
        """为每个订单确定发货方式"""
        orders = state["input_data"]["new_orders"]
        categorized = {"1688_dropship": [], "wechat_notify": [], "self_warehouse": []}

        for order in orders:
            product = await db.get_product(order.product_id)
            supplier = await db.get_primary_supplier(product.id)

            if supplier and supplier.platform == "1688":
                categorized["1688_dropship"].append(order)
            elif supplier and supplier.contact_wechat:
                categorized["wechat_notify"].append(order)
            else:
                categorized["self_warehouse"].append(order)

        state["input_data"]["categorized_orders"] = categorized
        return state

    def _route_fulfillment(self, state: AgentState) -> str:
        categorized = state["input_data"]["categorized_orders"]
        if categorized["1688_dropship"]:
            return "1688_dropship"
        if categorized["wechat_notify"]:
            return "wechat_notify"
        if categorized["self_warehouse"]:
            return "self_warehouse"
        return "done"

    async def _handle_1688_dropship(self, state: AgentState) -> AgentState:
        """1688自动代发"""
        orders = state["input_data"]["categorized_orders"]["1688_dropship"]
        rpa = get_rpa_executor()
        results = []

        for order in orders:
            try:
                product = await db.get_product(order.product_id)
                supplier = await db.get_primary_supplier(product.id)
                buyer_info = decrypt_aes(order.buyer_encrypted)

                result = await rpa.alibaba_place_dropship_order(
                    product_url=supplier.platform_supplier_id,
                    order_info={
                        "sku_specs": json.loads(order.sku.attributes),
                        "quantity": order.quantity,
                        **json.loads(buyer_info)
                    }
                )

                if result["success"]:
                    await db.create_shipment_record({
                        "order_id": order.id,
                        "supplier_id": supplier.id,
                        "channel": "1688_auto",
                        "status": "confirmed",
                        "notified_at": datetime.now(),
                    })
                    await db.update_order_status(order.id, "shipped")

                results.append({"order_id": str(order.id), **result})

            except Exception as e:
                results.append({"order_id": str(order.id), "success": False, "error": str(e)})

        state["result"]["1688_dropship_results"] = results
        return state

    async def _handle_wechat_notify(self, state: AgentState) -> AgentState:
        """虚拟机微信通知供应商"""
        orders = state["input_data"]["categorized_orders"]["wechat_notify"]
        wechat_vm = WeChatVMController(settings.VM_CONFIG)
        results = []

        for order in orders:
            try:
                supplier = await db.get_primary_supplier(order.product_id)
                buyer_info = json.loads(decrypt_aes(order.buyer_encrypted))

                message = wechat_vm.format_order_message({
                    "order_id": order.platform_order_id,
                    "product_name": order.product.title,
                    "quantity": order.quantity,
                    "spec": str(order.sku.attributes),
                    **buyer_info
                })

                result = await wechat_vm.send_supplier_message(
                    supplier_name=supplier.contact_wechat,
                    order_info={"message": message}
                )

                await db.create_shipment_record({
                    "order_id": order.id,
                    "supplier_id": supplier.id,
                    "channel": "wechat_notify",
                    "status": "notified",
                    "message_content": message,
                    "notified_at": datetime.now(),
                })

                results.append({"order_id": str(order.id), "success": True})

            except Exception as e:
                results.append({"order_id": str(order.id), "success": False, "error": str(e)})

        state["result"]["wechat_notify_results"] = results
        return state

    async def _check_stock_alerts(self, state: AgentState) -> AgentState:
        """检查库存预警"""
        skus = await db.get_low_stock_skus(
            shop_id=state["shop_id"],
            threshold=self.STOCK_ALERT_THRESHOLD
        )
        state["input_data"]["low_stock_skus"] = skus
        return state

    async def _generate_restock_suggestions(self, state: AgentState) -> AgentState:
        """AI生成补货建议"""
        low_stock_skus = state["input_data"]["low_stock_skus"]
        if not low_stock_skus:
            return state

        result = await self._llm_call(
            system_prompt=INVENTORY_RESTOCK_PROMPT,
            user_content=json.dumps([{
                "sku_id": str(s.id),
                "product_title": s.product.title,
                "attributes": s.attributes,
                "current_stock": s.stock,
                "recent_daily_sales": await db.get_sku_daily_sales(s.id, days=7),
                "supplier_lead_days": await db.get_supplier_lead_days(s.product_id),
            } for s in low_stock_skus], ensure_ascii=False)
        )

        suggestions = json.loads(result)
        state["input_data"]["restock_suggestions"] = suggestions
        return state

    async def _notify_alerts(self, state: AgentState) -> AgentState:
        """推送库存告警"""
        low_stock = state["input_data"].get("low_stock_skus", [])
        suggestions = state["input_data"].get("restock_suggestions", [])

        if low_stock:
            await ws_manager.push_to_tenant(state["tenant_id"], {
                "type": "inventory_alert",
                "data": {
                    "low_stock_count": len(low_stock),
                    "suggestions": suggestions,
                    "shop_name": await db.get_shop_name(state["shop_id"]),
                }
            })
        state["status"] = "done"
        return state
```

---

## 六、CustomerServiceAgent — 客服Agent

### 6.1 图结构

```
START
  ↓
[抓取新消息]   fetch_new_messages
  ↓
[情绪分析]     analyze_sentiment
  ↓
[分类路由] ──→ 负面/投诉 → [转人工告警]
               ↓ (正常)
             [生成AI回复] → [发送回复] → [更新会话状态]
  ↓
[处理新评价]   handle_reviews
  ↓
END
```

### 6.2 实现

```python
# agents/cs_agent.py

class CustomerServiceAgent(BaseAgent):

    # 触发转人工的关键词
    ESCALATION_KEYWORDS = [
        "投诉", "举报", "假货", "欺骗", "骗子", "曝光",
        "退款", "退货", "差评", "维权", "律师", "起诉"
    ]

    # 情绪转人工阈值
    SENTIMENT_THRESHOLD = -0.6

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("fetch_new_messages",    self._fetch_new_messages)
        graph.add_node("analyze_sentiment",     self._analyze_sentiment)
        graph.add_node("generate_ai_reply",     self._generate_ai_reply)
        graph.add_node("send_reply",            self._send_reply)
        graph.add_node("escalate_to_human",     self._escalate_to_human)
        graph.add_node("update_session_status", self._update_session_status)
        graph.add_node("handle_reviews",        self._handle_reviews)

        graph.set_entry_point("fetch_new_messages")
        graph.add_edge("fetch_new_messages", "analyze_sentiment")

        graph.add_conditional_edges(
            "analyze_sentiment",
            self._route_by_sentiment,
            {
                "escalate":  "escalate_to_human",
                "ai_handle": "generate_ai_reply",
            }
        )

        graph.add_edge("generate_ai_reply",    "send_reply")
        graph.add_edge("send_reply",           "update_session_status")
        graph.add_edge("escalate_to_human",    "update_session_status")
        graph.add_edge("update_session_status","handle_reviews")
        graph.add_edge("handle_reviews",       END)

        return graph.compile(checkpointer=self.checkpointer)

    async def _fetch_new_messages(self, state: AgentState) -> AgentState:
        """RPA抓取新消息"""
        shop = await db.get_shop(state["shop_id"])
        rpa = get_rpa_executor()

        raw_sessions = await rpa.fetch_new_cs_messages(
            shop_id=state["shop_id"],
            platform=shop.platform
        )

        sessions = []
        for raw in raw_sessions:
            session = await db.get_or_create_cs_session({
                "shop_id": state["shop_id"],
                "platform_session_id": raw["session_id"],
                "buyer_id": raw["buyer_id"],
            })
            await db.save_cs_message({
                "session_id": session.id,
                "sender_type": "buyer",
                "content": raw["last_message"],
                "sent_at": datetime.now(),
            })
            sessions.append({
                "session": session,
                "message": raw["last_message"],
                "history": await db.get_session_history(session.id, limit=10),
            })

        state["input_data"]["sessions"] = sessions
        return state

    async def _analyze_sentiment(self, state: AgentState) -> AgentState:
        """批量情绪分析"""
        sessions = state["input_data"]["sessions"]
        analyzed = []

        for item in sessions:
            message = item["message"]

            # 快速关键词检测（不用LLM，节省token）
            has_escalation_keyword = any(
                kw in message for kw in self.ESCALATION_KEYWORDS
            )

            if has_escalation_keyword:
                item["sentiment"] = -1.0
                item["needs_escalation"] = True
                item["escalation_reason"] = "包含投诉/退款关键词"
            else:
                # LLM情绪打分
                result = await self._llm_call(
                    system_prompt=SENTIMENT_ANALYSIS_PROMPT,
                    user_content=message,
                    model=FAST_MODEL
                )
                sentiment_data = json.loads(result)
                item["sentiment"] = sentiment_data["score"]
                item["needs_escalation"] = sentiment_data["score"] < self.SENTIMENT_THRESHOLD
                item["escalation_reason"] = sentiment_data.get("reason", "")

            analyzed.append(item)

        state["input_data"]["analyzed_sessions"] = analyzed
        return state

    def _route_by_sentiment(self, state: AgentState) -> str:
        sessions = state["input_data"]["analyzed_sessions"]
        if any(s["needs_escalation"] for s in sessions):
            return "escalate"
        return "ai_handle"

    async def _generate_ai_reply(self, state: AgentState) -> AgentState:
        """Agnes AI生成客服回复"""
        sessions = state["input_data"]["analyzed_sessions"]
        kb = await db.get_shop_knowledge_base(state["shop_id"])

        for item in sessions:
            if item["needs_escalation"]:
                continue

            result = await self._llm_call(
                system_prompt=CS_REPLY_PROMPT.format(
                    shop_name=item["session"].shop.platform_shop_name,
                    knowledge_base=json.dumps(kb, ensure_ascii=False),
                    platform_rules=kb.get("platform_rules", ""),
                ),
                user_content=f"""
对话历史：
{self._format_history(item['history'])}

买家最新消息：{item['message']}

请生成回复。
""",
                model=FAST_MODEL
            )

            reply_data = json.loads(result)
            item["ai_reply"] = reply_data["reply"]
            item["reply_confidence"] = reply_data["confidence"]
            item["reply_type"] = reply_data["type"]  # direct_answer/empathy/clarification

        state["input_data"]["analyzed_sessions"] = sessions
        return state

    async def _send_reply(self, state: AgentState) -> AgentState:
        """RPA发送回复"""
        shop = await db.get_shop(state["shop_id"])
        rpa = get_rpa_executor()
        sessions = state["input_data"]["analyzed_sessions"]

        for item in sessions:
            if item["needs_escalation"] or not item.get("ai_reply"):
                continue

            try:
                success = await rpa.reply_cs_message(
                    shop_id=state["shop_id"],
                    platform=shop.platform,
                    session_id=item["session"].platform_session_id,
                    reply_text=item["ai_reply"]
                )

                if success:
                    await db.save_cs_message({
                        "session_id": item["session"].id,
                        "sender_type": "ai",
                        "content": item["ai_reply"],
                        "reply_type": "auto",
                        "confidence_score": item["reply_confidence"],
                        "sent_at": datetime.now(),
                    })
                    await db.update_session_sentiment(
                        item["session"].id, item["sentiment"]
                    )

            except Exception as e:
                state["errors"].append(f"回复发送失败: {e}")

        return state

    async def _escalate_to_human(self, state: AgentState) -> AgentState:
        """转人工处理"""
        sessions = state["input_data"]["analyzed_sessions"]

        for item in sessions:
            if not item["needs_escalation"]:
                continue

            await db.update_cs_session(item["session"].id, {
                "status": "escalated",
                "escalation_reason": item["escalation_reason"],
                "sentiment_score": item["sentiment"],
            })

            # 推送告警到手机端
            await ws_manager.push_to_tenant(state["tenant_id"], {
                "type": "cs_escalation",
                "data": {
                    "session_id": str(item["session"].id),
                    "shop_name": item["session"].shop.name,
                    "reason": item["escalation_reason"],
                    "sentiment_score": item["sentiment"],
                    "last_message": item["message"],
                }
            })

        return state

    async def _handle_reviews(self, state: AgentState) -> AgentState:
        """处理新评价：抓取+分析+自动回复"""
        shop = await db.get_shop(state["shop_id"])
        rpa = get_rpa_executor()

        reviews = await rpa.fetch_new_reviews(
            shop_id=state["shop_id"],
            platform=shop.platform
        )

        for review in reviews:
            # 低于4星的评价需要特殊处理
            if review["rating"] <= 3:
                # AI生成回复建议
                reply_suggestion = await self._generate_review_reply(review)
                await db.save_review({
                    "shop_id": state["shop_id"],
                    "status": "needs_attention",
                    **review,
                    "reply_content": reply_suggestion,
                })
                # 推送告警
                await ws_manager.push_to_tenant(state["tenant_id"], {
                    "type": "negative_review",
                    "data": {
                        "rating": review["rating"],
                        "content": review["content"],
                        "shop_name": shop.name,
                        "ai_reply_suggestion": reply_suggestion,
                    }
                })
            else:
                # 好评自动回复
                auto_reply = await self._generate_review_reply(review)
                await rpa.reply_review(
                    shop_id=state["shop_id"],
                    platform=shop.platform,
                    review_id=review["platform_review_id"],
                    reply=auto_reply
                )

        state["status"] = "done"
        return state
```

### 6.3 客服Prompt模板

```python
CS_REPLY_PROMPT = """
你是「{shop_name}」的专业客服助手。你的职责是用友好、专业的语气回复买家咨询。

商品和店铺知识库：
{knowledge_base}

平台规则：
{platform_rules}

回复原则：
1. 简洁明了，不超过100字
2. 友好亲切，称呼买家为「亲」
3. 涉及价格/退换货，严格按平台规则回答
4. 不确定的问题不要乱答，说「稍等，帮您查询一下」
5. 不要主动提及竞品

请严格输出JSON格式：
{{
  "reply": "回复内容",
  "confidence": 0到1之间的置信度,
  "type": "direct_answer/empathy/clarification/redirect_human",
  "key_issue": "买家主要问题类型"
}}
"""

SENTIMENT_ANALYSIS_PROMPT = """
分析用户消息的情绪倾向。

输出JSON：
{
  "score": -1到1之间的数字（-1极度负面，0中性，1极度正面），
  "label": "positive/neutral/negative/very_negative",
  "reason": "情绪判断依据，20字以内",
  "urgency": "low/medium/high"
}
"""

INVENTORY_RESTOCK_PROMPT = """
你是库存管理助手。基于当前库存和销售数据，给出补货建议。

补货计算逻辑：
- 安全库存 = 日均销量 × 供货周期 × 1.5（安全系数）
- 建议补货量 = 安全库存 - 当前库存（如果大于0）
- 优先级：库存为0 > 库存少于3天销量 > 库存少于7天销量

请输出JSON数组：
[
  {
    "sku_id": "xxx",
    "product_title": "商品名",
    "current_stock": 当前库存,
    "daily_sales": 日均销量,
    "suggested_restock": 建议补货数量,
    "urgency": "urgent/normal/low",
    "reason": "补货理由"
  }
]
"""
```

---

## 七、AdsAgent — 广告Agent

### 7.1 实现（核心节点）

```python
# agents/ads_agent.py

class AdsAgent(BaseAgent):

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("fetch_ads_data",          self._fetch_ads_data)
        graph.add_node("analyze_performance",     self._analyze_performance)
        graph.add_node("generate_optimizations",  self._generate_optimizations)
        graph.add_node("check_approval",          self._check_approval_needed)
        graph.add_node("create_approval",         self._create_approval_task)
        graph.add_node("wait_approval",           self._wait_for_approval)
        graph.add_node("execute_optimizations",   self._execute_optimizations)

        graph.set_entry_point("fetch_ads_data")
        graph.add_edge("fetch_ads_data",         "analyze_performance")
        graph.add_edge("analyze_performance",    "generate_optimizations")
        graph.add_edge("generate_optimizations", "check_approval")

        graph.add_conditional_edges(
            "check_approval",
            self._route_approval,
            {"execute": "execute_optimizations", "create_approval": "create_approval"}
        )
        graph.add_edge("create_approval", "wait_approval")
        graph.add_conditional_edges(
            "wait_approval",
            self._route_after_approval,
            {"execute": "execute_optimizations", "end": END, "wait": "wait_approval"}
        )
        graph.add_edge("execute_optimizations", END)

        return graph.compile(checkpointer=self.checkpointer)

    async def _fetch_ads_data(self, state: AgentState) -> AgentState:
        shop = await db.get_shop(state["shop_id"])
        rpa = get_rpa_executor()
        ads_data = await rpa.fetch_ads_report(
            shop_id=state["shop_id"],
            platform=shop.platform,
            days=7
        )
        state["input_data"]["ads_data"] = ads_data
        return state

    async def _analyze_performance(self, state: AgentState) -> AgentState:
        ads_data = state["input_data"]["ads_data"]
        shop_config = await db.get_shop_config(state["shop_id"])

        result = await self._llm_call(
            system_prompt=ADS_ANALYSIS_PROMPT,
            user_content=f"""
广告数据（近7天）：
{json.dumps(ads_data, ensure_ascii=False, indent=2)}

目标ROI：{shop_config.get('target_roi', 2.5)}
日预算上限：¥{shop_config.get('max_ads_daily_budget', 500)}
""",
            model=THINK_MODEL
        )

        analysis = json.loads(result)
        state["input_data"]["ads_analysis"] = analysis
        return state

    async def _generate_optimizations(self, state: AgentState) -> AgentState:
        analysis = state["input_data"]["ads_analysis"]
        actions = []

        for opt in analysis.get("optimizations", []):
            change_pct = abs(opt.get("budget_change_pct", 0))
            actions.append({
                "type":           opt["action_type"],
                "campaign_id":    opt["campaign_id"],
                "ad_group_id":    opt.get("ad_group_id"),
                "keyword":        opt.get("keyword"),
                "before_value":   opt["before_value"],
                "after_value":    opt["after_value"],
                "reason":         opt["reason"],
                "risk_level":     "high" if change_pct > 20 else "low",
                "budget_change_pct": change_pct,
            })

        state["actions"] = actions
        return state

    async def _execute_optimizations(self, state: AgentState) -> AgentState:
        shop = await db.get_shop(state["shop_id"])
        rpa = get_rpa_executor()

        for action in state["actions"]:
            try:
                await rpa.execute_ads_action(
                    shop_id=state["shop_id"],
                    platform=shop.platform,
                    action=action
                )
                await db.save_ads_optimization_record({
                    "tenant_id": state["tenant_id"],
                    "agent_task_id": state["task_id"],
                    "campaign_id": action["campaign_id"],
                    "action_type": action["type"],
                    "before_state": {"value": action["before_value"]},
                    "after_state": {"value": action["after_value"]},
                    "reason": action["reason"],
                    "status": "executed",
                    "executed_at": datetime.now(),
                })
                await asyncio.sleep(random.uniform(2, 5))
            except Exception as e:
                state["errors"].append(str(e))

        state["status"] = "done"
        return state
```

### 7.2 广告分析Prompt

```python
ADS_ANALYSIS_PROMPT = """
你是电商广告优化专家。基于广告数据，给出优化建议。

优化逻辑：
1. ROI < 1.5：该计划严重亏损，降低预算50%或暂停
2. ROI 1.5-2.0：亏损，降低出价10-20%
3. ROI 2.0-目标ROI：正常，小幅优化
4. ROI > 目标ROI × 1.5：超额完成，增加预算20-30%扩大规模
5. CTR < 0.5%：点击率过低，考虑优化创意或暂停关键词
6. CVR < 1%：转化率过低，检查详情页或降价

请输出JSON：
{
  "overall_assessment": "整体评估描述",
  "total_roi": 整体ROI数字,
  "optimizations": [
    {
      "action_type": "bid_adjust/pause_keyword/add_keyword/budget_adjust",
      "campaign_id": "xxx",
      "ad_group_id": "xxx或null",
      "keyword": "关键词或null",
      "before_value": 调整前的值,
      "after_value": 调整后的值,
      "budget_change_pct": 预算变动百分比(正数增加负数减少),
      "reason": "优化理由",
      "expected_impact": "预期效果"
    }
  ]
}
"""
```

---

## 八、ContentAgent — 内容上架Agent

### 8.1 实现（核心节点）

```python
# agents/content_agent.py

class ContentAgent(BaseAgent):

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("prepare_product_data",  self._prepare_product_data)
        graph.add_node("generate_copywriting",  self._generate_copywriting)
        graph.add_node("trigger_image_gen",     self._trigger_image_generation)
        graph.add_node("trigger_video_gen",     self._trigger_video_generation)
        graph.add_node("wait_assets_ready",     self._wait_assets_ready)
        graph.add_node("preview_and_approve",   self._create_approval_task)
        graph.add_node("wait_approval",         self._wait_for_approval)
        graph.add_node("execute_upload",        self._execute_upload)
        graph.add_node("verify_upload",         self._verify_upload)

        graph.set_entry_point("prepare_product_data")
        graph.add_edge("prepare_product_data", "generate_copywriting")
        graph.add_edge("generate_copywriting",  "trigger_image_gen")
        graph.add_edge("trigger_image_gen",     "trigger_video_gen")
        graph.add_edge("trigger_video_gen",     "wait_assets_ready")
        graph.add_edge("wait_assets_ready",     "preview_and_approve")
        graph.add_edge("preview_and_approve",   "wait_approval")

        graph.add_conditional_edges(
            "wait_approval",
            self._route_after_approval,
            {"execute": "execute_upload", "end": END, "wait": "wait_approval"}
        )

        graph.add_edge("execute_upload", "verify_upload")
        graph.add_edge("verify_upload",  END)

        return graph.compile(checkpointer=self.checkpointer)

    async def _generate_copywriting(self, state: AgentState) -> AgentState:
        """生成商品文案"""
        product = state["input_data"]["product"]
        platform = state["input_data"]["platform"]

        result = await self._llm_call(
            system_prompt=COPYWRITING_PROMPT,
            user_content=f"""
商品信息：
- 来源URL：{product.get('source_url', '')}
- 原始标题：{product.get('original_title', '')}
- 品类：{product.get('category', '')}
- 主要卖点：{product.get('selling_points', '')}
- 采购价：¥{product.get('cost', 0)}
- 目标售价：¥{product.get('target_price', 0)}

目标平台：{platform}
平台标题限制：{PLATFORM_UPLOAD_CONFIG[platform]['title_max_length']}字
""",
            model=TEXT_MODEL
        )

        copy_data = json.loads(result)

        # 保存文案到数据库
        for copy_type, content in copy_data.items():
            await db.save_copywriting({
                "tenant_id": state["tenant_id"],
                "product_id": product["id"],
                "platform": platform,
                "type": copy_type,
                "content": content,
                "status": "draft",
            })

        state["input_data"]["copywriting"] = copy_data
        return state

    async def _trigger_image_generation(self, state: AgentState) -> AgentState:
        """触发ImageAgent生成商品图片"""
        image_agent = ImageAgent()
        image_task_state = AgentState(
            task_id=str(uuid4()),
            tenant_id=state["tenant_id"],
            shop_id=state["shop_id"],
            agent_type="image",
            task_type="generate_product_images",
            trigger="internal",
            input_data={
                "product_id": state["input_data"]["product"]["id"],
                "platform": state["input_data"]["platform"],
                "source_image": state["input_data"]["product"].get("source_image"),
            },
            messages=[], decisions=[], tool_calls=[],
            actions=[], requires_approval=False,
            approval_id=None, approval_status="",
            result={}, errors=[], status="running"
        )

        # 异步触发，不等待完成
        asyncio.create_task(image_agent.run(image_task_state))
        state["input_data"]["image_task_id"] = image_task_state["task_id"]
        return state

    async def _wait_assets_ready(self, state: AgentState) -> AgentState:
        """等待图片/视频素材生成完成（最多等30分钟）"""
        image_task_id = state["input_data"].get("image_task_id")
        video_task_id = state["input_data"].get("video_task_id")

        timeout = 1800  # 30分钟
        start = datetime.now()

        while (datetime.now() - start).seconds < timeout:
            image_ready = True
            video_ready = True

            if image_task_id:
                task = await db.get_agent_task(image_task_id)
                image_ready = task.status == "done"

            if video_task_id:
                task = await db.get_agent_task(video_task_id)
                video_ready = task.status == "done"

            if image_ready and video_ready:
                break

            await asyncio.sleep(30)

        # 加载生成的素材
        product_id = state["input_data"]["product"]["id"]
        state["input_data"]["images"] = await db.get_product_images(product_id, status="ready")
        state["input_data"]["videos"] = await db.get_product_videos(product_id, status="ready")

        return state

    async def _execute_upload(self, state: AgentState) -> AgentState:
        """RPA执行上架"""
        shop = await db.get_shop(state["shop_id"])
        rpa = get_rpa_executor()

        upload_data = {
            "title":      state["input_data"]["copywriting"]["title"],
            "description":state["input_data"]["copywriting"]["description"],
            "price":      state["input_data"]["product"]["target_price"],
            "cost":       state["input_data"]["product"]["cost"],
            "images":     [img.storage_path for img in state["input_data"]["images"]],
            "video_path": state["input_data"]["videos"][0].storage_path
                         if state["input_data"]["videos"] else None,
            "category_path": state["input_data"]["product"].get("category_path", []),
            "hashtags":   state["input_data"]["copywriting"].get("hashtags", []),
        }

        result = await rpa.upload_product(
            shop_id=state["shop_id"],
            platform=shop.platform,
            product_data=upload_data
        )

        if result["success"]:
            await db.update_product({
                "id": state["input_data"]["product"]["id"],
                "platform_product_id": result["platform_product_id"],
                "status": "on_sale",
                "listed_at": datetime.now(),
            })

        state["result"]["upload_result"] = result
        return state
```

### 8.2 商品文案Prompt

```python
COPYWRITING_PROMPT = """
你是专业的电商文案师。为商品生成适合指定平台的销售文案。

各平台文案风格：
- pdd：突出性价比、折扣、限时优惠，价格敏感型用户
- taobao：详细介绍、专业感、信任背书，重视品质
- douyin：短促有力、视觉冲击、情绪驱动，年轻用户
- xiaohongshu：生活方式、场景化、种草感，女性用户

请严格输出JSON格式：
{
  "title": "商品标题（符合平台字数限制，包含核心关键词）",
  "description": "详情页文案（200-500字，突出卖点）",
  "bullet_points": ["卖点1", "卖点2", "卖点3", "卖点4", "卖点5"],
  "seo_tags": ["关键词1", "关键词2", "关键词3"],
  "hashtags": ["话题标签1", "话题标签2"],
  "hook_sentence": "30字以内的钩子句，用于视频口播开头"
}
"""
```

---

## 九、ImageAgent & VideoAgent

### 9.1 ImageAgent核心逻辑

```python
# agents/image_agent.py

class ImageAgent(BaseAgent):

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("prepare_source_image",  self._prepare_source_image)
        graph.add_node("remove_background",     self._remove_background)
        graph.add_node("generate_product_shots",self._generate_product_shots)
        graph.add_node("resize_for_platforms",  self._resize_for_platforms)
        graph.add_node("quality_check",         self._quality_check)
        graph.add_node("save_results",          self._save_results)

        graph.set_entry_point("prepare_source_image")
        graph.add_edge("prepare_source_image",  "remove_background")
        graph.add_edge("remove_background",     "generate_product_shots")
        graph.add_edge("generate_product_shots","resize_for_platforms")
        graph.add_edge("resize_for_platforms",  "quality_check")
        graph.add_edge("quality_check",         "save_results")
        graph.add_edge("save_results",          END)

        return graph.compile(checkpointer=self.checkpointer)

    async def _remove_background(self, state: AgentState) -> AgentState:
        """BiRefNet抠图"""
        source_image = state["input_data"]["source_image_path"]
        workflow = load_comfyui_workflow("birefnet_cutout")
        workflow = inject_image_to_workflow(workflow, source_image)

        cutout_images = await run_comfyui_workflow(workflow)
        state["input_data"]["cutout_image_path"] = cutout_images[0]
        return state

    async def _generate_product_shots(self, state: AgentState) -> AgentState:
        """ComfyUI + SD XL + ControlNet生成商品图"""
        cutout_path = state["input_data"]["cutout_image_path"]
        platform = state["input_data"]["platform"]
        product_title = state["input_data"].get("product_title", "")

        # 根据平台选择风格
        style_prompts = {
            "pdd":          "clean white background, professional product photography, studio lighting",
            "taobao":       "clean white background, e-commerce product photo, high quality",
            "douyin":       "lifestyle scene, trendy, vibrant, young aesthetic, natural lighting",
            "xiaohongshu":  "instagram style, warm tones, minimalist, cozy lifestyle"
        }

        generated = []

        # 白底图
        white_bg_workflow = load_comfyui_workflow("white_bg_product")
        white_bg_workflow = inject_image_to_workflow(white_bg_workflow, cutout_path)
        white_bg_images = await run_comfyui_workflow(white_bg_workflow)
        generated.append({"type": "white_bg", "paths": white_bg_images})

        # 场景图
        scene_workflow = load_comfyui_workflow("scene_product")
        scene_workflow = inject_image_to_workflow(scene_workflow, cutout_path)
        scene_workflow = inject_prompt_to_workflow(
            scene_workflow, style_prompts.get(platform, style_prompts["taobao"])
        )
        scene_images = await run_comfyui_workflow(scene_workflow)
        generated.append({"type": "scene", "paths": scene_images})

        state["input_data"]["generated_images"] = generated
        return state

    async def _save_results(self, state: AgentState) -> AgentState:
        """上传图片到OSS，保存到数据库"""
        product_id = state["input_data"]["product_id"]
        platform = state["input_data"]["platform"]

        for group in state["input_data"]["generated_images"]:
            for path in group["paths"]:
                oss_url = await upload_to_oss(path)
                await db.save_product_image({
                    "tenant_id":          state["tenant_id"],
                    "product_id":         product_id,
                    "type":               group["type"],
                    "platform":           platform,
                    "url":                oss_url,
                    "storage_path":       path,
                    "generation_method":  "comfyui",
                    "status":             "ready",
                })

        state["status"] = "done"
        return state
```

### 9.2 VideoAgent核心逻辑

```python
# agents/video_agent.py

class VideoAgent(BaseAgent):

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("analyze_competitor_videos", self._analyze_competitor_videos)
        graph.add_node("generate_script",           self._generate_script)
        graph.add_node("synthesize_voice",          self._synthesize_voice)
        graph.add_node("generate_talking_head",     self._generate_talking_head)
        graph.add_node("compose_final_video",       self._compose_final_video)
        graph.add_node("save_results",              self._save_results)

        graph.set_entry_point("analyze_competitor_videos")
        graph.add_edge("analyze_competitor_videos", "generate_script")
        graph.add_edge("generate_script",           "synthesize_voice")
        graph.add_edge("synthesize_voice",          "generate_talking_head")
        graph.add_edge("generate_talking_head",     "compose_final_video")
        graph.add_edge("compose_final_video",       "save_results")
        graph.add_edge("save_results",              END)

        return graph.compile(checkpointer=self.checkpointer)

    async def _analyze_competitor_videos(self, state: AgentState) -> AgentState:
        """分析竞品爆款视频，获取模板"""
        product = state["input_data"]["product"]
        platform = state["input_data"]["platform"]

        # 先查是否有现成模板
        template = await db.get_best_viral_template(
            category=product.get("category"),
            platform=platform
        )

        if not template:
            # 没有则RPA抓取并分析
            rpa = get_rpa_executor()
            video_urls = await rpa.get_hot_videos(
                keyword=product["title"][:15],
                platform=platform,
                count=10
            )

            templates = []
            for url in video_urls[:5]:
                video_path = await download_video_yt_dlp(url)
                transcript = await whisper_transcribe(video_path)
                template_data = await self._extract_template_from_video(
                    transcript, video_path
                )
                templates.append(template_data)

            template = await self._merge_templates_to_best(templates, product)
            template = await db.save_viral_template({
                "tenant_id": state["tenant_id"],
                "category": product.get("category"),
                "platform": platform,
                **template,
            })

        state["input_data"]["template"] = template
        return state

    async def _generate_script(self, state: AgentState) -> AgentState:
        """生成口播脚本"""
        product = state["input_data"]["product"]
        template = state["input_data"]["template"]
        duration = state["input_data"].get("duration", 30)

        result = await self._llm_call(
            system_prompt=VIDEO_SCRIPT_PROMPT,
            user_content=f"""
商品信息：
{json.dumps(product, ensure_ascii=False, indent=2)}

爆款视频结构模板：
{json.dumps(template.structure, ensure_ascii=False, indent=2)}

目标时长：{duration}秒
目标平台：{state["input_data"]["platform"]}
""",
            model=TEXT_MODEL
        )

        script_data = json.loads(result)

        script = await db.save_oral_script({
            "tenant_id": state["tenant_id"],
            "product_id": product["id"],
            "template_id": str(template.id),
            "script_content": script_data["script"],
            "duration_seconds": script_data["estimated_duration"],
            "tone": script_data["tone"],
            "status": "draft",
        })

        state["input_data"]["script"] = script
        state["input_data"]["script_data"] = script_data
        return state

    async def _synthesize_voice(self, state: AgentState) -> AgentState:
        """CosyVoice2 TTS合成"""
        script = state["input_data"]["script_data"]["script"]

        audio_path = await cosyvoice_synthesize(
            text=script,
            voice=state["input_data"].get("voice_style", "female_warm"),
            output_path=f"temp/audio_{state['task_id']}.wav"
        )

        state["input_data"]["audio_path"] = audio_path
        return state

    async def _generate_talking_head(self, state: AgentState) -> AgentState:
        """MuseTalk生成口播视频"""
        persona = await db.get_next_persona(state["tenant_id"])
        audio_path = state["input_data"]["audio_path"]

        talking_head_path = await musetalk_generate(
            persona_image=persona.image_path,
            audio_path=audio_path,
            output_path=f"temp/talking_head_{state['task_id']}.mp4"
        )

        # 更新使用次数
        await db.increment_persona_usage(persona.id)
        state["input_data"]["talking_head_path"] = talking_head_path
        state["input_data"]["persona_id"] = str(persona.id)
        return state

    async def _compose_final_video(self, state: AgentState) -> AgentState:
        """FFmpeg合成最终视频"""
        product_images = await db.get_product_images(
            state["input_data"]["product"]["id"], status="ready"
        )

        output_path = await ffmpeg_compose(
            talking_head=state["input_data"]["talking_head_path"],
            product_images=[img.storage_path for img in product_images[:3]],
            audio=state["input_data"]["audio_path"],
            script=state["input_data"]["script_data"]["script"],
            platform=state["input_data"]["platform"],
            output_path=f"temp/final_{state['task_id']}.mp4"
        )

        state["input_data"]["final_video_path"] = output_path
        return state

    async def _save_results(self, state: AgentState) -> AgentState:
        oss_url = await upload_to_oss(state["input_data"]["final_video_path"])

        await db.save_product_video({
            "tenant_id":       state["tenant_id"],
            "product_id":      state["input_data"]["product"]["id"],
            "type":            "oral",
            "platform":        state["input_data"]["platform"],
            "url":             oss_url,
            "storage_path":    state["input_data"]["final_video_path"],
            "persona_id":      state["input_data"]["persona_id"],
            "script_id":       str(state["input_data"]["script"].id),
            "template_id":     str(state["input_data"]["template"].id),
            "status":          "ready",
        })

        state["status"] = "done"
        return state
```

### 9.3 视频脚本Prompt

```python
VIDEO_SCRIPT_PROMPT = """
你是一个短视频口播脚本创作专家，专注于电商带货内容。

创作原则：
1. 前3秒必须有强力钩子（痛点/好奇/福利）
2. 自然口语化，不要书面语
3. 多用短句，每句不超过15个字
4. 包含明确的行动号召（下单/收藏/关注）
5. 价格锚点要显著

请严格输出JSON格式：
{
  "script": "完整口播脚本（纯文字，不含时间标注）",
  "estimated_duration": 预估秒数,
  "tone": "亲切/专业/夸张/测评",
  "hook": "前3秒钩子内容",
  "key_points": ["卖点1", "卖点2", "卖点3"],
  "cta": "行动号召语句"
}
"""
```

---

## 十、Celery定时任务配置

```python
# tasks/scheduled.py
from celery import Celery
from celery.schedules import crontab

app = Celery("ecommerce_agents")

app.conf.beat_schedule = {
    # 竞品价格巡检 - 每15分钟
    "price-check-all-shops": {
        "task": "tasks.rpa_tasks.trigger_pricing_agent",
        "schedule": crontab(minute="*/15"),
        "args": ("all_tenants", "competitor_scan"),
    },
    # 订单处理 - 每5分钟
    "process-new-orders": {
        "task": "tasks.rpa_tasks.trigger_inventory_agent",
        "schedule": crontab(minute="*/5"),
        "args": ("all_tenants", "process_new_orders"),
    },
    # 客服巡检 - 每3分钟
    "cs-message-check": {
        "task": "tasks.rpa_tasks.trigger_cs_agent",
        "schedule": crontab(minute="*/3"),
        "args": ("all_tenants", "fetch_new_messages"),
    },
    # 每日选品巡检 - 每天8点
    "daily-selection-scan": {
        "task": "tasks.rpa_tasks.trigger_selection_agent",
        "schedule": crontab(hour=8, minute=0),
        "args": ("all_tenants", "daily_hot_scan"),
    },
    # 广告优化 - 每2小时
    "ads-optimization": {
        "task": "tasks.rpa_tasks.trigger_ads_agent",
        "schedule": crontab(minute=0, hour="*/2"),
        "args": ("all_tenants", "optimize_all"),
    },
    # Cookie健康检查 - 每6小时
    "cookie-health-check": {
        "task": "tasks.rpa_tasks.check_cookie_health",
        "schedule": crontab(minute=0, hour="*/6"),
        "args": ("all_tenants",),
    },
}
```

---

*文档版本：v1.0 | 覆盖9个Agent完整设计 | 配合API接口文档和RPA操作手册使用*

---

# 第五部分：RPA各平台操作手册

**版本：** v1.0  
**适用：** Playwright + DrissionPage 双引擎  
**覆盖平台：** 拼多多 · 淘宝/天猫 · 抖音小店 · 小红书 · 1688  

---

## 总体设计原则

### 反检测三层防护

```
第一层：浏览器指纹伪装
  · User-Agent轮换
  · WebGL/Canvas指纹随机化
  · 屏幕分辨率/时区/语言模拟真实环境

第二层：行为模拟
  · 鼠标轨迹使用贝塞尔曲线（非直线移动）
  · 按键间隔正态分布随机（均值120ms，σ=40ms）
  · 页面停留时间模拟人类阅读节奏
  · 操作前随机滚动页面

第三层：频率控制
  · 每个店铺每小时操作上限可配置
  · 相邻两次操作最小间隔2秒
  · 高风险操作（改价/上下架）每日上限
  · 检测到异常立即停止并告警
```

### 引擎选择策略

| 平台 | 主引擎 | 备用引擎 | 原因 |
|------|--------|---------|------|
| 拼多多 | DrissionPage | Playwright | 拼多多反爬最激进，DrissionPage适配更好 |
| 淘宝/天猫 | Playwright+stealth | DrissionPage | stealth插件可处理大部分检测 |
| 抖音小店 | Playwright+stealth | DrissionPage | 抖音指纹检测较强 |
| 小红书 | Playwright+stealth | - | 相对宽松 |
| 1688 | Playwright | - | 最宽松，标准配置即可 |

### 基础配置

```python
# rpa/config.py

BROWSER_BASE_CONFIG = {
    "headless": False,          # 必须有头模式，无头更容易被检测
    "args": [
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--disable-gpu",
        "--window-size=1920,1080",
    ],
    "ignore_default_args": ["--enable-automation"],
}

STEALTH_SCRIPTS = """
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
    Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN','zh']});
    window.chrome = { runtime: {} };
    Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
"""

# 操作频率限制（每个店铺）
RATE_LIMITS = {
    "pdd":          {"ops_per_hour": 60,  "min_interval_sec": 3},
    "taobao":       {"ops_per_hour": 80,  "min_interval_sec": 2},
    "douyin":       {"ops_per_hour": 50,  "min_interval_sec": 4},
    "xiaohongshu":  {"ops_per_hour": 40,  "min_interval_sec": 3},
    "1688":         {"ops_per_hour": 120, "min_interval_sec": 1},
}

# 高风险操作每日上限
DAILY_LIMITS = {
    "price_update":     {"pdd": 50,  "taobao": 80,  "douyin": 30},
    "product_upload":   {"pdd": 20,  "taobao": 15,  "douyin": 10},
    "product_offshlef": {"pdd": 30,  "taobao": 30,  "douyin": 20},
}
```

### 人类行为模拟工具函数

```python
# rpa/human_behavior.py
import asyncio
import random
import math
from playwright.async_api import Page

async def human_move_mouse(page: Page, x: int, y: int):
    """贝塞尔曲线鼠标移动"""
    current = await page.evaluate("() => ({x: window.mouseX||0, y: window.mouseY||0})")
    cx = random.randint(min(current['x'], x), max(current['x'], x))
    cy = random.randint(min(current['y'], y), max(current['y'], y))
    steps = random.randint(10, 25)
    for i in range(steps + 1):
        t = i / steps
        # 二次贝塞尔曲线
        bx = (1-t)**2 * current['x'] + 2*(1-t)*t * cx + t**2 * x
        by = (1-t)**2 * current['y'] + 2*(1-t)*t * cy + t**2 * y
        await page.mouse.move(bx, by)
        await asyncio.sleep(random.uniform(0.01, 0.03))

async def human_click(page: Page, selector: str):
    """模拟人类点击：移动到元素附近再点击"""
    element = await page.wait_for_selector(selector, timeout=10000)
    box = await element.bounding_box()
    # 点击元素内随机位置（非正中心）
    x = box['x'] + box['width'] * random.uniform(0.3, 0.7)
    y = box['y'] + box['height'] * random.uniform(0.3, 0.7)
    await human_move_mouse(page, x, y)
    await asyncio.sleep(random.uniform(0.1, 0.3))
    await page.mouse.click(x, y)

async def human_type(page: Page, selector: str, text: str, clear_first: bool = True):
    """模拟人类打字"""
    await human_click(page, selector)
    if clear_first:
        await page.keyboard.press("Control+a")
        await page.keyboard.press("Delete")
    for char in text:
        await page.keyboard.type(char)
        # 偶尔停顿，模拟思考
        if random.random() < 0.05:
            await asyncio.sleep(random.uniform(0.3, 0.8))
        else:
            await asyncio.sleep(random.gauss(0.12, 0.04))

async def human_scroll(page: Page, direction: str = "down", distance: int = None):
    """模拟人类滚动"""
    if distance is None:
        distance = random.randint(200, 600)
    delta = distance if direction == "down" else -distance
    steps = random.randint(3, 8)
    for _ in range(steps):
        await page.mouse.wheel(0, delta // steps)
        await asyncio.sleep(random.uniform(0.05, 0.15))

async def random_wait(min_sec: float = 0.5, max_sec: float = 2.0):
    """随机等待"""
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def reading_pause(page: Page):
    """模拟页面加载后的阅读停顿"""
    await asyncio.sleep(random.gauss(1.5, 0.5))
    await human_scroll(page, "down", random.randint(100, 300))
    await asyncio.sleep(random.gauss(0.8, 0.3))
```

---

## 一、拼多多操作手册

> **风险等级：高** — 反自动化机制最激进，优先使用DrissionPage

### 1.1 环境配置

```python
# rpa/platforms/pdd/config.py
from DrissionPage import ChromiumPage, ChromiumOptions

def create_pdd_browser(user_data_dir: str) -> ChromiumPage:
    """
    DrissionPage配置
    user_data_dir: 每个店铺独立用户目录，保持Cookie隔离
    """
    opts = ChromiumOptions()
    opts.set_argument("--no-sandbox")
    opts.set_argument("--disable-blink-features=AutomationControlled")
    opts.set_argument("--window-size=1920,1080")
    opts.set_user_data_path(user_data_dir)

    # 禁用WebDriver特征
    opts.set_argument("--disable-infobars")
    opts.set_pref("credentials_enable_service", False)

    page = ChromiumPage(opts)

    # 注入反检测脚本
    page.run_js(STEALTH_SCRIPTS)

    return page
```

### 1.2 登录流程

```python
# rpa/platforms/pdd/auth.py

PDD_LOGIN_URL = "https://mms.pinduoduo.com/login"

async def pdd_login_qrcode(page) -> dict:
    """
    拼多多扫码登录
    返回：{"status": "waiting", "qrcode_base64": "..."}
    """
    page.get(PDD_LOGIN_URL)
    await reading_pause(page)

    # 等待二维码出现
    qr_element = page.ele(".login-qrcode img", timeout=15)
    if not qr_element:
        raise Exception("二维码加载失败")

    # 截取二维码图片
    qr_base64 = qr_element.attr("src")

    return {
        "status": "waiting",
        "qrcode_base64": qr_base64
    }

async def pdd_check_login_status(page) -> str:
    """
    轮询检测登录状态
    返回：waiting / scanned / success / expired
    """
    current_url = page.url

    if "mms.pinduoduo.com/home" in current_url:
        return "success"

    # 检查是否有扫码成功提示
    scanned_tip = page.ele(".qrcode-scanned-tip", timeout=1)
    if scanned_tip:
        return "scanned"

    # 检查二维码是否过期
    expired_tip = page.ele(".qrcode-expired", timeout=1)
    if expired_tip:
        return "expired"

    return "waiting"

async def pdd_save_cookies(page, shop_id: str):
    """登录成功后保存Cookie"""
    cookies = page.cookies()
    encrypted = encrypt_aes(json.dumps(cookies))
    await db.update_shop_cookies(shop_id, encrypted)
```

### 1.3 商品价格修改

```python
# rpa/platforms/pdd/product.py

PDD_PRODUCT_EDIT_URL = "https://mms.pinduoduo.com/goods/goods_edit?goods_id={goods_id}"

SELECTORS = {
    "price_input":      ".goods-price-input input",
    "sku_price_inputs": ".sku-price-item input",
    "save_button":      ".save-goods-btn",
    "success_toast":    ".toast-success",
}

async def pdd_update_price(
    page,
    platform_product_id: str,
    new_price: float,
    sku_prices: list = None
) -> dict:
    """
    修改拼多多商品价格
    sku_prices: [{"sku_id": "xxx", "price": 49.9}]
    """
    url = PDD_PRODUCT_EDIT_URL.format(goods_id=platform_product_id)
    page.get(url)
    await reading_pause(page)

    try:
        if sku_prices:
            # SKU级别定价
            sku_inputs = page.eles(SELECTORS["sku_price_inputs"])
            for i, sku in enumerate(sku_prices):
                if i < len(sku_inputs):
                    await human_type_dp(sku_inputs[i], str(sku["price"]))
                    await random_wait(0.3, 0.8)
        else:
            # 统一定价
            price_input = page.ele(SELECTORS["price_input"])
            await human_type_dp(price_input, str(new_price))

        await random_wait(0.5, 1.5)

        # 点击保存
        save_btn = page.ele(SELECTORS["save_button"])
        await human_click_dp(save_btn)

        # 等待成功提示
        success = page.ele(SELECTORS["success_toast"], timeout=10)
        if success:
            return {"success": True, "new_price": new_price}
        else:
            raise Exception("保存后未检测到成功提示")

    except Exception as e:
        screenshot_path = await take_screenshot(page, "pdd_price_update_error")
        return {"success": False, "error": str(e), "screenshot": screenshot_path}
```

### 1.4 商品上架

```python
# rpa/platforms/pdd/upload.py

PDD_UPLOAD_URL = "https://mms.pinduoduo.com/goods/goods_add"

async def pdd_upload_product(page, product_data: dict) -> dict:
    """
    拼多多商品上架
    product_data字段：title/price/desc/images/category/specs
    """
    page.get(PDD_UPLOAD_URL)
    await reading_pause(page)

    steps = [
        ("填写标题",      _fill_title),
        ("选择类目",      _select_category),
        ("上传主图",      _upload_images),
        ("填写价格库存",  _fill_price_stock),
        ("填写详情",      _fill_description),
        ("设置规格",      _setup_specs),
        ("提交上架",      _submit),
    ]

    for step_name, step_func in steps:
        try:
            await step_func(page, product_data)
            await random_wait(0.8, 2.0)
        except Exception as e:
            screenshot = await take_screenshot(page, f"pdd_upload_{step_name}_error")
            return {
                "success": False,
                "failed_step": step_name,
                "error": str(e),
                "screenshot": screenshot
            }

    # 获取上架后的商品ID
    platform_product_id = await _get_product_id_after_upload(page)
    return {"success": True, "platform_product_id": platform_product_id}


async def _fill_title(page, data: dict):
    title_input = page.ele(".goods-name-input input")
    await human_type_dp(title_input, data["title"][:60])  # 拼多多限60字符


async def _upload_images(page, data: dict):
    """上传商品主图（最多5张）"""
    upload_zone = page.ele(".image-upload-zone input[type=file]")
    for img_path in data["images"][:5]:
        upload_zone.input(img_path)       # DrissionPage文件上传
        await random_wait(1.5, 3.0)       # 等待图片上传完成
        # 等待缩略图出现
        page.ele(".uploaded-thumb", timeout=15)


async def _select_category(page, data: dict):
    """选择商品类目（三级联动）"""
    category_btn = page.ele(".category-select-btn")
    await human_click_dp(category_btn)
    await random_wait(0.5, 1.0)

    # 逐级选择类目
    for level, cat_name in enumerate(data["category_path"]):
        cat_items = page.eles(f".category-level-{level+1} .cat-item")
        for item in cat_items:
            if cat_name in item.text:
                await human_click_dp(item)
                await random_wait(0.3, 0.8)
                break


async def _submit(page, data: dict):
    submit_btn = page.ele(".submit-goods-btn")
    await human_click_dp(submit_btn)
    # 处理可能出现的二次确认弹窗
    confirm = page.ele(".confirm-dialog .confirm-btn", timeout=3)
    if confirm:
        await human_click_dp(confirm)
```

### 1.5 订单数据抓取

```python
# rpa/platforms/pdd/orders.py

PDD_ORDER_URL = "https://mms.pinduoduo.com/order/list"

async def pdd_fetch_orders(page, status: str = "wait_ship") -> list:
    """
    抓取待发货订单
    status: wait_ship / shipped / completed / refunding
    """
    page.get(PDD_ORDER_URL)
    await reading_pause(page)

    # 点击对应状态Tab
    status_tabs = {
        "wait_ship":  ".tab-wait-ship",
        "shipped":    ".tab-shipped",
        "completed":  ".tab-completed",
        "refunding":  ".tab-refunding",
    }
    tab = page.ele(status_tabs[status])
    await human_click_dp(tab)
    await random_wait(1.0, 2.0)

    orders = []
    while True:
        # 抓取当前页订单
        order_rows = page.eles(".order-row")
        for row in order_rows:
            order = _parse_order_row(row)
            orders.append(order)

        # 翻页
        next_btn = page.ele(".pagination-next:not(.disabled)", timeout=2)
        if not next_btn:
            break
        await human_click_dp(next_btn)
        await random_wait(1.5, 3.0)

    return orders


def _parse_order_row(row) -> dict:
    return {
        "platform_order_id": row.ele(".order-id").text.strip(),
        "product_title":     row.ele(".goods-name").text.strip(),
        "sku_info":          row.ele(".sku-info").text.strip(),
        "quantity":          int(row.ele(".quantity").text.strip()),
        "amount":            row.ele(".amount").text.strip(),
        "buyer_name":        row.ele(".receiver-name").text.strip(),
        "buyer_address":     row.ele(".receiver-address").text.strip(),
        "buyer_phone":       row.ele(".receiver-phone").text.strip(),
        "paid_at":           row.ele(".pay-time").text.strip(),
    }
```

### 1.6 竞品价格采集

```python
# rpa/platforms/pdd/competitor.py

async def pdd_scrape_competitor_prices(page, keyword: str) -> list:
    """搜索关键词，抓取前3页竞品价格"""
    search_url = f"https://mobile.pinduoduo.com/search_result.html?search_key={keyword}"
    page.get(search_url)
    await reading_pause(page)

    # 等待商品列表加载
    await random_wait(2.0, 4.0)

    products = []
    for page_num in range(1, 4):
        items = page.eles(".goods-item")
        for item in items:
            products.append({
                "title":         item.ele(".goods-title").text,
                "price":         float(item.ele(".price-text").text.replace("¥", "")),
                "monthly_sales": item.ele(".sales-info").text,
                "shop_name":     item.ele(".shop-name").text,
                "product_url":   item.attr("href"),
            })

        # 模拟翻页
        await human_scroll(page, "down", 3000)
        await random_wait(2.0, 3.5)

    return products
```

### 1.7 客服消息处理

```python
# rpa/platforms/pdd/customer_service.py

PDD_CS_URL = "https://mms.pinduoduo.com/customer-service/session-list"

async def pdd_fetch_new_messages(page) -> list:
    """抓取未回复的买家消息"""
    page.get(PDD_CS_URL)
    await reading_pause(page)

    sessions = []
    session_items = page.eles(".session-item.unread")
    for item in session_items:
        sessions.append({
            "session_id":   item.attr("data-session-id"),
            "buyer_id":     item.attr("data-buyer-id"),
            "last_message": item.ele(".last-msg").text,
            "unread_count": int(item.ele(".unread-count").text or 0),
        })
    return sessions


async def pdd_reply_message(page, session_id: str, reply_text: str) -> bool:
    """回复买家消息"""
    # 进入会话
    session = page.ele(f"[data-session-id='{session_id}']")
    await human_click_dp(session)
    await random_wait(0.8, 1.5)

    # 输入回复内容
    input_box = page.ele(".chat-input-textarea")
    await human_type_dp(input_box, reply_text)
    await random_wait(0.5, 1.0)

    # 发送
    send_btn = page.ele(".send-btn")
    await human_click_dp(send_btn)
    await random_wait(0.3, 0.8)

    # 确认发送成功
    sent_msg = page.ele(f".message-sent:last-child", timeout=5)
    return sent_msg is not None
```

---

## 二、淘宝/天猫操作手册

> **风险等级：中** — 主要风险是滑块验证码，需要集成打码服务

### 2.1 环境配置

```python
# rpa/platforms/taobao/config.py
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def create_taobao_browser(user_data_dir: str):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        args=[
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1920,1080",
        ],
        ignore_default_args=["--enable-automation"],
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
        viewport={"width": 1920, "height": 1080},
    )

    # 注入stealth脚本到每个新页面
    browser.on("page", lambda page: asyncio.create_task(stealth_async(page)))

    return browser
```

### 2.2 登录流程

```python
# rpa/platforms/taobao/auth.py

TAOBAO_LOGIN_URL = "https://login.taobao.com/member/login.jhtml"
SELLER_CENTER_URL = "https://myseller.taobao.com"

async def taobao_login_qrcode(page) -> dict:
    await page.goto(TAOBAO_LOGIN_URL)
    await reading_pause(page)

    # 切换到二维码登录
    qr_tab = page.locator(".qrcode-login-btn")
    if await qr_tab.count() > 0:
        await human_click(page, ".qrcode-login-btn")
        await random_wait(0.5, 1.0)

    # 获取二维码
    qr_img = page.locator(".qrcode-img img")
    await qr_img.wait_for(timeout=10000)
    qr_src = await qr_img.get_attribute("src")

    return {"status": "waiting", "qrcode_base64": qr_src}


async def taobao_check_login_status(page) -> str:
    current_url = page.url
    if "myseller.taobao.com" in current_url or "home.html" in current_url:
        return "success"
    scanned = await page.locator(".qrcode-scanned").count()
    if scanned > 0:
        return "scanned"
    expired = await page.locator(".qrcode-expired").count()
    if expired > 0:
        return "expired"
    return "waiting"
```

### 2.3 滑块验证码处理

```python
# rpa/platforms/taobao/captcha.py

CAPTCHA_API_URL = "https://api.2captcha.com/createTask"  # 打码平台

async def handle_slider_captcha(page) -> bool:
    """
    处理淘宝滑块验证码
    策略：优先尝试模拟人工滑动，失败后调用打码平台
    """
    slider = await page.query_selector(".nc_iconfont.btn_slide")
    if not slider:
        return True  # 没有验证码，直接通过

    # 策略1：模拟人工滑动
    success = await _simulate_slide(page, slider)
    if success:
        return True

    # 策略2：截图发送打码平台
    screenshot = await page.screenshot()
    result = await _call_captcha_service(screenshot)
    if result:
        await _apply_captcha_result(page, result)
        return True

    # 策略3：暂停，推送告警让人工处理
    await push_alert("taobao", "滑块验证码需要人工处理")
    return False


async def _simulate_slide(page, slider_element) -> bool:
    """模拟人工滑动轨迹"""
    box = await slider_element.bounding_box()
    start_x = box['x'] + box['width'] / 2
    start_y = box['y'] + box['height'] / 2

    await page.mouse.move(start_x, start_y)
    await page.mouse.down()

    # 生成带抖动的滑动轨迹
    track = _generate_slide_track(start_x, start_x + 280)
    for point in track:
        await page.mouse.move(point['x'], start_y + point['y_offset'])
        await asyncio.sleep(point['delay'])

    await page.mouse.up()
    await asyncio.sleep(1.5)

    # 检查是否通过
    success = await page.query_selector(".nc-lang-cnt[data-nc-lang='_yesTEXT']")
    return success is not None


def _generate_slide_track(start_x: float, end_x: float) -> list:
    """生成模拟人类的滑动轨迹（先快后慢，带微小抖动）"""
    track = []
    distance = end_x - start_x
    current = 0
    mid = distance * 0.7  # 前70%距离加速

    while current < distance:
        if current < mid:
            # 加速阶段
            move = random.uniform(8, 15)
        else:
            # 减速阶段
            move = random.uniform(2, 5)

        current = min(current + move, distance)
        track.append({
            'x': start_x + current,
            'y_offset': random.uniform(-1, 1),  # 微小垂直抖动
            'delay': random.uniform(0.008, 0.02)
        })

    return track
```

### 2.4 商品价格修改

```python
# rpa/platforms/taobao/product.py

TAOBAO_ITEM_EDIT_URL = "https://item.taobao.com/sell/publish/upload.htm?item_id={item_id}"

SELECTORS = {
    "price_input":    "#J_DivItemId .item-price input",
    "sku_rows":       ".sku-edit-row",
    "sku_price":      ".sku-price-input input",
    "submit_btn":     "#J_SaveSku, .publish-btn",
    "success_msg":    ".success-message, .success-tip",
}

async def taobao_update_price(
    page,
    item_id: str,
    new_price: float,
    sku_prices: list = None
) -> dict:
    url = TAOBAO_ITEM_EDIT_URL.format(item_id=item_id)
    await page.goto(url, wait_until="networkidle")
    await reading_pause(page)

    # 检查是否有验证码
    captcha_present = await page.query_selector(".nc-container")
    if captcha_present:
        await handle_slider_captcha(page)

    try:
        if sku_prices:
            sku_rows = await page.query_selector_all(SELECTORS["sku_rows"])
            for i, sku in enumerate(sku_prices):
                if i < len(sku_rows):
                    price_input = await sku_rows[i].query_selector(SELECTORS["sku_price"])
                    await human_type(page, None, str(sku["price"]), element=price_input)
                    await random_wait(0.3, 0.8)
        else:
            await human_type(page, SELECTORS["price_input"], str(new_price))

        await random_wait(0.8, 1.5)
        await human_click(page, SELECTORS["submit_btn"])

        # 等待保存成功
        await page.wait_for_selector(SELECTORS["success_msg"], timeout=15000)
        return {"success": True, "new_price": new_price}

    except Exception as e:
        screenshot = await take_screenshot(page, "taobao_price_update_error")
        return {"success": False, "error": str(e), "screenshot": screenshot}
```

### 2.5 订单发货（回填快递单号）

```python
# rpa/platforms/taobao/orders.py

TAOBAO_ORDER_URL = "https://trade.taobao.com/trade/itemlist/list_sold_items.htm"

async def taobao_fill_tracking_number(
    page,
    order_id: str,
    carrier: str,
    tracking_no: str
) -> bool:
    """回填物流单号"""
    await page.goto(TAOBAO_ORDER_URL)
    await reading_pause(page)

    # 搜索订单
    search_input = page.locator(".order-search input")
    await human_type(page, None, order_id, element=search_input)
    await page.keyboard.press("Enter")
    await random_wait(1.5, 3.0)

    # 点击发货按钮
    ship_btn = page.locator(f"[data-order-id='{order_id}'] .ship-btn")
    await human_click(page, None, element=ship_btn)
    await random_wait(0.8, 1.5)

    # 选择快递公司
    carrier_select = page.locator(".carrier-select")
    await carrier_select.select_option(label=carrier)
    await random_wait(0.3, 0.8)

    # 填写快递单号
    tracking_input = page.locator(".tracking-no-input")
    await human_type(page, None, tracking_no, element=tracking_input)
    await random_wait(0.5, 1.0)

    # 确认发货
    confirm_btn = page.locator(".confirm-ship-btn")
    await human_click(page, None, element=confirm_btn)

    # 等待成功
    success = await page.wait_for_selector(".ship-success-tip", timeout=10000)
    return success is not None
```

---

## 三、抖音小店操作手册

> **风险等级：中高** — 指纹检测较强，操作频率限制严格

### 3.1 环境配置

```python
# rpa/platforms/douyin/config.py

DOUYIN_EXTRA_STEALTH = """
    // 抖音额外反检测
    delete window.__nightmare;
    delete window.callPhantom;
    Object.defineProperty(document, 'hidden', {get: () => false});
    Object.defineProperty(document, 'visibilityState', {get: () => 'visible'});
    // 模拟正常的performance timing
    const originalNow = performance.now.bind(performance);
    performance.now = () => originalNow() + Math.random() * 10;
"""

DOUYIN_SHOP_URL = "https://fxg.jinritemai.com"
```

### 3.2 登录流程

```python
# rpa/platforms/douyin/auth.py

DOUYIN_LOGIN_URL = "https://fxg.jinritemai.com/login"

async def douyin_login_qrcode(page) -> dict:
    await page.goto(DOUYIN_LOGIN_URL, wait_until="networkidle")
    await page.evaluate(DOUYIN_EXTRA_STEALTH)
    await reading_pause(page)

    # 抖音小店使用抖音App扫码
    qr_img = page.locator(".login-qrcode img, .qrcode-box img")
    await qr_img.wait_for(timeout=15000)
    qr_src = await qr_img.get_attribute("src")

    return {
        "status": "waiting",
        "qrcode_base64": qr_src,
        "tip": "请使用抖音App扫码登录"
    }


async def douyin_check_login_status(page) -> str:
    if "fxg.jinritemai.com/home" in page.url:
        return "success"
    if "fxg.jinritemai.com/dashboard" in page.url:
        return "success"

    scanned = await page.query_selector(".qrcode-scanned")
    if scanned:
        return "scanned"

    return "waiting"
```

### 3.3 商品上架

```python
# rpa/platforms/douyin/upload.py

DOUYIN_UPLOAD_URL = "https://fxg.jinritemai.com/ffa/mshop/goods/add"

async def douyin_upload_product(page, product_data: dict) -> dict:
    """
    抖音小店上架注意事项：
    1. 标题最长20字符（远短于其他平台）
    2. 必须有视频（强烈建议）
    3. 价格展示逻辑与其他平台不同（划线价/促销价）
    """
    await page.goto(DOUYIN_UPLOAD_URL, wait_until="networkidle")
    await reading_pause(page)

    steps = [
        ("填写标题",     _douyin_fill_title),
        ("上传主图视频", _douyin_upload_media),
        ("选择类目",     _douyin_select_category),
        ("设置价格",     _douyin_set_price),
        ("填写详情",     _douyin_fill_detail),
        ("设置规格",     _douyin_setup_specs),
        ("发布",         _douyin_publish),
    ]

    for step_name, step_func in steps:
        try:
            await step_func(page, product_data)
            await random_wait(1.0, 2.5)
        except Exception as e:
            screenshot = await take_screenshot(page, f"douyin_upload_{step_name}_error")
            return {
                "success": False,
                "failed_step": step_name,
                "error": str(e),
                "screenshot": screenshot
            }

    product_id = await _get_douyin_product_id(page)
    return {"success": True, "platform_product_id": product_id}


async def _douyin_fill_title(page, data: dict):
    """抖音标题限20字"""
    title = data["title"][:20]
    await human_type(page, ".title-input input", title)


async def _douyin_upload_media(page, data: dict):
    """上传图片和视频"""
    # 上传主图（最多9张）
    img_upload = page.locator(".image-upload input[type=file]")
    for img_path in data["images"][:9]:
        await img_upload.set_input_files(img_path)
        await random_wait(2.0, 4.0)
        # 等待上传进度条消失
        await page.wait_for_selector(".upload-progress", state="hidden", timeout=30000)

    # 上传视频（可选但强烈建议）
    if data.get("video_path"):
        video_upload = page.locator(".video-upload input[type=file]")
        await video_upload.set_input_files(data["video_path"])
        # 视频上传时间较长
        await page.wait_for_selector(".video-upload-progress", state="hidden", timeout=120000)


async def _douyin_set_price(page, data: dict):
    """设置抖音价格（含划线价）"""
    # 售价
    await human_type(page, ".price-input input", str(data["price"]))
    await random_wait(0.3, 0.8)

    # 划线价（市场价，选填）
    if data.get("market_price"):
        await human_type(page, ".market-price-input input", str(data["market_price"]))
```

### 3.4 广告投放（千川）

```python
# rpa/platforms/douyin/ads.py

QIANCHUAN_URL = "https://qianchuan.jinritemai.com"

async def douyin_fetch_ads_data(page, campaign_id: str = None) -> list:
    """抓取千川广告数据"""
    await page.goto(f"{QIANCHUAN_URL}/report/ad", wait_until="networkidle")
    await reading_pause(page)

    # 设置日期范围（最近7天）
    await _set_date_range(page, days=7)
    await random_wait(1.0, 2.0)

    ads_data = []
    rows = await page.query_selector_all(".ad-data-row")
    for row in rows:
        ads_data.append({
            "campaign_name": await row.query_selector(".campaign-name") and
                            (await (await row.query_selector(".campaign-name")).text_content()),
            "spend":         _parse_number(await _get_cell_text(row, ".spend-cell")),
            "clicks":        _parse_number(await _get_cell_text(row, ".clicks-cell")),
            "impressions":   _parse_number(await _get_cell_text(row, ".imp-cell")),
            "conversions":   _parse_number(await _get_cell_text(row, ".conv-cell")),
            "roi":           _parse_number(await _get_cell_text(row, ".roi-cell")),
        })

    return ads_data


async def douyin_adjust_bid(page, ad_group_id: str, new_bid: float) -> bool:
    """调整广告出价"""
    await page.goto(f"{QIANCHUAN_URL}/ad/list", wait_until="networkidle")
    await reading_pause(page)

    # 找到广告组并点击编辑
    edit_btn = page.locator(f"[data-adgroup-id='{ad_group_id}'] .edit-bid-btn")
    await human_click(page, None, element=edit_btn)
    await random_wait(0.5, 1.0)

    # 修改出价
    bid_input = page.locator(".bid-input input")
    await human_type(page, None, str(new_bid), element=bid_input)
    await random_wait(0.3, 0.8)

    # 确认
    confirm_btn = page.locator(".confirm-btn")
    await human_click(page, None, element=confirm_btn)

    success = await page.wait_for_selector(".success-tip", timeout=8000)
    return success is not None
```

---

## 四、小红书操作手册

> **风险等级：低中** — 反自动化相对宽松，但内容审核较严

### 4.1 环境配置

```python
# rpa/platforms/xiaohongshu/config.py

XHS_SELLER_URL = "https://seller.xiaohongshu.com"

# 小红书特殊注意事项：
# 1. 图片必须符合小红书美学（ins风/生活方式）
# 2. 标题使用话题标签（#标签）
# 3. 内容审核周期1-24小时，需要监控审核状态
# 4. 发布频率不宜过高（每天不超过5-10个新品）
```

### 4.2 登录流程

```python
# rpa/platforms/xiaohongshu/auth.py

XHS_LOGIN_URL = "https://seller.xiaohongshu.com/login"

async def xhs_login_qrcode(page) -> dict:
    await page.goto(XHS_LOGIN_URL, wait_until="networkidle")
    await reading_pause(page)

    qr_img = page.locator(".qr-code img, .login-qr img")
    await qr_img.wait_for(timeout=15000)
    qr_src = await qr_img.get_attribute("src")

    return {
        "status": "waiting",
        "qrcode_base64": qr_src,
        "tip": "请使用小红书App扫码登录"
    }
```

### 4.3 商品上架

```python
# rpa/platforms/xiaohongshu/upload.py

XHS_UPLOAD_URL = "https://seller.xiaohongshu.com/commodity/publish"

async def xhs_upload_product(page, product_data: dict) -> dict:
    """
    小红书商品上架特点：
    1. 图片风格要求高（需要ins/生活方式风格）
    2. 标题含话题标签
    3. 详情页更像笔记（图文结合）
    """
    await page.goto(XHS_UPLOAD_URL, wait_until="networkidle")
    await reading_pause(page)

    steps = [
        ("上传图片",   _xhs_upload_images),
        ("填写标题",   _xhs_fill_title),
        ("填写描述",   _xhs_fill_description),
        ("选择类目",   _xhs_select_category),
        ("设置价格",   _xhs_set_price),
        ("添加标签",   _xhs_add_hashtags),
        ("发布",       _xhs_publish),
    ]

    for step_name, step_func in steps:
        try:
            await step_func(page, product_data)
            await random_wait(0.8, 2.0)
        except Exception as e:
            screenshot = await take_screenshot(page, f"xhs_upload_{step_name}_error")
            return {
                "success": False,
                "failed_step": step_name,
                "error": str(e),
                "screenshot": screenshot
            }

    product_id = await _get_xhs_product_id(page)
    return {"success": True, "platform_product_id": product_id}


async def _xhs_fill_title(page, data: dict):
    """小红书标题：正文+话题标签，总长度限20字"""
    title = data["title"][:20]
    # 加入话题标签
    if data.get("hashtags"):
        tags = " ".join([f"#{tag}" for tag in data["hashtags"][:3]])
        title = f"{title[:14]} {tags}"
    await human_type(page, ".title-input", title)


async def _xhs_add_hashtags(page, data: dict):
    """添加话题标签"""
    tag_input = page.locator(".hashtag-input")
    for tag in data.get("hashtags", [])[:10]:
        await human_type(page, None, tag, element=tag_input)
        await page.keyboard.press("Enter")
        await random_wait(0.3, 0.8)


async def xhs_check_review_status(page, product_id: str) -> str:
    """检查商品审核状态"""
    review_url = f"https://seller.xiaohongshu.com/commodity/list"
    await page.goto(review_url, wait_until="networkidle")
    await reading_pause(page)

    product_row = page.locator(f"[data-product-id='{product_id}']")
    status_cell = product_row.locator(".review-status")
    status_text = await status_cell.text_content()

    status_map = {
        "审核中": "reviewing",
        "已上架": "on_sale",
        "审核不通过": "rejected",
        "已下架": "off_shelf",
    }
    return status_map.get(status_text.strip(), "unknown")
```

### 4.4 客服消息处理

```python
# rpa/platforms/xiaohongshu/customer_service.py

XHS_CS_URL = "https://seller.xiaohongshu.com/im/session-list"

async def xhs_fetch_messages(page) -> list:
    """抓取小红书未回复消息"""
    await page.goto(XHS_CS_URL, wait_until="networkidle")
    await reading_pause(page)

    sessions = []
    unread_items = await page.query_selector_all(".session-item.has-unread")
    for item in unread_items:
        sessions.append({
            "session_id":   await item.get_attribute("data-session-id"),
            "buyer_name":   await (await item.query_selector(".buyer-name")).text_content(),
            "last_message": await (await item.query_selector(".last-msg")).text_content(),
        })
    return sessions
```

---

## 五、1688操作手册

> **风险等级：低** — 相对宽松，标准Playwright配置即可

### 5.1 选品数据抓取

```python
# rpa/platforms/alibaba_1688/selection.py

ALIBABA_SEARCH_URL = "https://s.1688.com/selloffer/offer_search.htm"

async def alibaba_search_products(
    page,
    keyword: str,
    max_pages: int = 3
) -> list:
    """搜索1688商品，抓取选品数据"""
    products = []

    for page_num in range(1, max_pages + 1):
        url = f"{ALIBABA_SEARCH_URL}?keywords={keyword}&pageNum={page_num}"
        await page.goto(url, wait_until="networkidle")
        await reading_pause(page)
        await human_scroll(page)

        items = await page.query_selector_all(".offer-list-row, .normal-offer-wrapper")
        for item in items:
            try:
                product = await _parse_1688_item(item, page)
                products.append(product)
            except Exception:
                continue

        await random_wait(1.5, 3.0)

    return products


async def _parse_1688_item(item, page) -> dict:
    """解析1688商品卡片数据"""

    title_el = await item.query_selector(".title, .offer-title")
    price_el = await item.query_selector(".price, .offer-price")
    sales_el = await item.query_selector(".sale-count, .deal-cnt")
    supplier_el = await item.query_selector(".supplier-name, .company-name")
    url_el = await item.query_selector("a.title, a.offer-title")

    title = await title_el.text_content() if title_el else ""
    price_text = await price_el.text_content() if price_el else "0"
    sales_text = await sales_el.text_content() if sales_el else "0"
    supplier = await supplier_el.text_content() if supplier_el else ""
    url = await url_el.get_attribute("href") if url_el else ""

    return {
        "title":          title.strip(),
        "price":          _parse_price(price_text),
        "monthly_sales":  _parse_sales(sales_text),
        "supplier_name":  supplier.strip(),
        "url":            url if url.startswith("http") else f"https:{url}",
        "min_order":      1,  # 默认，详情页再抓精确值
    }


async def alibaba_get_product_detail(page, product_url: str) -> dict:
    """获取1688商品详情（产能/发货速度/供应商评分）"""
    await page.goto(product_url, wait_until="networkidle")
    await reading_pause(page)
    await human_scroll(page)

    detail = {}

    # 起订量
    min_order_el = await page.query_selector(".min-order-num, .order-unit")
    if min_order_el:
        detail["min_order"] = await min_order_el.text_content()

    # 发货地
    ship_from_el = await page.query_selector(".ship-address, .product-place")
    if ship_from_el:
        detail["ship_from"] = await ship_from_el.text_content()

    # 供应商评分
    score_el = await page.query_selector(".supplier-score, .company-score")
    if score_el:
        detail["supplier_score"] = await score_el.text_content()

    # 主营类目
    category_el = await page.query_selector(".main-product")
    if category_el:
        detail["main_category"] = await category_el.text_content()

    # 成交量/复购率
    deal_el = await page.query_selector(".deal-cnt")
    if deal_el:
        detail["total_deals"] = await deal_el.text_content()

    return detail


async def alibaba_place_dropship_order(
    page,
    product_url: str,
    order_info: dict
) -> dict:
    """
    1688代发订单
    order_info: {
        "sku_id": "xxx",
        "quantity": 1,
        "receiver_name": "张三",
        "receiver_phone": "138xxxx",
        "receiver_address": "广东省深圳市..."
    }
    """
    await page.goto(product_url, wait_until="networkidle")
    await reading_pause(page)

    # 选择规格
    if order_info.get("sku_specs"):
        for spec_name, spec_value in order_info["sku_specs"].items():
            spec_btn = page.locator(f".property-item[data-value='{spec_value}']")
            await human_click(page, None, element=spec_btn)
            await random_wait(0.3, 0.8)

    # 设置数量
    qty_input = page.locator(".input-number input")
    await human_type(page, None, str(order_info["quantity"]), element=qty_input)

    # 立即购买
    buy_btn = page.locator(".buy-now-btn, .btn-buy-now")
    await human_click(page, None, element=buy_btn)
    await random_wait(1.5, 3.0)

    # 填写收货信息（代发地址）
    await _fill_dropship_address(page, order_info)

    # 提交订单
    submit_btn = page.locator(".submit-order-btn")
    await human_click(page, None, element=submit_btn)
    await random_wait(1.0, 2.0)

    # 支付（如果已设置免密支付）
    pay_btn = page.locator(".pay-btn, .confirm-pay")
    if await pay_btn.count() > 0:
        await human_click(page, None, element=pay_btn)
        await random_wait(2.0, 4.0)

    # 获取订单号
    order_id_el = await page.wait_for_selector(".order-id, .trade-id", timeout=15000)
    order_id = await order_id_el.text_content()

    return {
        "success": True,
        "alibaba_order_id": order_id.strip()
    }
```

### 5.2 供应商数据抓取

```python
# rpa/platforms/alibaba_1688/supplier.py

async def alibaba_get_supplier_info(page, supplier_url: str) -> dict:
    """获取1688供应商详细信息"""
    await page.goto(supplier_url, wait_until="networkidle")
    await reading_pause(page)

    return {
        "name":           await _get_text(page, ".company-name"),
        "score":          await _get_text(page, ".supplier-score"),
        "years":          await _get_text(page, ".company-years"),
        "main_products":  await _get_text(page, ".main-products"),
        "ship_speed":     await _get_text(page, ".ship-speed"),
        "repurchase_rate": await _get_text(page, ".repurchase-rate"),
        "response_rate":  await _get_text(page, ".response-rate"),
    }
```

---

## 六、通用异常处理框架

```python
# rpa/error_handler.py

class RPAException(Exception):
    pass

class CaptchaDetectedError(RPAException):
    pass

class LoginExpiredError(RPAException):
    pass

class ElementNotFoundError(RPAException):
    pass

class RateLimitError(RPAException):
    pass

class BannedError(RPAException):
    pass


class RPAErrorHandler:

    @staticmethod
    async def handle(
        error: Exception,
        shop_id: str,
        platform: str,
        operation: str,
        page=None
    ) -> dict:
        """统一异常处理入口"""

        # 截图存档
        screenshot_url = None
        if page:
            screenshot_url = await take_screenshot(
                page, f"{platform}_{operation}_error"
            )

        if isinstance(error, CaptchaDetectedError):
            # 暂停该店铺所有操作，推送人工处理告警
            await pause_shop(shop_id)
            await push_alert(shop_id, "captcha_detected", {
                "platform": platform,
                "operation": operation,
                "screenshot_url": screenshot_url,
                "message": f"{platform} 检测到验证码，操作已暂停"
            })
            return {"action": "paused", "reason": "captcha"}

        elif isinstance(error, LoginExpiredError):
            await push_alert(shop_id, "cookie_expired", {
                "platform": platform,
                "message": "登录已过期，请重新扫码绑定"
            })
            return {"action": "paused", "reason": "login_expired"}

        elif isinstance(error, BannedError):
            await push_alert(shop_id, "possible_ban", {
                "platform": platform,
                "message": "疑似账号风控，请人工检查账号状态",
                "level": "critical"
            })
            await pause_shop(shop_id)
            return {"action": "paused", "reason": "possible_ban"}

        elif isinstance(error, ElementNotFoundError):
            # 页面结构可能已变更，通知开发团队
            await notify_dev_team({
                "platform": platform,
                "operation": operation,
                "error": str(error),
                "screenshot_url": screenshot_url,
                "message": "页面元素未找到，平台页面结构可能已更新"
            })
            return {"action": "failed", "reason": "element_not_found"}

        elif isinstance(error, RateLimitError):
            # 触发频率限制，等待后重试
            await asyncio.sleep(random.uniform(300, 600))  # 等待5-10分钟
            return {"action": "retry", "reason": "rate_limited"}

        else:
            # 未知错误，记录日志
            logger.error(f"Unknown RPA error: {error}", extra={
                "shop_id": shop_id,
                "platform": platform,
                "operation": operation,
            })
            return {"action": "failed", "reason": str(error)}


class RPARetry:
    """带重试的RPA操作装饰器"""

    @staticmethod
    def with_retry(max_retries: int = 3, backoff: float = 2.0):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                last_error = None
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except (CaptchaDetectedError, BannedError, LoginExpiredError):
                        raise  # 这些不重试，直接上报
                    except Exception as e:
                        last_error = e
                        wait_time = backoff ** attempt + random.uniform(0, 1)
                        await asyncio.sleep(wait_time)
                        logger.warning(f"RPA retry {attempt+1}/{max_retries}: {e}")
                raise last_error
            return wrapper
        return decorator
```

---

## 七、Cookie管理与健康检测

```python
# rpa/cookie_manager.py

class CookieManager:

    COOKIE_CHECK_INTERVAL = 3600  # 每小时检查一次Cookie有效性

    async def check_cookie_health(self, shop_id: str, platform: str, page) -> bool:
        """
        检测Cookie是否仍然有效
        通过访问需要登录的页面并检测是否被重定向到登录页
        """
        check_urls = {
            "pdd":          "https://mms.pinduoduo.com/home",
            "taobao":       "https://myseller.taobao.com",
            "douyin":       "https://fxg.jinritemai.com/home",
            "xiaohongshu":  "https://seller.xiaohongshu.com/home",
            "1688":         "https://portal.1688.com",
        }

        check_url = check_urls.get(platform)
        if not check_url:
            return True

        try:
            await page.goto(check_url, timeout=15000)
            await asyncio.sleep(2)

            current_url = page.url
            login_keywords = ["login", "signin", "auth"]

            if any(kw in current_url.lower() for kw in login_keywords):
                return False  # 被重定向到登录页，Cookie已失效

            return True

        except Exception:
            return False

    async def refresh_cookies(self, shop_id: str, platform: str, page) -> dict:
        """定期刷新Cookie（访问页面触发自动续期）"""
        check_urls = {
            "pdd": "https://mms.pinduoduo.com/home",
            "taobao": "https://myseller.taobao.com",
        }
        url = check_urls.get(platform)
        if url:
            await page.goto(url)
            await asyncio.sleep(2)
            new_cookies = await page.context.cookies()
            encrypted = encrypt_aes(json.dumps(new_cookies))
            await db.update_shop_cookies(shop_id, encrypted, extend_expiry=True)
        return {"refreshed": True}

    async def scheduled_health_check(self):
        """定时任务：检查所有活跃店铺的Cookie状态"""
        shops = await db.get_active_shops()
        for shop in shops:
            is_healthy = await self.check_cookie_health(
                shop.id, shop.platform, await browser_pool.get_page(shop.id)
            )
            if not is_healthy:
                await db.update_shop_status(shop.id, "cookie_expired")
                await push_alert(shop.id, "cookie_expired", {
                    "shop_name": shop.name,
                    "platform": shop.platform,
                    "message": "店铺登录已过期，请重新扫码"
                })
```

---

## 八、截图与日志管理

```python
# rpa/utils.py
import boto3   # 或阿里云OSS SDK
from datetime import datetime
import os

SCREENSHOT_STORAGE = "local"  # local / s3 / oss

async def take_screenshot(page, label: str) -> str:
    """截图并上传存储，返回访问URL"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{label}_{timestamp}.png"

    if SCREENSHOT_STORAGE == "local":
        path = f"screenshots/{filename}"
        os.makedirs("screenshots", exist_ok=True)
        await page.screenshot(path=path, full_page=False)
        return f"/static/screenshots/{filename}"

    elif SCREENSHOT_STORAGE == "oss":
        screenshot_bytes = await page.screenshot(full_page=False)
        # 上传到OSS
        oss_path = f"rpa/screenshots/{filename}"
        oss_client.put_object(oss_path, screenshot_bytes)
        return f"https://your-bucket.oss-cn-hangzhou.aliyuncs.com/{oss_path}"


async def push_alert(shop_id: str, alert_type: str, data: dict):
    """推送告警到WebSocket"""
    from api.websocket import ws_manager
    await ws_manager.broadcast_to_tenant(
        tenant_id=await db.get_tenant_id_by_shop(shop_id),
        message={
            "type": "rpa_alert",
            "data": {
                "shop_id": shop_id,
                "alert_type": alert_type,
                **data
            }
        }
    )


async def notify_dev_team(data: dict):
    """通知开发团队（页面结构变更等需要修复的问题）"""
    # 发送钉钉/企业微信机器人通知
    import httpx
    webhook_url = os.getenv("DEV_ALERT_WEBHOOK")
    if webhook_url:
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json={
                "msgtype": "markdown",
                "markdown": {
                    "title": "RPA告警",
                    "text": f"## RPA页面异常\n"
                           f"**平台：** {data.get('platform')}\n"
                           f"**操作：** {data.get('operation')}\n"
                           f"**错误：** {data.get('message')}\n"
                           f"**截图：** {data.get('screenshot_url')}"
                }
            })
```

---

## 九、平台选择器版本管理

```python
# rpa/selector_manager.py

class SelectorManager:
    """
    选择器版本化管理
    当平台更新页面结构时，只需更新数据库中的选择器，无需修改代码
    """

    async def get_selectors(self, platform: str) -> dict:
        """从数据库获取当前选择器配置"""
        adapter = await db.get_platform_adapter(platform)
        return adapter.selectors

    async def verify_selectors(self, platform: str, page) -> dict:
        """验证选择器是否仍然有效"""
        selectors = await self.get_selectors(platform)
        results = {}

        for name, selector in selectors.items():
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                results[name] = {"valid": element is not None}
            except Exception:
                results[name] = {"valid": False, "selector": selector}

        invalid = {k: v for k, v in results.items() if not v["valid"]}
        if invalid:
            await notify_dev_team({
                "platform": platform,
                "message": f"以下选择器失效：{list(invalid.keys())}",
                "operation": "selector_check"
            })

        return results

    async def update_selector(
        self,
        platform: str,
        selector_name: str,
        new_selector: str
    ):
        """更新单个选择器"""
        adapter = await db.get_platform_adapter(platform)
        adapter.selectors[selector_name] = new_selector
        await db.update_platform_adapter(platform, adapter.selectors)
```

---

## 十、RPA操作频率调度器

```python
# rpa/rate_limiter.py
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    """
    基于令牌桶的操作频率控制
    防止操作过于频繁触发平台风控
    """

    def __init__(self):
        self.shop_last_ops = defaultdict(list)  # shop_id -> [timestamp]

    async def acquire(self, shop_id: str, platform: str, operation: str):
        """获取操作许可，必要时等待"""
        config = RATE_LIMITS.get(platform, {"ops_per_hour": 60, "min_interval_sec": 2})
        daily_config = DAILY_LIMITS.get(operation, {})

        # 检查每小时操作上限
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        recent_ops = [t for t in self.shop_last_ops[shop_id] if t > hour_ago]

        if len(recent_ops) >= config["ops_per_hour"]:
            wait_time = (recent_ops[0] - hour_ago).total_seconds()
            await asyncio.sleep(wait_time + random.uniform(1, 5))

        # 检查最小操作间隔
        if self.shop_last_ops[shop_id]:
            last_op = self.shop_last_ops[shop_id][-1]
            elapsed = (now - last_op).total_seconds()
            if elapsed < config["min_interval_sec"]:
                await asyncio.sleep(config["min_interval_sec"] - elapsed + random.uniform(0.5, 2))

        # 记录本次操作
        self.shop_last_ops[shop_id].append(datetime.now())

        # 清理过期记录（保留最近2小时）
        two_hours_ago = datetime.now() - timedelta(hours=2)
        self.shop_last_ops[shop_id] = [
            t for t in self.shop_last_ops[shop_id] if t > two_hours_ago
        ]

rate_limiter = RateLimiter()
```

---

## 附录：选择器快速更新指南

当平台页面更新导致操作失败时，按以下步骤快速修复：

```
1. 收到告警（DevOps钉钉/企微消息）
2. 打开Chrome开发者工具，进入对应页面
3. 使用Ctrl+F在Elements中搜索对应元素
4. 右键 → Copy → Copy selector 获取新选择器
5. 调用管理后台API更新选择器：
   PATCH /admin/platform-adapters/{platform}/selectors
   {"selector_name": "price_input", "new_selector": ".new-price-input input"}
6. 触发选择器验证任务确认修复成功
7. 无需重新部署代码
```

---

*文档版本：v1.0 | 覆盖平台：拼多多·淘宝·抖音小店·小红书·1688 | 配合API接口文档和ER图使用*

---

# 第六部分：部署运维手册

## 一、硬件要求

### 1.1 客户端标准配置

| 配置项 | 最低要求 | 推荐配置 |
|--------|---------|---------|
| CPU | 8核 | 16核 |
| 内存 | 32GB | 64GB |
| 显卡 | RTX 3060 12GB | RTX 4070 16GB |
| 硬盘 | SSD 500GB | SSD 1TB |
| 网络 | 50Mbps稳定宽带 | 100Mbps+ |
| 操作系统 | Windows 10 64位 | Windows 11 64位 |

**显存说明：**
- ComfyUI + SD XL：需要8GB显存
- MuseTalk口播视频：需要8GB显存
- CosyVoice2 TTS：需要4GB显存
- Whisper large-v3：需要6GB显存
- 建议显卡显存16GB以上，可同时运行多个模型

---

## 二、环境搭建

### 2.1 Python环境

```bash
# 安装Python 3.11
# Windows下载：https://www.python.org/downloads/

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

**requirements.txt 核心依赖：**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
langgraph==0.2.0
langchain-core==0.2.0
openai==1.30.0
playwright==1.44.0
DrissionPage==4.0.4
playwright-stealth==1.0.6
celery==5.3.6
redis==5.0.4
sqlalchemy==2.0.30
alembic==1.13.1
asyncpg==0.29.0
psycopg2-binary==2.9.9
pydantic==2.7.1
pydantic-settings==2.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.27.0
aiofiles==23.2.1
python-multipart==0.0.9
websockets==12.0
yt-dlp==2024.5.1
openai-whisper==20231117
boto3==1.34.101
cryptography==42.0.7
```

```bash
# 安装Playwright浏览器
playwright install chromium
playwright install-deps chromium
```

### 2.2 PostgreSQL安装

```bash
# Windows安装PostgreSQL 15
# 下载：https://www.postgresql.org/download/windows/

# 创建数据库
psql -U postgres
CREATE DATABASE ecommerce_agent;
CREATE USER agent_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_agent TO agent_user;
\q

# 执行数据库迁移
alembic upgrade head
```

### 2.3 Redis安装

```bash
# Windows使用WSL或Redis官方Windows版
# 下载：https://github.com/microsoftarchive/redis/releases

# 启动Redis（默认端口6379）
redis-server

# 验证连接
redis-cli ping
# 返回PONG表示成功
```

### 2.4 ComfyUI安装

```bash
# 克隆ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 安装依赖
pip install -r requirements.txt

# 下载模型（放入models/checkpoints/）
# SD XL基础模型：sd_xl_base_1.0.safetensors
# BiRefNet抠图模型：BiRefNet-general-epoch_244.pth
# ControlNet模型：control-lora-canny-rank128.safetensors

# 启动ComfyUI（默认端口8188）
python main.py --port 8188 --listen 127.0.0.1
```

### 2.5 CosyVoice2安装

```bash
# 克隆CosyVoice2
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice

# 安装依赖
pip install -r requirements.txt

# 下载模型
# 模型放入pretrained_models/CosyVoice2-0.5B/

# 启动API服务（端口50000）
python api.py --port 50000
```

### 2.6 MuseTalk安装

```bash
# 克隆MuseTalk
git clone https://github.com/TMElyralab/MuseTalk.git
cd MuseTalk

# 安装依赖
pip install -r requirements.txt

# 下载模型
# 按官方文档下载所需模型文件

# 启动推理服务（端口50001）
python api_server.py --port 50001
```

### 2.7 QEMU虚拟机配置（微信）

```bash
# Windows安装QEMU
# 下载：https://www.qemu.org/download/#windows

# 创建虚拟机镜像（Windows 10，20GB）
qemu-img create -f qcow2 wechat_vm.qcow2 20G

# 启动虚拟机（带VNC）
qemu-system-x86_64 \
  -m 4096 \
  -hda wechat_vm.qcow2 \
  -cdrom windows10.iso \
  -vnc :1 \
  -netdev user,id=net0 \
  -device e1000,netdev=net0

# VNC端口：5901（:1对应5901）
# 在虚拟机内安装Windows + 微信PC版
# 登录微信后保存虚拟机快照
qemu-img snapshot -c wechat_logged_in wechat_vm.qcow2
```

---

## 三、配置文件

### 3.1 环境变量配置

```bash
# .env 文件
# ─── 基础配置 ───
APP_ENV=production
APP_HOST=127.0.0.1
APP_PORT=8765
SECRET_KEY=your_secret_key_min_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ─── 数据库 ───
DATABASE_URL=postgresql+asyncpg://agent_user:password@localhost:5432/ecommerce_agent
SYNC_DATABASE_URL=postgresql://agent_user:password@localhost:5432/ecommerce_agent

# ─── Redis ───
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# ─── Agnes AI ───
AGNES_API_KEY=your_agnes_api_key
AGNES_BASE_URL=https://apihub.agnes-ai.com/v1

# ─── ComfyUI ───
COMFYUI_URL=http://127.0.0.1:8188

# ─── CosyVoice2 ───
COSYVOICE_URL=http://127.0.0.1:50000

# ─── MuseTalk ───
MUSETALK_URL=http://127.0.0.1:50001

# ─── 虚拟机微信 ───
VM_VNC_HOST=127.0.0.1
VM_VNC_PORT=5901
VM_VNC_PASSWORD=your_vnc_password

# ─── 文件存储 ───
STORAGE_TYPE=local         # local / oss
STORAGE_LOCAL_PATH=./storage
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET=your-bucket
OSS_ACCESS_KEY=your_key
OSS_SECRET_KEY=your_secret

# ─── 加密 ───
AES_KEY=your_32_byte_aes_key_here

# ─── 告警通知 ───
DEV_ALERT_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx

# ─── 打码平台（处理滑块验证码）───
CAPTCHA_API_KEY=your_2captcha_key
```

### 3.2 Supervisor进程管理配置

```ini
# /etc/supervisor/conf.d/ecommerce_agent.conf

[program:fastapi]
command=/path/to/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8765 --workers 2
directory=/path/to/backend
user=agent
autostart=true
autorestart=true
stdout_logfile=/var/log/agent/fastapi.log
stderr_logfile=/var/log/agent/fastapi_err.log
environment=PYTHONPATH="/path/to/backend"

[program:celery_worker_default]
command=/path/to/venv/bin/celery -A tasks.celery_app worker -Q default --concurrency=4 --loglevel=info
directory=/path/to/backend
user=agent
autostart=true
autorestart=true
stdout_logfile=/var/log/agent/celery_worker.log
stderr_logfile=/var/log/agent/celery_worker_err.log

[program:celery_beat]
command=/path/to/venv/bin/celery -A tasks.celery_app beat --loglevel=info
directory=/path/to/backend
user=agent
autostart=true
autorestart=true
stdout_logfile=/var/log/agent/celery_beat.log
stderr_logfile=/var/log/agent/celery_beat_err.log

[program:comfyui]
command=python main.py --port 8188 --listen 127.0.0.1
directory=/path/to/ComfyUI
user=agent
autostart=true
autorestart=true
stdout_logfile=/var/log/agent/comfyui.log
stderr_logfile=/var/log/agent/comfyui_err.log

[program:cosyvoice]
command=python api.py --port 50000
directory=/path/to/CosyVoice
user=agent
autostart=true
autorestart=true
stdout_logfile=/var/log/agent/cosyvoice.log

[program:musetalk]
command=python api_server.py --port 50001
directory=/path/to/MuseTalk
user=agent
autostart=true
autorestart=true
stdout_logfile=/var/log/agent/musetalk.log

[group:ecommerce_agent]
programs=fastapi,celery_worker_default,celery_beat,comfyui,cosyvoice,musetalk
```

```bash
# Supervisor常用命令
supervisorctl reread
supervisorctl update
supervisorctl start ecommerce_agent:*
supervisorctl stop ecommerce_agent:*
supervisorctl restart ecommerce_agent:fastapi
supervisorctl status
```

---

## 四、Tauri桌面端打包

### 4.1 开发环境

```bash
# 安装Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装Node.js（前端构建）
# 下载：https://nodejs.org/

# 安装Tauri CLI
cargo install tauri-cli

# 安装前端依赖
cd desktop
npm install

# 开发模式运行
npm run tauri dev
```

### 4.2 生产打包

```bash
# 构建安装包（生成.msi安装文件）
npm run tauri build

# 输出文件：
# src-tauri/target/release/bundle/msi/多Agent电商系统_1.0.0_x64_en-US.msi
```

### 4.3 Tauri关键配置

```json
// src-tauri/tauri.conf.json
{
  "build": {
    "beforeBuildCommand": "npm run build",
    "beforeDevCommand": "npm run dev",
    "devPath": "http://localhost:1420",
    "distDir": "../dist"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "shell": { "execute": true, "sidecar": true },
      "http": { "all": true, "scope": ["http://127.0.0.1:8765/**"] },
      "notification": { "all": true },
      "window": { "all": true }
    },
    "bundle": {
      "active": true,
      "identifier": "com.ecommerce.agent",
      "icon": ["icons/icon.png"],
      "windows": {
        "wix": { "language": "zh-CN" }
      }
    },
    "windows": [
      {
        "title": "多Agent电商运营系统",
        "width": 1440,
        "height": 900,
        "minWidth": 1280,
        "minHeight": 720,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "systemTray": {
      "iconPath": "icons/icon.png",
      "iconAsTemplate": true,
      "menuOnLeftClick": false
    }
  }
}
```

### 4.4 Rust后端启动Python服务

```rust
// src-tauri/src/main.rs
use std::process::{Command, Child};
use std::sync::Mutex;
use tauri::State;

struct BackendProcess(Mutex<Option<Child>>);

#[tauri::command]
async fn start_backend() -> Result<String, String> {
    let child = Command::new("python")
        .args(["-m", "uvicorn", "main:app",
               "--host", "127.0.0.1",
               "--port", "8765"])
        .current_dir("../backend")
        .spawn()
        .map_err(|e| e.to_string())?;

    Ok(format!("Backend started with PID: {}", child.id()))
}

#[tauri::command]
async fn check_backend_health() -> bool {
    let client = reqwest::Client::new();
    match client.get("http://127.0.0.1:8765/health")
        .timeout(std::time::Duration::from_secs(3))
        .send().await {
        Ok(resp) => resp.status().is_success(),
        Err(_) => false,
    }
}

fn main() {
    tauri::Builder::default()
        .manage(BackendProcess(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![
            start_backend,
            check_backend_health,
        ])
        .setup(|app| {
            // 应用启动时自动启动后端
            let handle = app.handle();
            tauri::async_runtime::spawn(async move {
                start_backend().await.ok();
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## 五、数据库迁移管理

### 5.1 Alembic初始化

```bash
# 初始化Alembic
alembic init migrations

# 生成迁移文件
alembic revision --autogenerate -m "initial_schema"

# 执行迁移
alembic upgrade head

# 回滚一个版本
alembic downgrade -1

# 查看迁移历史
alembic history
```

### 5.2 核心建表SQL

```sql
-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 启用RLS
ALTER DATABASE ecommerce_agent SET app.tenant_id = '';

-- 创建所有表后执行RLS策略
DO $$
DECLARE
  tbl text;
BEGIN
  FOR tbl IN SELECT tablename FROM pg_tables
    WHERE schemaname = 'public'
    AND tablename NOT IN ('plans', 'platform_adapters', 'alembic_version')
  LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
    EXECUTE format(
      'CREATE POLICY tenant_isolation ON %I
       USING (tenant_id = current_setting(''app.tenant_id'', true)::UUID)',
      tbl
    );
  END LOOP;
END $$;

-- 创建关键索引
CREATE INDEX CONCURRENTLY idx_shops_tenant_status
  ON shops(tenant_id, status);
CREATE INDEX CONCURRENTLY idx_products_shop_status
  ON products(shop_id, status);
CREATE INDEX CONCURRENTLY idx_orders_shop_status_created
  ON orders(shop_id, status, created_at DESC);
CREATE INDEX CONCURRENTLY idx_agent_tasks_tenant_status_created
  ON agent_tasks(tenant_id, status, created_at DESC);
CREATE INDEX CONCURRENTLY idx_approval_tasks_pending
  ON approval_tasks(tenant_id, status, priority)
  WHERE status = 'pending';
CREATE INDEX CONCURRENTLY idx_competitor_prices_product_recorded
  ON competitor_prices(product_id, recorded_at DESC);
CREATE INDEX CONCURRENTLY idx_usage_records_tenant_type_recorded
  ON usage_records(tenant_id, resource_type, recorded_at DESC);
CREATE INDEX CONCURRENTLY idx_cs_sessions_shop_status
  ON cs_sessions(shop_id, status);
CREATE INDEX CONCURRENTLY idx_ad_stats_campaign_date
  ON ad_stats(campaign_id, stat_date DESC);
```

---

## 六、监控与告警

### 6.1 健康检查接口

```python
# main.py
@app.get("/health")
async def health_check():
    checks = {}

    # 数据库连接
    try:
        await db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # Redis连接
    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    # ComfyUI
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.COMFYUI_URL}/system_stats", timeout=3
            )
            checks["comfyui"] = "ok" if resp.status_code == 200 else "error"
    except Exception:
        checks["comfyui"] = "unreachable"

    # RPA浏览器池
    checks["browser_pool"] = await browser_pool.health_check()

    # 平台适配器状态
    adapters = await db.get_all_platform_adapters()
    checks["platform_adapters"] = {
        a.platform: "ok" if a.is_healthy else "degraded"
        for a in adapters
    }

    overall = "ok" if all(
        v == "ok" for v in checks.values()
        if isinstance(v, str)
    ) else "degraded"

    return {
        "status": overall,
        "timestamp": datetime.now().isoformat(),
        "checks": checks,
    }
```

### 6.2 关键指标监控

```python
# monitoring/metrics.py

# 每5分钟收集一次关键指标
METRICS_TO_TRACK = [
    "rpa_success_rate",           # RPA操作成功率（目标>95%）
    "agent_avg_response_time_ms", # Agent平均响应时间（目标<30s）
    "pending_approval_count",     # 待审批任务数（预警阈值>20）
    "cookie_expiring_count",      # 即将过期Cookie数
    "celery_queue_depth",         # 任务队列深度（预警阈值>100）
    "cs_auto_reply_rate",         # 客服自动回复率（目标>70%）
    "order_process_lag_minutes",  # 订单处理延迟（目标<10分钟）
]

async def collect_metrics():
    metrics = {}

    # RPA成功率（最近1小时）
    total = await db.count_rpa_ops(hours=1)
    success = await db.count_rpa_ops(hours=1, status="success")
    metrics["rpa_success_rate"] = (success / total * 100) if total > 0 else 100

    # 待审批任务
    metrics["pending_approval_count"] = await db.count_pending_approvals()

    # 队列深度
    metrics["celery_queue_depth"] = await redis.llen("celery")

    # 触发告警
    if metrics["rpa_success_rate"] < 90:
        await notify_dev_team({
            "message": f"RPA成功率下降至 {metrics['rpa_success_rate']:.1f}%",
            "level": "warning"
        })

    if metrics["pending_approval_count"] > 20:
        await ws_manager.broadcast_alert({
            "type": "pending_approvals_overflow",
            "count": metrics["pending_approval_count"],
            "message": f"有{metrics['pending_approval_count']}个任务等待审批"
        })

    return metrics
```

### 6.3 日志规范

```python
# config/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """结构化JSON日志，便于日志分析"""
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        # 附加额外上下文
        if hasattr(record, 'tenant_id'):
            log_data["tenant_id"] = record.tenant_id
        if hasattr(record, 'shop_id'):
            log_data["shop_id"] = record.shop_id
        if hasattr(record, 'task_id'):
            log_data["task_id"] = record.task_id
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": JSONFormatter},
        "simple": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file_json": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 50 * 1024 * 1024,   # 50MB
            "backupCount": 10,
            "formatter": "json",
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/error.log",
            "maxBytes": 20 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "json",
            "level": "ERROR",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file_json", "file_error"],
    },
}
```

---

## 七、安全规范

### 7.1 数据安全

```python
# utils/crypto.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64

# AES-256-GCM加密（用于Cookie和买家信息）
def encrypt_aes(plaintext: str) -> str:
    key = bytes.fromhex(settings.AES_KEY)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()

def decrypt_aes(ciphertext: str) -> str:
    key = bytes.fromhex(settings.AES_KEY)
    aesgcm = AESGCM(key)
    data = base64.b64decode(ciphertext)
    nonce, ciphertext = data[:12], data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
```

### 7.2 API安全

```python
# middleware/security.py

# JWT Token生成与验证
def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token无效或已过期")

# API限流（防止滥用）
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# 使用示例
@app.post("/auth/login")
@limiter.limit("10/minute")   # 登录接口每分钟最多10次
async def login(request: Request, ...):
    ...
```

### 7.3 敏感数据处理规范

```
买家信息（姓名/电话/地址）：
  ✅ AES-256-GCM加密存储在buyer_encrypted字段
  ✅ 只在发货流程中解密使用
  ✅ 日志中不打印买家信息
  ✅ 截图中买家信息自动打码

Cookie存储：
  ✅ AES-256-GCM加密存储
  ✅ 只在RPA执行时解密注入浏览器
  ✅ 不传输到任何第三方服务

LLM调用：
  ✅ 发送给Agnes AI的数据不含买家个人信息
  ✅ 只发送商品标题/价格/类目等非敏感数据
```

---

## 八、常见问题与排查

### 8.1 RPA常见问题

| 问题 | 可能原因 | 排查步骤 |
|------|---------|---------|
| 登录二维码不显示 | 页面加载超时/选择器失效 | 检查网络；更新平台适配器选择器 |
| 改价后价格未变化 | 页面提交失败/验证码阻断 | 查看操作截图；检查是否有验证码 |
| Cookie频繁过期 | 平台安全策略收紧 | 降低操作频率；检查IP是否被标记 |
| 订单抓取为空 | 选择器失效/登录态失效 | 验证Cookie有效性；更新选择器 |
| 图片上传失败 | 图片格式/尺寸不符合要求 | 检查平台图片规格；重新生成图片 |

### 8.2 Agent常见问题

| 问题 | 可能原因 | 排查步骤 |
|------|---------|---------|
| Agent任务卡在pending | Celery Worker未启动 | 检查supervisorctl status |
| LLM返回非JSON格式 | Prompt设计问题 | 检查Agent日志；调整Prompt |
| 审批任务不推送 | WebSocket连接断开 | 检查手机端网络；重新连接 |
| 选品分析评分异常 | 竞品数据抓取失败 | 查看RPA操作日志；检查平台适配器 |

### 8.3 日志查看

```bash
# 查看FastAPI日志
tail -f logs/app.log | python -m json.tool

# 查看错误日志
tail -f logs/error.log

# 查看Celery任务日志
supervisorctl tail -f celery_worker_default

# 查看特定shop_id的日志
cat logs/app.log | grep "shop_id_xxx" | python -m json.tool

# 查看最近1小时RPA失败记录
psql -U agent_user -d ecommerce_agent -c "
  SELECT operation_type, error_message, screenshot_url, started_at
  FROM rpa_operations
  WHERE status = 'failed'
  AND started_at > NOW() - INTERVAL '1 hour'
  ORDER BY started_at DESC
  LIMIT 20;
"
```

---

## 九、版本迭代计划

### v1.0（初始交付）
- 核心RPA框架（拼多多+淘宝）
- 定价/客服/库存Agent
- 桌面端基础版
- 手机端PWA审批

### v1.1（+4周）
- AI作图流水线（ComfyUI）
- 内容上架全自动
- 抖音小店适配器
- 广告Agent

### v1.2（+8周）
- AI视频生成（MuseTalk+CosyVoice2）
- 小红书适配器
- 多租户SaaS化
- 官网+支付系统

### v2.0（+16周）
- 数据分析看板
- 选品预测模型优化
- 直播自动化（抖音）
- 移动端原生App

---

## 十、项目目录结构

```
ecommerce-agent/
├── backend/                    # Python服务端
│   ├── main.py                 # FastAPI入口
│   ├── config/
│   │   ├── settings.py         # 环境配置
│   │   └── logging.py          # 日志配置
│   ├── api/                    # API路由
│   │   ├── auth.py
│   │   ├── shops.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── tasks.py
│   │   ├── approvals.py
│   │   ├── commands.py
│   │   ├── content.py
│   │   ├── ads.py
│   │   ├── cs.py
│   │   ├── billing.py
│   │   ├── dashboard.py
│   │   └── websocket.py
│   ├── agents/                 # Agent层
│   │   ├── state.py
│   │   ├── base_agent.py
│   │   ├── orchestrator.py
│   │   ├── selection_agent.py
│   │   ├── pricing_agent.py
│   │   ├── inventory_agent.py
│   │   ├── ads_agent.py
│   │   ├── cs_agent.py
│   │   ├── content_agent.py
│   │   ├── image_agent.py
│   │   └── video_agent.py
│   ├── rpa/                    # RPA层
│   │   ├── browser_pool.py
│   │   ├── stealth_config.py
│   │   ├── error_handler.py
│   │   ├── rate_limiter.py
│   │   ├── cookie_manager.py
│   │   ├── selector_manager.py
│   │   ├── wechat_vm.py
│   │   └── platforms/
│   │       ├── base_platform.py
│   │       ├── pdd/
│   │       │   ├── auth.py
│   │       │   ├── product.py
│   │       │   ├── orders.py
│   │       │   ├── competitor.py
│   │       │   └── customer_service.py
│   │       ├── taobao/
│   │       │   ├── auth.py
│   │       │   ├── captcha.py
│   │       │   ├── product.py
│   │       │   └── orders.py
│   │       ├── douyin/
│   │       ├── xiaohongshu/
│   │       └── alibaba_1688/
│   ├── tasks/                  # Celery任务
│   │   ├── celery_app.py
│   │   ├── scheduled.py
│   │   └── rpa_tasks.py
│   ├── models/                 # SQLAlchemy模型
│   │   ├── tenant.py
│   │   ├── shop.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── agent_task.py
│   │   ├── content.py
│   │   ├── ads.py
│   │   └── cs.py
│   ├── middleware/
│   │   ├── tenant.py
│   │   └── security.py
│   ├── utils/
│   │   ├── crypto.py
│   │   ├── storage.py
│   │   └── comfyui_client.py
│   ├── db/
│   │   ├── database.py
│   │   └── migrations/
│   ├── monitoring/
│   │   └── metrics.py
│   ├── requirements.txt
│   └── .env
│
├── desktop/                    # Tauri桌面端
│   ├── src/                    # 前端（React/Vue）
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Shops.tsx
│   │   │   ├── Products.tsx
│   │   │   ├── Orders.tsx
│   │   │   ├── Tasks.tsx
│   │   │   ├── Approvals.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   └── hooks/
│   └── src-tauri/              # Rust后端
│       ├── src/
│       │   └── main.rs
│       └── tauri.conf.json
│
├── mobile-pwa/                 # 手机端PWA
│   ├── index.html
│   ├── manifest.json
│   └── src/
│       ├── pages/
│       │   ├── Notifications.vue
│       │   ├── Approvals.vue
│       │   ├── Command.vue
│       │   └── Overview.vue
│       └── components/
│
└── docs/                       # 文档（即本文件所在目录）
    ├── 完整开发文档.md
    ├── ER图.mermaid
    └── ComfyUI工作流/
        ├── white_bg_product.json
        ├── scene_product.json
        └── birefnet_cutout.json
```

---

*文档版本：v1.0 | 完整开发文档，涵盖产品设计至部署运维全流程*
