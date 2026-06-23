# PMO 开发 Agent 角色与分工

> **文档定位：** 定义本项目中 AI 开发 Agent 的职责边界、协作规则与验收标准  
> **维护频率：** 新 Agent 加入或职责调整时更新  
> **文档版本：** v1.0

---

## 一、Agent 总览

| Agent 名称 | 英文代号 | 核心职责 | 主要工作目录 | 主力阶段 |
|-----------|---------|---------|-------------|---------|
| 后端核心 Agent | `backend-core` | API、模型、认证、多租户、业务逻辑 | `backend/app/` | Phase 0~6 |
| RPA 平台 Agent | `rpa-platform` | 浏览器自动化、平台适配器、登录/改价 | `backend/rpa/`, `desktop/src-tauri/` | Phase 2~6 |
| Agent 引擎 Agent | `agent-engine` | LangGraph 工作流、LLM 调用、业务 Agent | `backend/agents/` | Phase 3~6 |
| 前端客户端 Agent | `frontend-client` | Tauri 桌面端、Mobile PWA、用户界面 | `desktop/`, `mobile/` | Phase 7 |
| DevOps & QA Agent | `devops-qa` | 部署、测试、CI/CD、代码质量、验收 | 全局 | 全程 |

---

## 二、各 Agent 详细职责

### 1. 后端核心 Agent（backend-core）

**负责范围：**
- FastAPI 项目骨架与路由组织
- Pydantic Schema 设计（前后端/RPA 共享契约）
- SQLAlchemy ORM 模型与关系
- Alembic 数据库迁移脚本
- JWT 认证、刷新 Token、权限校验
- 多租户中间件、tenant_id 注入、PostgreSQL RLS
- AES 加密/解密（Cookie、敏感配置）
- 业务 Service 层：店铺、商品、订单、用户、审批、通知等
- 通用工具：分页、异常处理、日志、缓存封装

**输出物：**
- `backend/app/api/v1/*.py`
- `backend/app/models/*.py`
- `backend/app/schemas/*.py`
- `backend/app/services/*.py`
- `backend/app/core/*.py`
- `backend/alembic/versions/*.py`

**禁止事项：**
- 不直接操作浏览器（交给 RPA Platform）
- 不写 LangGraph 节点逻辑（交给 Agent Engine）
- 不写前端页面（交给 Frontend Client）

**验收标准：**
- 所有 API 可通过 Swagger UI 调用
- Alembic 迁移可正常升级/降级
- pytest 单元测试覆盖率 ≥ 60%
- 接口变更必须同步更新 `docs/API/`

---

### 2. RPA 平台 Agent（rpa-platform）

**负责范围：**
- Playwright 浏览器实例池管理
- 电商平台适配器抽象层（拼多多优先）
- 登录流程：扫码、Cookie 保存、Cookie 刷新
- 商品改价、订单同步、广告数据抓取等原子操作
- RPA 操作日志、截图/录屏证据链
- 本地机器与阿里云 ECS 的任务分发
- 浏览器指纹/反爬策略基础处理

**输出物：**
- `backend/rpa/*.py`
- `backend/rpa/adapters/pdd.py`
- `backend/rpa/adapters/taobao.py`（Phase 4+）
- `backend/rpa/adapters/douyin.py`（Phase 5+）
- `backend/rpa/adapters/jd.py`（Phase 6+）
- `backend/rpa/pool.py`
- `backend/rpa/recorder.py`

**禁止事项：**
- 不直接写数据库模型（调用 backend-core 提供的 API/Service）
- 不做 LLM 决策（调用 Agent Engine 的决策结果）
- 不写前端界面

**验收标准：**
- 可成功启动浏览器并访问拼多多商家后台
- 扫码登录流程可完整录制并保存 Cookie
- 改价操作可截图留证
- 每个原子操作有独立的错误重试机制

---

### 3. Agent 引擎 Agent（agent-engine）

**负责范围：**
- LangGraph 工作流定义与编排
- LLM Provider 统一封装（Agnes / OpenAI / DeepSeek）
- Prompt 模板管理与版本化
- 业务 Agent 实现：
  - 价格监控 Agent（Phase 3）
  - 智能调价 Agent（Phase 3）
  - 广告投放 Agent（Phase 6）
  - 客服回复 Agent（Phase 5）
  - 选品/上新 Agent（Phase 4）
  - 库存预警 Agent（Phase 4）
  - 售后处理 Agent（Phase 5）
- Agent 执行状态机与日志追踪
- Token 用量统计

**输出物：**
- `backend/agents/graphs/*.py`
- `backend/agents/nodes/*.py`
- `backend/agents/prompts/*.md` 或 `.txt`
- `backend/agents/tools/*.py`
- `backend/agents/runner.py`
- `backend/agents/models.py`

**禁止事项：**
- 不直接操作浏览器（调用 RPA Platform）
- 不修改数据库 Schema（调用 backend-core Service）
- 不硬编码 LLM 密钥（从配置读取）

**验收标准：**
- 每个 Agent 图可独立运行并返回标准输出
- LLM Provider 可通过环境变量切换
- Agent 运行日志完整可追踪
- 决策结果可解释（输出 reasoning）

---

### 4. 前端客户端 Agent（frontend-client）

**负责范围：**
- Tauri 2.4 桌面端应用
- React 19 + Tailwind 4 页面开发
- Mobile PWA 页面开发
- 与后端 API 对接
- 审批弹窗、消息通知、实时状态展示
- 本地配置存储与加密
- 登录窗口与多租户选择

**输出物：**
- `desktop/src/**/*.tsx`
- `desktop/src-tauri/src/*.rs`
- `mobile/src/**/*.tsx`
- `mobile/public/*`

**禁止事项：**
- 不直接访问数据库
- 不在前端硬编码密钥
- 不修改后端接口契约

**验收标准：**
- Tauri 桌面端可打包运行
- PWA 可通过浏览器安装
- 所有页面调用真实 API 无报错
- 响应式布局适配常见屏幕

---

### 5. DevOps & QA Agent（devops-qa）

**负责范围：**
- Docker / Docker Compose 编排维护
- 环境变量与配置管理
- CI/CD 脚本编写
- 测试框架搭建与维护
  - 后端 pytest
  - API 集成测试
  - RPA 端到端测试
  - 前端组件测试
- 代码质量工具
  - pre-commit hooks
  - lint / format
  - 类型检查
- 监控、日志、告警脚本
- 验收 checklist 与自动化
- 代码合并前的冲突检测

**输出物：**
- `docker-compose.yml`
- `backend/Dockerfile`
- `.github/workflows/*.yml`
- `backend/tests/**/*.py`
- `desktop/tests/**/*.ts`
- `mobile/tests/**/*.ts`
- `.pre-commit-config.yaml`
- `pyproject.toml`
- `Makefile`

**禁止事项：**
- 不写业务逻辑代码
- 不修改接口契约
- 不引入未经 decision_log 确认的依赖

**验收标准：**
- `docker compose up` 可启动全部服务
- `pytest` 全部通过
- pre-commit 无错误
- 每次 Phase Gate 能出具验收报告

---

## 三、跨 Agent 协作接口

### 1. 数据流约定

```
Frontend Client  ←→  Backend Core API  ←→  Database/Cache
                            ↓
                    Agent Engine（决策）
                            ↓
                    RPA Platform（执行）
                            ↓
                    电商平台（拼多多等）
```

### 2. 接口契约

| 调用方向 | 调用方式 | 说明 |
|---------|---------|------|
| Frontend → Backend | HTTP API | 按 OpenAPI 规范 |
| Agent Engine → Backend | 直接调用 Service 函数 | 同进程内调用 |
| Agent Engine → RPA | 通过 Celery Task | `rpa.tasks.execute_action()` |
| RPA → 电商平台 | Playwright | 浏览器自动化 |
| RPA → Backend | HTTP API 或 Service 函数 | 上传截图、Cookie、执行结果 |
| DevOps/QA → 全部 | 测试代码 | 不改动业务代码 |

### 3. 共享文件

以下文件任何 Agent 修改前必须经过 PMO 协调：

- `backend/app/schemas/*.py`
- `backend/app/models/*.py`
- `PORT_CONFIG.md`
- `ARCHITECTURE.md`
- `docs/PMO/traceability_matrix.md`
- `docs/PMO/decision_log.md`
- `backend/pyproject.toml`
- `backend/requirements*.txt`

---

## 四、工单分配规则

每个工单必须明确指定负责 Agent：

```markdown
**负责 Agent:** backend-core
**依赖 Agent:** devops-qa
**协作 Agent:** rpa-platform
```

工单类型与默认负责 Agent：

| 工单类型 | 默认 Agent | 示例 |
|---------|-----------|------|
| 数据库模型 | backend-core | CODE-006 |
| API 接口 | backend-core | CODE-007 |
| 认证/租户 | backend-core | CODE-008 |
| RPA 浏览器 | rpa-platform | CODE-029 ~ CODE-034 |
| LangGraph | agent-engine | CODE-023, CODE-027 |
| 业务 Agent | agent-engine | CODE-020 ~ CODE-022 |
| 桌面端 | frontend-client | 待创建 |
| PWA | frontend-client | 待创建 |
| Docker/CI/测试 | devops-qa | CODE-002 及后续 |

---

## 五、冲突解决流程

1. **Agent 内部冲突** → Agent 自行统一风格
2. **跨 Agent 接口冲突** → 提交到 PMO，由 PMO 裁决
3. **依赖版本冲突** → 进 `decision_log.md`，全体 Agent 遵守
4. **代码合并冲突** → DevOps/QA Agent 负责检测并通知相关 Agent

---

## 六、变更记录

| 时间 | 变更人 | 变更内容 |
|------|--------|---------|
| 2026-06-24 | OpenCode | 创建 v1.0，定义 5 个 Agent |
