# CODE-005: 全局配置与日志

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-005 |
| **阶段** | Phase 0 |
| **负责 Agent** | `backend-core` |
| **协作 Agent** | `devops-qa` |
| **依赖** | CODE-001, CODE-003 |
| **被依赖** | CODE-006 及后续所有 backend 工单 |
| **原文档章节** | `重写开发计划.md` Phase 0 |
| **优先级** | P0 |

---

## 目标

建立统一的全局配置管理和结构化日志系统，所有后续模块共用同一套配置与日志。

---

## 交付文件

```
backend/app/
├── core/
│   ├── __init__.py
│   ├── config.py           # Pydantic Settings 全局配置
│   └── logging.py          # structlog 配置
├── main.py                 # 注入配置与日志
└── tests/
    └── test_config.py      # 配置加载测试
```

---

## 配置要求

### Settings 类（Pydantic Settings）

必须包含以下配置项：

```python
class Settings(BaseSettings):
    # 应用
    app_env: str = "development"
    app_name: str = "ecomAgentOS"
    app_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 6200
    secret_key: str
    
    # 数据库
    database_url: str
    
    # Redis
    redis_url: str
    
    # LLM
    llm_provider: str = "agnes"
    agnes_api_key: str | None = None
    agnes_base_url: str | None = None
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    deepseek_api_key: str | None = None
    deepseek_base_url: str | None = None
    
    # 日志
    log_level: str = "INFO"
    log_format: str = "json"  # json | console
```

### 环境变量来源

- `.env` 文件
- 系统环境变量
- `.env.example` 由 devops-qa 在 CODE-002 维护

---

## 日志要求

- 使用 `structlog`
- 支持 JSON 格式（生产）和 Console 格式（开发）
- 每个请求生成 `request_id`
- 日志包含：timestamp、level、logger、message、request_id
- FastAPI 中间件记录请求日志：method、path、status_code、duration_ms

---

## 验收标准

### 1. 配置加载
- [ ] `from app.core.config import settings` 可正常导入
- [ ] `.env` 文件中的值被正确加载
- [ ] 缺少必填项时启动报错信息清晰
- [ ] 支持 `APP_ENV`、`DATABASE_URL` 等环境变量覆盖

### 2. 日志输出
- [ ] 启动时输出结构化日志
- [ ] 每个 HTTP 请求记录一条 access log
- [ ] access log 包含 request_id、method、path、status_code、duration_ms
- [ ] `LOG_LEVEL=DEBUG` 时输出 debug 级别日志

### 3. 代码质量
- [ ] `make check` 通过
- [ ] `pytest tests/test_config.py` 通过

---

## 约束

- `secret_key` 必须必填，不能给默认值
- 数据库 URL 支持 asyncpg（`postgresql+asyncpg://`）
- 日志配置在 `app.core.logging` 中初始化，在 `main.py` 中导入
- 不要重复实现，确保 CODE-004 能复用 settings

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
source .venv/bin/activate
cp .env.example .env
# 编辑 .env 填入 SECRET_KEY 和 DATABASE_URL、REDIS_URL
python -c "from app.core.config import settings; print(settings.app_name)"
python -c "from app.core.logging import get_logger; get_logger().info('test log')"
make test
make check
```

---

## 回执格式

1. 修改的文件列表
2. 配置加载测试输出
3. 日志输出示例
4. 是否通过全部验收标准
