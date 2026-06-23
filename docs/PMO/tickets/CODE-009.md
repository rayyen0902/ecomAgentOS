# CODE-009: 店铺管理核心接口

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-009 |
| **阶段** | Phase 1 |
| **负责 Agent** | `backend-core` |
| **验收 Agent** | `acceptance` |
| **依赖** | CODE-006, CODE-007, CODE-008 |
| **被依赖** | CODE-010, CODE-014, CODE-015 等 |
| **原文档章节** | 原设计 4.1 店铺管理 |
| **优先级** | P0 |

---

## 目标

实现店铺 CRUD、配置管理、状态控制、日报数据查询。

**必须遵守 Phase 1 通用规范：** `docs/PMO/phase1_common_spec.md`

---

## 交付文件

```
backend/app/
├── api/v1/
│   └── shops.py             # /shops/* 路由
├── schemas/
│   └── shop.py              # Shop Schema
├── services/
│   └── shop_service.py      # 店铺业务逻辑
└── tests/
    └── test_shops.py        # 店铺接口测试
```

---

## API 接口

### POST /api/v1/shops

创建店铺（此时 Cookie 为空，状态为 pending_bind）。

**请求：**
```json
{
  "platform": "pdd",
  "shop_name": "我的拼多多店铺"
}
```

**响应：**
```json
{
  "id": "uuid",
  "platform": "pdd",
  "shop_name": "我的拼多多店铺",
  "status": "pending_bind",
  "created_at": "..."
}
```

### GET /api/v1/shops

查询当前租户店铺列表，含今日基础指标。

**响应：**
```json
{
  "items": [
    {
      "id": "uuid",
      "platform": "pdd",
      "shop_name": "...",
      "status": "active",
      "today_orders": 0,
      "today_sales": 0,
      "created_at": "..."
    }
  ],
  "total": 1
}
```

### GET /api/v1/shops/{shop_id}

获取店铺详情，包含配置字段。

### PUT /api/v1/shops/{shop_id}

更新店铺配置。

**可更新字段：**
```json
{
  "shop_name": "新名称",
  "config": {
    "min_margin": 0.1,
    "price_floor": 0.9,
    "max_daily_price_changes": 10
  }
}
```

### POST /api/v1/shops/{shop_id}/pause

暂停店铺 Agent。

### POST /api/v1/shops/{shop_id}/resume

恢复店铺 Agent。

### DELETE /api/v1/shops/{shop_id}

解绑/删除店铺（软删除）。

### GET /api/v1/shops/{shop_id}/metrics

获取店铺日报数据（今日/近7天/近30天）。

> **数据来源说明：** 本工单 `today_orders` / `today_sales` 直接返回 0（mock）。真实数据由后续订单同步工单（CODE-018 / CODE-032）提供，到时替换为从 `orders` 表聚合。

---

## 店铺状态机

```
pending_bind → active → paused → active
                  ↓
              deleted
```

---

## 字段要求

- `platform` 枚举：`pdd`, `taobao`, `douyin`, `jd`
  - 使用 `Platform(str, Enum)` 定义
  - 新增平台时同步修改枚举 + `platform_adapters` 表
- `cookies_encrypted`：AES 加密存储（CODE-008）
- `config`：JSONB，当前预定义字段如下（可扩展）：
  ```json
  {
    "min_margin": 0.1,
    "price_floor": 0.9,
    "max_daily_price_changes": 10,
    "auto_approve_price_change": false
  }
  ```
- `status`：pending_bind / active / paused / deleted

## 分页与过滤

- `GET /shops` 支持 `page`、`page_size` 分页
- `page_size` 上限 100（见通用规范）
- 列表默认过滤 `deleted_at IS NULL`，不返回已删除店铺
- 支持按 `platform`、`status` 过滤

---

## 验收标准

- [ ] 创建店铺成功，状态为 pending_bind
- [ ] 只能查看当前租户店铺
- [ ] 更新店铺配置成功
- [ ] 暂停/恢复店铺状态切换正确
- [ ] 删除店铺后查询不到（软删除）
- [ ] 访问其他租户店铺返回 403/404
- [ ] `pytest tests/test_shops.py` 通过
- [ ] `make check` 通过

---

## 测试要求

- 创建店铺
- 列表查询
- 详情查询
- 更新配置
- 暂停/恢复
- 删除
- 跨租户访问被拒绝

---

## 约束

- 所有接口必须要求登录
- 必须校验 tenant_id
- Cookie 字段必须 AES 加密后存储

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
source .venv/bin/activate
export SECRET_KEY=test-secret
export DATABASE_URL=postgresql+asyncpg://ecom:password@localhost:6210/ecomagentos
export REDIS_URL=redis://localhost:6211/0

alembic upgrade head
pytest tests/test_shops.py -v
make check
```

---

## 回执格式

1. 修改的文件列表
2. 各接口测试结果
3. `pytest` 输出
4. 是否通过全部验收标准
