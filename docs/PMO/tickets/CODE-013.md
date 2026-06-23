# CODE-013: 商品 / SKU / 价格历史接口

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-013 |
| **阶段** | Phase 1 |
| **负责 Agent** | `backend-core` |
| **验收 Agent** | `acceptance` |
| **依赖** | CODE-006, CODE-007, CODE-008, CODE-009 |
| **被依赖** | CODE-014, CODE-015, CODE-016, CODE-020 |
| **原文档章节** | 原设计 4.2 商品管理 |
| **优先级** | P1 |

---

## 目标

实现商品、SKU、价格历史的基础数据接口，为后续改价、价格监控、AI Agent 提供数据层。

**必须遵守 Phase 1 通用规范：** `docs/PMO/phase1_common_spec.md`

---

## 交付文件

```
backend/app/
├── api/v1/
│   ├── products.py          # /products/* 路由
│   └── skus.py              # /skus/* 路由
├── schemas/
│   ├── product.py           # Product / ProductSnapshot Schema
│   └── sku.py               # SKU / PriceHistory Schema
├── services/
│   ├── product_service.py   # 商品业务逻辑
│   └── sku_service.py       # SKU 业务逻辑
└── tests/
    └── test_products.py     # 商品/SKU 接口测试
```

---

## API 接口

### POST /api/v1/shops/{shop_id}/products

手动创建商品（主要用于测试，实际商品来自平台同步）。

**请求：**
```json
{
  "platform_product_id": "PDD123456",
  "title": "示例商品",
  "main_image_url": "https://...",
  "status": "active"
}
```

### GET /api/v1/shops/{shop_id}/products

查询店铺商品列表，支持分页、状态过滤、关键词搜索。

**响应：**
```json
{
  "items": [
    {
      "id": "uuid",
      "platform_product_id": "PDD123456",
      "title": "示例商品",
      "status": "active",
      "shop_id": "uuid",
      "created_at": "..."
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### GET /api/v1/products/{product_id}

商品详情，包含 SKU 列表。

### GET /api/v1/products/{product_id}/snapshots

商品快照历史。

### POST /api/v1/products/{product_id}/skus

为商品添加 SKU。

**请求：**
```json
{
  "sku_code": "SKU-001",
  "price": "99.00",
  "stock": 100,
  "spec": {"颜色": "红", "尺码": "M"}
}
```

> `price` 使用字符串表示 Decimal（见通用规范），数据库用 `Numeric(12,2)`。

### GET /api/v1/skus/{sku_id}

SKU 详情。

### GET /api/v1/skus/{sku_id}/price-history

SKU 价格历史。

**响应：**
```json
{
  "items": [
    {
      "id": "uuid",
      "old_price": "99.00",
      "new_price": "89.00",
      "source": "manual",
      "created_at": "..."
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

## 字段要求

### products
- `tenant_id`, `shop_id`
- `platform_product_id`（平台侧 ID）
- `title`（必填）
- `main_image_url`（可选）
- `status`：枚举 `active` | `inactive` | `deleted`
- `created_at`, `updated_at`
- 唯一约束：`(tenant_id, shop_id, platform_product_id)`

### product_snapshots
- `tenant_id`, `product_id`
- `snapshot_data`（JSONB，完整商品数据）
- `created_at`

### skus
- `tenant_id`, `product_id`
- `sku_code`, `price`, `stock`, `spec`
- `created_at`, `updated_at`
- `price` 类型：`Numeric(12,2)` / Python `Decimal`
- `spec` 类型：JSONB（必须）
- 唯一约束：`(tenant_id, product_id, sku_code)`

### price_history
- `tenant_id`, `sku_id`
- `old_price`, `new_price`, `source`
- `created_at`
- `old_price` / `new_price` 类型：`Numeric(12,2)` / Python `Decimal`

---

## 验收标准

- [ ] 创建商品成功
- [ ] 商品列表分页查询正常
- [ ] 商品详情包含 SKU 列表
- [ ] 创建 SKU 成功
- [ ] 修改 SKU 价格自动记录 price_history
- [ ] 价格历史可查询
- [ ] 只能访问当前租户商品
- [ ] `pytest tests/test_products.py` 通过
- [ ] `make check` 通过

---

## 测试要求

- 创建商品
- 商品列表分页
- 商品详情
- 创建 SKU
- 修改 SKU 价格并检查历史
- 跨租户访问被拒绝

---

## 约束

- 所有接口必须要求登录
- 必须校验 tenant_id
- 价格变动必须记录历史
- SKU 规格使用 JSONB
- 所有金额字段使用 `Numeric(12,2)` / `Decimal`，禁止 float

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
source .venv/bin/activate
export SECRET_KEY=test-secret
export DATABASE_URL=postgresql+asyncpg://ecom:password@localhost:6210/ecomagentos
export REDIS_URL=redis://localhost:6211/0

alembic upgrade head
pytest tests/test_products.py -v
make check
```

---

## 回执格式

1. 修改的文件列表
2. 各接口测试结果
3. `pytest` 输出
4. 是否通过全部验收标准
