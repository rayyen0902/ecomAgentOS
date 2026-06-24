# CODE-006 验收报告

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-006 |
| **工单名称** | 数据库模型与 Alembic |
| **验收 Agent** | acceptance Agent |
| **验收日期** | 2026-06-24 |
| **负责 Agent** | backend-core |

---

## 验收结果

### 1. 文件存在

| 文件/目录 | 结果 | 证据 |
|-----------|------|------|
| `backend/alembic/env.py` | 通过 | 2654 bytes，支持 asyncpg |
| `backend/alembic/script.py.mako` | 通过 | 634 bytes |
| `backend/alembic.ini` | 通过 | 880 bytes |
| `backend/alembic/versions/` 含迁移 | 通过 | `c7a680450fab_init_core_tables.py` |
| `backend/app/db/base.py` | 通过 | TimestampMixin + UUIDMixin + TenantMixin |
| `backend/app/db/session.py` | 通过 | AsyncSessionLocal + create_async_engine |
| `backend/app/db/dependencies.py` | 通过 | get_db() FastAPI 依赖 |
| `backend/app/models/` （12 模型文件） | 通过 | 15 个模型文件含 `__init__.py` |
| `backend/tests/test_models.py` | 通过 | 244 行，19 个测试用例 |

### 2. 12 张核心表模型

| 表名 | 模型类 | 结果 |
|------|--------|------|
| `tenants` | Tenant | 通过 |
| `users` | User | 通过 |
| `shops` | Shop | 通过 |
| `platform_adapters` | PlatformAdapter | 通过 |
| `products` | Product | 通过 |
| `product_snapshots` | ProductSnapshot | 通过 |
| `skus` | SKU | 通过 |
| `price_history` | PriceHistory | 通过 |
| `orders` | Order | 通过 |
| `refund_orders` | RefundOrder | 通过 |
| `approval_policies` | ApprovalPolicy | 通过 |
| `approval_requests` | ApprovalRequest | 通过 |
| `agent_runs` | AgentRun | 通过 |
| `agent_steps` | AgentStep | 通过 |

附加：`ai_usage_logs` (AIUsageLog) 已在本次一并创建。

### 3. 技术要求

| 检查项 | 结果 | 证据 |
|--------|------|------|
| SQLAlchemy 2.0 + asyncpg | 通过 | `create_async_engine` in `session.py:11` |
| UUID 主键 | 通过 | `UUIDMixin`: `id = Column(UUID(as_uuid=True), primary_key=True)` |
| 业务表含 tenant_id | 通过 | `TenantMixin` 模式 + 各模型显式定义 |
| DateTime(timezone=True) | 通过 | `TimestampMixin.created_at` / `updated_at` |
| JSONB 字段 | 通过 | 多处使用 `from sqlalchemy.dialects.postgresql import JSONB` |
| 外键建立索引 | 通过 | 各模型 `__table_args__` 定义 `Index` |
| 模型可从 `app.models` 统一导入 | 通过 | `__init__.py` 导出全部 15 个模型 |

### 4. Alembic 迁移

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `alembic.ini` 配置正确 | 通过 | 文件存在，`env.py` 覆盖 `sqlalchemy.url` |
| `env.py` 支持 asyncpg | 通过 | `async_engine_from_config` + `run_async_migrations()` |
| `alembic upgrade head` 成功 | 通过 | 日志 `Running upgrade -> c7a680450fab, init core tables` |
| `alembic downgrade -1` 成功 | 通过 | 日志 `Running downgrade c7a680450fab ->` |
| 再 `alembic upgrade head` 成功 | 通过 | 重新创建所有表 |

### 5. 测试

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `pytest tests/test_models.py` | 通过 | 19 passed |
| 模型属性验证 | 通过 | 15 个 test_x_model_import 用例 |
| 迁移测试 | 通过 | test_upgrade_head + test_downgrade_1 |
| health endpoint mock DB 测试 | 通过 | test_health_endpoint_with_database |

### 6. 代码质量

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `make check` | 通过 | `All checks passed! 42 files already formatted` |
| `make test` (全量) | **通过（附注）** | 40 passed，首次运行在手动 downgrade-upgrade 脏状态下可复现 1 次偶发失败，二次运行通过 |

### 7. Docker 部署

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `docker compose up -d --build` | **不通过** | API 启动失败：`ModuleNotFoundError: No module named 'sqlalchemy'` |
| `curl http://localhost:6200/api/v1/health` | **不通过** | 无响应（服务未启动） |
| db/redis/flower 服务正常 | 通过 | 3 个服务 Up (healthy) |

---

## 总体结论

- **[ ] 通过**
- **[x] 不通过（发现 1 个严重缺陷）**

---

## 缺陷列表

### 缺陷 1：严重 — Docker API 服务启动失败

**问题：** `docker compose up -d --build` 后，api 容器启动崩溃，无法响应任何请求。

**根因：**
```
File "/app/app/api/v1/health.py", line 6, in <module>
    from sqlalchemy import text
ModuleNotFoundError: No module named 'sqlalchemy'
```

`backend/Dockerfile` 仅执行 `pip install .`（从 `pyproject.toml` 安装 fastapi/uvicorn/pydantic/httpx），但 CODE-006 引入的 `health.py` 依赖 `sqlalchemy`、`asyncpg`、`pydantic-settings`、`structlog`、`tenacity` 等大量新依赖，这些仅在 `requirements.txt` 中声明，未被 Docker 镜像安装。

**修复方向：** 在 `Dockerfile` 中改为 `pip install -r requirements.txt && pip install .` 或扩展 `pyproject.toml` 的 dependencies 列表。

### 次要观察（非阻塞）

1. **测试隔离脆弱性** — `TestMigration.test_upgrade_head` 在 `make test` 全量运行时，若 DB 状态被手动操作干扰（如手动 `alembic downgrade` 后再跑），可能触发 `DuplicateTable` 错误。建议在测试中添加 alembic 状态预检查或使用 `conftest.py` fixture 重置。

2. **deprecation warning** — `app/db/base.py:10` 使用旧版 `declarative_base()` API，SQLAlchemy 2.0 已废弃，建议迁移到 `sqlalchemy.orm.DeclarativeBase`。

---

## 缺陷修复验证

### CODE-006-FIX 修复结果

| 项目 | 结果 | 证据 |
|------|------|------|
| Dockerfile 已添加 `requirements.txt` 安装 | 通过 | `RUN pip install -r requirements.txt` 在 `pip install .` 之前 |
| `docker compose up -d --build` 成功 | 通过 | 4 服务全绿 |
| `/api/v1/health` 返回 `database: ok` | 通过 | 响应包含 `{"database": "ok"}` |
| `make check` | 通过 | 无错误 |
| `make test` | 通过 | 全部通过 |

### 修复后结论

**CODE-006 严重缺陷已修复，Phase 0 全部验收通过。**

> **流程记录：** DevOps-QA Agent 曾主张"该缺陷不存在"，但验收结论以 acceptance Agent 复测结果为准。执行 Agent 无权否决验收结论。

---

## 签名

acceptance Agent
2026-06-24
