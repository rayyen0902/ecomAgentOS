# 系统架构设计

> **文档版本：** v1.0
> **最后更新：** 2026-06-23
> **设计目标：** 支持「本地单机」和「阿里云+本地混合」两种部署模式，预留SaaS化扩展接口

---

## 一、部署架构总览

### 1.1 模式一：本地单机（开发/初期使用）

```
┌─────────────────────────────────────────────────────────────────┐
│                        单台Windows/Mac电脑                        │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │  Tauri桌面端      │                                          │
│  │  React + Rust    │                                          │
│  └────────┬─────────┘                                          │
│           │ HTTP :6200                                         │
│  ┌────────▼─────────┐     ┌──────────────┐    ┌─────────────┐ │
│  │  FastAPI后端      │────▶│ PostgreSQL   │    │ Redis       │ │
│  │  Python + Agent   │     │ :6210        │    │ :6211       │ │
│  │  + RPA引擎        │     └──────────────┘    └─────────────┘ │
│  └────────┬─────────┘                                          │
│           │ Playwright/DrissionPage                              │
│  ┌────────▼─────────┐                                          │
│  │  浏览器集群        │                                          │
│  │  拼多多/淘宝/抖音  │                                          │
│  └──────────────────┘                                          │
│                                                                 │
│  PWA移动端 ←──── WebSocket :6200 ────→ 审批通知/指令           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**适用场景：**
- 开发调试
- 个人/小团队初期使用（5人以下）
- 不需要远程访问

**特点：**
- 一键启动（Tauri自动启动Python后端）
- 所有数据本地存储
- 账号Cookie本地管理，不上传云端

---

### 1.2 模式二：阿里云 + 本地混合（推荐生产）

```
┌─────────────────────────────┐              ┌─────────────────────────────┐
│      阿里云服务器            │              │      用户本地电脑            │
│  （API + 数据 + 任务调度）    │◄────────────▶│  （RPA执行 + 桌面端UI）      │
│                             │   HTTPS/WSS  │                             │
│  ┌───────────────────────┐  │              │  ┌───────────────────────┐  │
│  │ Nginx (443 HTTPS)     │  │              │  │ Tauri桌面端            │  │
│  │ 反向代理 → FastAPI    │  │              │  │ React + Rust          │  │
│  └───────────┬───────────┘  │              │  └───────────┬───────────┘  │
│              │ :6200         │              │              │              │
│  ┌───────────▼───────────┐  │              │  ┌───────────▼───────────┐  │
│  │ FastAPI主服务          │  │              │  │ RPA浏览器集群          │  │
│  │ - API网关              │  │              │  │ - Playwright           │  │
│  │ - Agent编排            │  │              │  │ - DrissionPage         │  │
│  │ - WebSocket推送        │  │              │  │ - 反检测               │  │
│  └───────────┬───────────┘  │              │  └───────────┬───────────┘  │
│              │              │              │              │              │
│  ┌───────────▼───┐ ┌──────▼────┐         │              │ 拼多多/淘宝  │
│  │ PostgreSQL    │ │ Redis     │         │              │ 抖音/小红书  │
│  │ :6210 (内网)   │ │ :6211     │         │              └─────────────┘
│  └───────────────┘ └───────────┘         │
│                                           │
│  ┌───────────────────────┐               │              ┌─────────────┐
│  │ Celery Worker/Beat    │               │              │ PWA移动端    │
│  │ 异步任务队列          │               │              │ 浏览器访问   │
│  └───────────────────────┘               │              └──────┬──────┘
│                                           │                     │
└─────────────────────────────┘              └─────────────────────┘
                                             HTTPS/WSS → 阿里云:443
```

**适用场景：**
- 团队协作（多用户共用一套数据）
- 需要远程审批（老板不在公司也能批）
- SaaS化前期过渡

**特点：**
- API和数据在阿里云，RPA在本地（账号安全）
- 本地电脑关机时，阿里云上的Agent决策和任务队列仍然运行
- 开机后本地RPA自动连接云端，执行积压任务

---

### 1.3 模式三：纯SaaS（未来扩展）

```
┌─────────────────────────────────────────────────────────────────┐
│                        云端SaaS平台                              │
│                                                                 │
│  用户注册 → 创建租户 → 分配Celery队列 → 下载桌面客户端          │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ 官网/控制台  │  │ FastAPI集群  │  │ 多租户数据库             │ │
│  │ Next.js     │  │ 负载均衡     │  │ PostgreSQL + RLS        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                 │
│  用户本地电脑：Tauri桌面端 + RPA浏览器（同模式二）               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**当前状态：** 架构预留接口，第二期实现

---

## 二、技术架构分层

### 2.1 整体分层

```
┌─────────────────────────────────────────────┐
│  表现层 (Presentation)                       │
│  ├── Tauri桌面端 (React + Rust)              │
│  └── PWA移动端 (React + Vite)                │
├─────────────────────────────────────────────┤
│  接入层 (Gateway)                            │
│  ├── Nginx (反向代理 + HTTPS)                │
│  ├── FastAPI (API路由 + WebSocket)           │
│  ├── JWT认证中间件                           │
│  ├── 多租户中间件 (TenantMiddleware)          │
│  └── API限流 (SlowAPI)                       │
├─────────────────────────────────────────────┤
│  业务层 (Business)                           │
│  ├── Agent编排 (LangGraph 1.x)               │
│  │   ├── OrchestratorAgent (调度中枢)        │
│  │   ├── PricingAgent (定价)                 │
│  │   ├── SelectionAgent (选品)               │
│  │   ├── InventoryAgent (库存)               │
│  │   ├── CustomerServiceAgent (客服)         │
│  │   ├── AdsAgent (广告)                     │
│  │   └── ContentAgent (内容)                 │
│  ├── 审批流引擎                              │
│  ├── 自然语言指令解析                        │
│  └── 任务调度 (Celery)                       │
├─────────────────────────────────────────────┤
│  RPA层 (Automation)                          │
│  ├── 浏览器池 (BrowserPool)                  │
│  ├── 反检测引擎 (Stealth)                    │
│  ├── 频率限制器 (RateLimiter)                │
│  ├── Cookie管理器                            │
│  ├── 选择器管理器 (SelectorManager)          │
│  └── 平台适配器                              │
│      ├── 拼多多 (DrissionPage)               │
│      ├── 淘宝 (Playwright+Stealth)           │
│      ├── 抖音小店 (Playwright)               │
│      ├── 小红书 (Playwright)                 │
│      └── 1688 (Playwright)                   │
├─────────────────────────────────────────────┤
│  AI层 (AI Services)                          │
│  ├── LLMProvider抽象层                       │
│  │   ├── AgnesProvider (默认)                │
│  │   ├── OpenAIProvider (备用)               │
│  │   └── DeepSeekProvider (备用)             │
│  ├── ImageProvider抽象层                     │
│  │   ├── AgnesImageProvider (默认)           │
│  │   └── ComfyUIImageProvider (可选本地)     │
│  └── VideoProvider抽象层                     │
│      ├── AgnesVideoProvider (默认)           │
│      └── CustomVideoProvider (可选本地)      │
├─────────────────────────────────────────────┤
│  数据层 (Data)                               │
│  ├── PostgreSQL 16 (主数据库)                │
│  ├── Redis 7 (缓存 + 消息队列)               │
│  └── 文件存储 (本地/OSS/S3)                  │
├─────────────────────────────────────────────┤
│  基础设施 (Infrastructure)                   │
│  ├── Docker Compose                          │
│  ├── Alembic (数据库迁移)                    │
│  ├── 结构化日志 (JSON)                       │
│  ├── 健康检查 (/health)                      │
│  └── 监控告警 (Prometheus + Grafana 预留)    │
└─────────────────────────────────────────────┘
```

---

## 三、关键设计决策

### 3.1 为什么API和数据上云，RPA留在本地？

| 考量 | 本地RPA | 云端API |
|------|---------|---------|
| **账号安全** | Cookie在本地浏览器，不上传 | 无需处理敏感Cookie |
| **平台风控** | 本地IP正常用户行为 | 云端IP批量操作易被识别 |
| **合规** | 用户自行承担 | 平台方不触碰店铺账号 |
| **可靠性** | 依赖本地网络 | 阿里云SLA保障 |
| **团队协作** | 单用户 | 多用户共享数据 |
| **远程访问** | 必须开机 | 云端24小时运行 |

**结论：** 混合架构是最佳平衡点。

### 3.2 为什么用Agnes API而不是本地ComfyUI？

**初期（第一期）：**
- Agnes图片 $0.003/张，视频 $0/秒
- 零硬件投入，任何电脑都能跑
- 快速验证产品价值

**未来（当Agnes不够用时）：**
- 实现 `ComfyUIImageProvider`，复用相同接口
- 改配置 `IMAGE_PROVIDER=comfyui`
- **业务代码零改动**

### 3.3 为什么LangGraph 1.x？

旧代码用 0.0.20，文档设计用 0.2.x。当前最新是 **1.2.6**。

LangGraph 1.x 相比旧版的重大改进：
- **状态持久化**：PostgresSaver，任务中断可恢复
- **并发执行**：`Send` 节点，多店铺并行
- **人机回环**：内置 `interrupt` 机制，审批等待更优雅
- **调试工具**：LangSmith集成（可选）

### 3.4 多租户设计

**从第一天就预留：**
- 所有数据表带 `tenant_id` 字段
- PostgreSQL RLS 行级安全策略
- JWT Token 中包含 `tenant_id`
- 套餐限制和用量统计表预留

**第一期简化：**
- 单租户硬编码（无需登录选择租户）
- 套餐限制先mock，不做真实校验
- 为未来SaaS化保留全部数据结构

---

## 四、数据流示例

### 4.1 定价Agent端到端流程

```
[定时触发] Celery Beat 每15分钟
    │
    ▼
[Orchestrator] 遍历所有活跃店铺
    │
    ▼
[PricingAgent] 对每个店铺：
    │
    ├── 1. RPA抓取竞品价格（拼多多/淘宝搜索）
    │   └── 数据存入 competitor_prices 表
    │
    ├── 2. LLM分析定价策略（Agnes API）
    │   └── Prompt: "竞品降价20%，建议跟价吗？"
    │   └── 返回JSON: {action, new_price, reason, confidence}
    │
    ├── 3. 风险评估
    │   └── 变动>15% → 标记 high_risk
    │
    ├── 4. 审批路由
    │   ├── high_risk → 创建approval_task → WebSocket推送手机端
    │   └── low_risk → 直接执行改价
    │
    ├── 5. 等待审批（手机端用户操作）
    │   └── 用户点击「同意」→ 更新approval_task状态
    │
    ├── 6. RPA执行改价
    │   └── 登录店铺 → 找到商品 → 修改价格 → 保存 → 截图
    │
    ├── 7. 结果验证
    │   └── 1分钟后再次抓取价格，确认修改成功
    │
    └── 8. 记录完整日志
        └── agent_tasks (决策) → rpa_operations (操作) → screenshots
```

### 4.2 店铺绑定流程

```
用户点击「添加店铺」
    │
    ▼
选择平台（拼多多）
    │
    ▼
后端启动独立浏览器实例（DrissionPage）
    │
    ▼
打开拼多多登录页，截取二维码
    │
    ▼
用户手机扫码
    │
    ▼
后端轮询检测登录状态（每秒1次，最多120秒）
    │
    ▼
登录成功 → 提取Cookie → AES加密 → 存入数据库
    │
    ▼
店铺加入管理列表，状态为 active
```

---

## 五、SaaS化扩展接口预留

### 5.1 预留的SaaS能力

| 能力 | 当前实现 | 预留接口 |
|------|---------|---------|
| 多租户 | 单租户硬编码 | 全部表有tenant_id + RLS |
| 用户管理 | 单用户 | users表（owner/admin/operator角色） |
| 套餐限制 | mock | tenant_configs表（max_shops/images/videos） |
| 用量计费 | mock | usage_records表 |
| 支付系统 | mock | subscriptions + recharge_records表 |
| 团队管理 | 无 | tenants.invite_code + users.tenant_id |
| API密钥 | 无 | api_keys表（未来开放API） |

### 5.2 从本地到SaaS的迁移路径

```
Phase 1（现在）: 本地单机
    │
    ├── 数据库结构和RLS从第一天就建好
    ├── 所有API接口天然支持tenant_id
    └── 单机使用无需感知多租户
    │
Phase 2（+4周）: 阿里云混合部署
    │
    ├── 数据库迁到阿里云RDS
    ├── FastAPI部署到阿里云ECS
    ├── 本地只保留RPA+桌面端
    └── 多用户可通过不同账号访问同一tenant
    │
Phase 3（+12周）: SaaS化
    │
    ├── 官网注册/登录/支付
    ├── 多租户数据隔离正式生效
    ├── 套餐限制和用量计费启用
    └── 开放API供第三方集成
```

---

## 六、安全设计

### 6.1 认证与授权

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   用户      │────▶│  登录API    │────▶│  JWT Token  │
│             │     │  /auth/login│     │  {user_id,  │
└─────────────┘     └─────────────┘     │   tenant_id,│
                                        │   role}     │
                                        └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │  后续请求   │
                                        │  Header:    │
                                        │  Bearer xxx │
                                        └─────────────┘
```

### 6.2 敏感数据加密

| 数据 | 存储方式 | 加密算法 |
|------|---------|---------|
| 用户密码 | bcrypt哈希 | bcrypt (salt=12) |
| 店铺Cookie | AES加密后存JSONB | AES-256-GCM |
| 买家信息 | AES加密后存JSONB | AES-256-GCM |
| API密钥 | 环境变量 | 不存入数据库 |
| JWT密钥 | 环境变量 | 不存入数据库 |

### 6.3 RPA安全

- 每个店铺独立浏览器上下文，Cookie隔离
- 操作频率限制（每小时/每日上限）
- 异常自动暂停（验证码/登录过期）
- 所有操作截图存档，可追溯

---

## 七、性能设计

### 7.1 并发模型

| 场景 | 并发策略 |
|------|---------|
| 多店铺RPA | 每个店铺独立浏览器实例，异步并发 |
| Agent决策 | LangGraph状态图串行执行，但多店铺可并行 |
| API请求 | FastAPI异步处理，单进程可支撑1000+并发 |
| 定时任务 | Celery分布式Worker，水平扩展 |

### 7.2 缓存策略

| 数据 | 缓存位置 | TTL |
|------|---------|-----|
| 店铺Cookie | 内存（BrowserPool） | 会话期间 |
| 商品列表 | Redis | 5分钟 |
| 竞品价格 | Redis | 15分钟 |
| 用户Token | Redis | 24小时 |
| LLM响应 | 无（实时决策） | - |

---

## 八、目录结构（重写后）

```
ecomAgentOS/
├── PORT_CONFIG.md              # 端口配置规范（本文件旁边）
├── ARCHITECTURE.md             # 架构设计文档
├── 重写开发计划.md              # 实施路线图
├── .env.example                # 环境变量模板
├── .gitignore
├── docker-compose.yml          # 基础设施编排
├── Dockerfile                  # 后端镜像
│
├── backend/                    # Python服务端
│   ├── main.py                 # FastAPI入口
│   ├── config/
│   │   ├── settings.py         # pydantic-settings配置
│   │   └── logging.py          # 结构化日志
│   ├── core/                   # 核心基础设施
│   │   ├── llm/
│   │   │   ├── provider.py     # LLMProvider抽象
│   │   │   └── factory.py      # 工厂方法
│   │   ├── content/
│   │   │   ├── image.py        # ImageProvider抽象
│   │   │   └── video.py        # VideoProvider抽象
│   │   ├── crypto.py           # AES-256-GCM加密
│   │   └── exceptions.py       # 业务异常
│   ├── api/                    # API路由
│   │   ├── deps.py             # 共享依赖（db/user/tenant）
│   │   ├── auth.py             # JWT认证
│   │   ├── shops.py            # 店铺管理
│   │   ├── products.py         # 商品管理
│   │   ├── orders.py           # 订单管理
│   │   ├── tasks.py            # Agent任务
│   │   ├── approvals.py        # 审批队列
│   │   ├── commands.py         # 自然语言指令
│   │   ├── dashboard.py        # 仪表盘数据
│   │   ├── billing.py          # 套餐/用量（预留）
│   │   └── websocket.py        # WebSocket推送
│   ├── agents/                 # Agent层（LangGraph 1.x）
│   │   ├── base.py             # BaseAgent + AgentState
│   │   ├── orchestrator.py     # 调度中枢
│   │   ├── pricing.py          # 定价Agent
│   │   ├── inventory.py        # 库存Agent
│   │   ├── selection.py        # 选品Agent
│   │   ├── cs.py               # 客服Agent
│   │   ├── ads.py              # 广告Agent
│   │   └── content.py          # 内容Agent
│   ├── rpa/                    # RPA引擎
│   │   ├── browser_pool.py     # 浏览器池
│   │   ├── rate_limiter.py     # 频率限制器
│   │   ├── cookie_manager.py   # Cookie管理
│   │   ├── error_handler.py    # 异常处理
│   │   ├── selector_manager.py # 选择器版本管理
│   │   ├── stealth.py          # 反检测配置
│   │   └── platforms/          # 平台适配器
│   │       ├── base.py         # BasePlatform抽象
│   │       ├── pdd.py          # 拼多多（DrissionPage）
│   │       ├── taobao.py       # 淘宝（Playwright）
│   │       ├── douyin.py       # 抖音小店
│   │       ├── xiaohongshu.py  # 小红书
│   │       └── alibaba_1688.py # 1688
│   ├── tasks/                  # Celery任务
│   │   ├── celery_app.py       # Celery配置
│   │   └── scheduled.py        # 定时任务
│   ├── models/                 # SQLAlchemy模型
│   │   ├── base.py             # 基类 + 公共字段
│   │   ├── tenant.py           # 租户/用户/订阅
│   │   ├── shop.py             # 店铺
│   │   ├── product.py          # 商品
│   │   ├── order.py            # 订单
│   │   └── task.py             # 任务/审批/RPA操作
│   ├── db/
│   │   ├── database.py         # 引擎 + Session工厂
│   │   └── migrations/         # Alembic迁移
│   ├── middleware/
│   │   ├── auth.py             # JWT验证
│   │   ├── tenant.py           # 多租户注入
│   │   └── rate_limit.py       # API限流
│   ├── tests/                  # pytest测试
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_pricing_agent.py
│   │   └── test_rpa_pdd.py
│   ├── requirements.txt        # Python依赖
│   └── .env.example            # 后端环境变量
│
├── desktop/                    # Tauri桌面端
│   ├── src/                    # React前端
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Shops.tsx
│   │   │   ├── Products.tsx
│   │   │   ├── Orders.tsx
│   │   │   ├── Tasks.tsx
│   │   │   ├── Approvals.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   ├── hooks/
│   │   └── stores/             # Zustand状态
│   ├── src-tauri/              # Rust后端
│   │   ├── src/
│   │   │   └── main.rs         # Tauri主程序
│   │   ├── Cargo.toml          # Tauri v2
│   │   └── tauri.conf.json
│   └── package.json
│
├── mobile/                     # PWA移动端
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   └── pages/
│   │       ├── Notifications.tsx
│   │       ├── Approvals.tsx
│   │       ├── Command.tsx
│   │       └── Overview.tsx
│   └── package.json
│
└── docs/                       # 文档
    ├── 完整开发文档.md
    ├── 重写开发计划.md
    └── ER图.mermaid
```

---

## 九、变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-06-23 | v1.0 | 初始架构设计，支持本地/混合/SaaS三种模式 |
