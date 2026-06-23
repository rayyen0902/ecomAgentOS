# CODE-006: 数据库模型与 Alembic

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-006 |
| **阶段** | Phase 0 |
| **负责 Agent** | `backend-core` |
| **协作 Agent** | `devops-qa` |
| **依赖** | CODE-001, CODE-003, CODE-005 |
| **被依赖** | CODE-007 ~ CODE-009, CODE-013, CODE-017 等 |
| **原文档章节** | 原设计 Part 2 数据库设计；`重写开发计划.md` Phase 0 |
| **优先级** | P0 |

---

## 目标

建立 Phase 0 所需的 12 张核心数据表，使用 SQLAlchemy 2.0 + asyncpg，配置 Alembic 迁移。

---

## 交付文件

```
backend/
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_init_core_tables.py
├── app/
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py           # declarative_base
│   │   ├── session.py        # AsyncSessionLocal
│   │   └── dependencies.py   # get_db 依赖
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tenant.py         # tenants
│   │   ├── user.py           # users
│   │   ├── shop.py           # shops
│   │   ├── platform_adapter.py # platform_adapters
│   │   ├── product.py        # products / product_snapshots
│   │   ├── sku.py            # skus
│   │   ├── price_history.py  # price_history
│   │   ├── order.py          # orders
│   │   ├── refund_order.py   # refund_orders
│   │   ├── approval_policy.py # approval_policies
│   │   ├── approval_request.py # approval_requests
│   │   ├── agent_run.py      # agent_runs
│   │   └── agent_step.py     # agent_steps
│   └── schemas/
│       └── __init__.py       # 公共 Schema 占位
└── tests/
    └── test_models.py        # 模型基础测试
```

---

## 12 张核心表

| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `tenants` | 租户 | id, name, slug, status, plan_id, created_at |
| `users` | 用户 | id, tenant_id, email, hashed_password, is_active |
| `shops` | 店铺 | id, tenant_id, platform, shop_name, cookies_encrypted, status, config_json |
| `platform_adapters` | 平台适配器 | id, platform, adapter_code, version, enabled |
| `products` | 商品主表 | id, tenant_id, shop_id, platform_product_id, title, status |
| `product_snapshots` | 商品快照 | id, product_id, snapshot_data, created_at |
| `skus` | SKU | id, product_id, sku_code, price, stock |
| `price_history` | 价格历史 | id, sku_id, old_price, new_price, source, created_at |
| `orders` | 订单 | id, tenant_id, shop_id, platform_order_id, amount, status, created_at |
| `refund_orders` | 售后单 | id, order_id, refund_type, amount, status |
| `approval_policies` | 审批策略 | id, tenant_id, agent_type, auto_approve, threshold_json |
| `approval_requests` | 审批请求 | id, tenant_id, policy_id, payload, status, approved_by |
| `agent_runs` | Agent 运行 | id, tenant_id, agent_type, shop_id, status, started_at, ended_at |
| `agent_steps` | Agent 步骤 | id, run_id, step_name, input, output, status |

> 注：以上是 Phase 0 核心 12 张表。`ai_usage_logs` 可在本工单中创建或留到 CODE-027。`notifications` 留到 Phase 3。

---

## 技术要求

- SQLAlchemy 2.0 + asyncpg
- 所有主键使用 UUID
- 所有业务表包含 `tenant_id`（除平台配置表外）
- 时间字段使用 `DateTime(timezone=True)`
- JSON 字段使用 `JSONB`（PostgreSQL）
- 外键建立索引
- 软删除使用 `deleted_at` 字段（可选，本次可不加）

---

## Alembic 要求

- [ ] `alembic.ini` 配置正确
- [ ] `alembic/env.py` 支持 asyncpg
- [ ] 初始迁移 `0001_init_core_tables.py` 可生成 12 张表
- [ ] `alembic upgrade head` 成功
- [ ] `alembic downgrade -1` 成功

---

## 多租户预留

- 每张业务表包含 `tenant_id: UUID`
- 为 `tenant_id` 建立索引
- 本次不强制实现 RLS（CODE-008 实现），但 Schema 必须支持

---

## 验收标准

### 1. 模型定义
- [ ] 12 张表的 SQLAlchemy 模型全部定义
- [ ] 模型关系正确（shop.tenant、product.shop、sku.product 等）
- [ ] 所有模型可从 `app.models` 统一导入

### 2. 迁移
- [ ] `alembic revision --autogenerate -m "init core tables"` 能生成迁移
- [ ] `alembic upgrade head` 能在本地 PostgreSQL 创建表
- [ ] `alembic downgrade -1` 能回滚

### 3. 数据库连接
- [ ] `AsyncSessionLocal` 可创建异步会话
- [ ] `get_db()` 可作为 FastAPI 依赖使用
- [ ] `/health` 扩展为检查 DB 连接（可选但推荐）

### 4. 测试
- [ ] `pytest tests/test_models.py` 通过
- [ ] 测试至少创建并查询一条 tenant 记录

### 5. Docker
- [ ] `docker compose up -d` 后 API 服务能连接 PostgreSQL
- [ ] `docker compose logs api` 无数据库连接错误

---

## 约束

- 不要复制旧代码 `archive/backend/db/init.sql`
- 不要一次性创建全部 46 张表，仅 Phase 0 所需的 12 张
- 所有数据库密码从环境变量读取
- 模型文件必须类型注解完整

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
source .venv/bin/activate

# 本地 PostgreSQL 已运行在 6210
cp .env.example .env
# 编辑 .env: DATABASE_URL=postgresql+asyncpg://ecom:password@localhost:6210/ecomagentos

alembic revision --autogenerate -m "init core tables"
alembic upgrade head

# 验证表已创建
psql postgresql://ecom:password@localhost:6210/ecomagentos -c "\dt"

pytest tests/test_models.py -v
make check

# Docker 验证
cd /Users/caopinggege/Desktop/ecomAgentOS
docker compose up -d --build
sleep 10
docker compose logs api --tail 20
curl -s http://localhost:6200/api/v1/health | python -m json.tool
```

---

## 回执格式

1. 修改的文件列表
2. `alembic upgrade head` 输出
3. `\dt` 表列表截图/输出
4. `pytest tests/test_models.py` 输出
5. Docker 健康检查结果
6. 是否通过全部验收标准
