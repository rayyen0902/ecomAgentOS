# CODE-004: LLM Provider 抽象与日志

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-004 |
| **阶段** | Phase 0 |
| **负责 Agent** | `agent-engine` |
| **协作 Agent** | `backend-core`, `devops-qa` |
| **依赖** | CODE-001, CODE-003 |
| **被依赖** | CODE-027 及后续 Agent 相关工单 |
| **原文档章节** | 原设计 6 / 12，AD-007 |
| **优先级** | P0 |

---

## 目标

建立统一的 LLM Provider 抽象层，支持通过环境变量切换 Agnes / OpenAI / DeepSeek，并记录 LLM 调用日志。

---

## 交付文件

```
backend/app/
├── core/
│   └── llm.py              # LLM 配置与 Provider 工厂
├── services/
│   └── llm_service.py      # 统一调用入口
├── schemas/
│   └── llm.py              # 请求/响应 Schema
├── models/
│   └── ai_usage_log.py     # AI 用量日志模型（占位，CODE-006 细化）
└── agents/
    ├── __init__.py
    └── tools/
        └── llm_tool.py     # 对 Agent 暴露的工具函数
```

---

## 技术要求

- 使用 `openai` SDK 1.x 兼容接口
- 支持 `LLM_PROVIDER` 环境变量：`agnes` | `openai` | `deepseek`
- 支持对应 `*_API_KEY` 和 `*_BASE_URL`
- 默认模型：
  - Agnes: `agnes-large-latest`
  - OpenAI: `gpt-4o`
  - DeepSeek: `deepseek-chat`

---

## 接口设计

### LLMService

```python
class LLMService:
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse: ...

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]: ...
```

### LLMResponse Schema

```python
class LLMResponse(BaseModel):
    content: str
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    created_at: datetime
```

---

## 验收标准

### 1. Provider 切换
- [ ] 设置 `LLM_PROVIDER=agnes` 时调用 Agnes API
- [ ] 设置 `LLM_PROVIDER=openai` 时调用 OpenAI API
- [ ] 设置 `LLM_PROVIDER=deepseek` 时调用 DeepSeek API
- [ ] 不支持的 provider 抛出清晰错误

### 2. 日志记录
- [ ] 每次调用记录到 `ai_usage_logs`（或至少提供记录函数）
- [ ] 日志包含：provider、model、prompt_tokens、completion_tokens、total_tokens、latency_ms

### 3. 测试
- [ ] 提供 mock provider 测试，不依赖真实 API key
- [ ] 测试覆盖 provider 工厂、chat 调用、参数传递

### 4. 文档
- [ ] `backend/README.md` 中说明如何配置 LLM

---

## 约束

- 不要硬编码任何 API key
- 不要提交包含真实 key 的 `.env`
- Agnes base URL 默认：`https://api.agnes.ai/v1`
- 所有调用必须可异步
- 错误处理需包含重试（tenacity）

---

## 环境变量示例

```bash
# Agnes
LLM_PROVIDER=agnes
AGNES_API_KEY=sk-xxx
AGNES_BASE_URL=https://api.agnes.ai/v1
AGNES_DEFAULT_MODEL=agnes-large-latest

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_DEFAULT_MODEL=gpt-4o

# DeepSeek
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_DEFAULT_MODEL=deepseek-chat
```

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
source .venv/bin/activate
export LLM_PROVIDER=mock
pytest tests/test_llm_service.py -v
make check
```

---

## 回执格式

1. 修改的文件列表
2. 各 provider 切换测试结果
3. `pytest` 输出
4. 是否通过全部验收标准
