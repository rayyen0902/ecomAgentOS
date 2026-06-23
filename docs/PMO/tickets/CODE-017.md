# CODE-017: 订单 / 售后基础接口

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-017 |
| **阶段** | Phase 1 |
| **负责 Agent** | `backend-core` |
| **验收 Agent** | `acceptance` |
| **依赖** | CODE-006, CODE-007, CODE-008, CODE-009 |
| **被依赖** | CODE-018, CODE-019 |
| **原文档章节** | 原设计 4.3 订单管理 |
| **优先级** | P1 |

---

## 目标

实现订单、售后单的基础数据接口，支持后续订单同步、售后处理 Agent。

---

## 交付文件

```
backend/app/
├── api/v1/
│   ├── orders.py            # /orders/* 路由
│   └── refunds.py           # /refunds/* 路由
├── schemas/
│   ├── order.py             # Order Schema
│   └── refund.py            # RefundOrder Schema
├── services/
│   ├── order_service.py     # 订单业务逻辑
│   └── refund_service.py    # 售后业务逻辑
└── tests/
    └── test_orders.py       # 订单/售后接口测试
```

---

## API 接口

### POST /api/v1/shops/{shop_id}/orders

手动创建订单（主要用于测试，实际订单来自平台同步）。

**请求：**
```json
{
  "platform_order_id": "ORDER123456",
  "amount": 199.00,
  "status": "pending",
  "buyer_info": {"nickname": "买家A"},
  "items": [
    {"product_id": "uuid", "sku_id": "uuid", "quantity": 1, "price": 99.00}
  ]
}
```

### GET /api/v1/shops/{shop_id}/orders

查询店铺订单列表，支持分页、状态过滤、时间范围。

**响应：**
```json
{
  "items": [
    {
      "id": "uuid",
      "platform_order_id": "ORDER123456",
      "amount": 199.00,
      "status": "pending",
      "created_at": "..."
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### GET /api/v1/orders/{order_id}

订单详情。

### POST /api/v1/orders/{order_id}/refunds

创建售后单。

**请求：**
```json
{
  "refund_type": "refund_only",
  "amount": 99.00,
  "reason": "商品质量问题",
  "status": "pending"
}
```

`refund_type`: `refund_only`（仅退款） / `return_refund`（退货退款）

### GET /api/v1/shops/{shop_id}/refunds

售后单列表。

### GET /api/v1/refunds/{refund_id}

售后单详情。

---

## 字段要求

### orders
- `tenant_id`, `shop_id`
- `platform_order_id`
- `amount`, `status`
- `buyer_info`（JSONB）
- `created_at`, `updated_at`

### refund_orders
- `tenant_id`, `order_id`
- `refund_type`, `amount`, `reason`, `status`
- `created_at`, `updated_at`

---

## 验收标准

- [ ] 创建订单成功
- [ ] 订单列表分页查询正常
- [ ] 订单详情可查询
- [ ] 创建售后单成功
- [ ] 售后单列表和详情可查询
- [ ] 只能访问当前租户订单
- [ ] `pytest tests/test_orders.py` 通过
- [ ] `make check` 通过

---

## 测试要求

- 创建订单
- 订单列表分页和过滤
- 订单详情
- 创建售后单
- 售后单列表/详情
- 跨租户访问被拒绝

---

## 约束

- 所有接口必须要求登录
- 必须校验 tenant_id
- 订单金额必须为正数
- 售后金额不能超过订单金额

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
source .venv/bin/activate
export SECRET_KEY=test-secret
export DATABASE_URL=postgresql+asyncpg://ecom:password@localhost:6210/ecomagentos
export REDIS_URL=redis://localhost:6211/0

alembic upgrade head
pytest tests/test_orders.py -v
make check
```

---

## 回执格式

1. 修改的文件列表
2. 各接口测试结果
3. `pytest` 输出
4. 是否通过全部验收标准
