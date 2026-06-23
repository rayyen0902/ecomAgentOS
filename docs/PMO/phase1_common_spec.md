# Phase 1 通用规范

> **文档定位：** Phase 1 所有工单必须遵守的通用约定  
> **适用范围：** CODE-007 ~ CODE-017  
> **文档版本：** v1.0

---

## 一、统一错误响应格式

所有 API 错误返回统一结构：

```json
{
  "code": "ERROR_CODE",
  "message": "Human readable message",
  "details": {}
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | string | 机器可读错误码，大写下划线分隔 |
| `message` | string | 人类可读错误信息 |
| `details` | object | 可选，额外上下文（如字段名、约束值） |

### 常见错误码

| HTTP 状态 | 错误码 | 含义 |
|-----------|--------|------|
| 400 | `BAD_REQUEST` | 请求参数错误 |
| 401 | `UNAUTHORIZED` | 未认证或 token 无效 |
| 403 | `FORBIDDEN` | 无权访问（跨租户等） |
| 404 | `NOT_FOUND` | 资源不存在 |
| 409 | `CONFLICT` | 资源冲突（邮箱重复等） |
| 422 | `VALIDATION_ERROR` | Pydantic 校验失败 |
| 500 | `INTERNAL_ERROR` | 服务器内部错误 |

### 示例

邮箱重复：
```json
{
  "code": "EMAIL_ALREADY_EXISTS",
  "message": "该邮箱已被注册",
  "details": {"field": "email"}
}
```

旧密码错误：
```json
{
  "code": "INVALID_OLD_PASSWORD",
  "message": "旧密码不正确",
  "details": {"field": "old_password"}
}
```

---

## 二、分页规范

### 请求参数

| 参数 | 类型 | 默认值 | 约束 |
|------|------|--------|------|
| `page` | int | 1 | >= 1 |
| `page_size` | int | 20 | 1 ~ 100 |

### 响应结构

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 约束

- `page_size > 100` 时返回 400：`PAGE_SIZE_TOO_LARGE`
- `page < 1` 时返回 400：`INVALID_PAGE`

---

## 三、金额与价格字段

所有金额、价格、库存相关数值字段必须遵守：

### 数据库层

使用 PostgreSQL `Numeric(12, 2)`：

```python
from sqlalchemy import Numeric

amount = Column(Numeric(12, 2), nullable=False)
```

### Python 层

使用 Python `Decimal`：

```python
from decimal import Decimal
from pydantic import Field

price: Decimal = Field(..., ge=0, decimal_places=2, max_digits=12)
```

### 禁止

- 禁止使用 `float` 表示金额
- 禁止使用 `DOUBLE PRECISION` 存金额

---

## 四、平台枚举

`platform` 字段当前枚举值：

```python
class Platform(str, Enum):
    PDD = "pdd"
    TAOBAO = "taobao"
    DOUYIN = "douyin"
    JD = "jd"
```

### 扩展规则

- 新增平台时，先修改 `Platform` 枚举
- 再添加对应的 `platform_adapters` 表记录
- 不要硬编码平台判断逻辑（应通过 adapter 表路由）

---

## 五、状态机规范

### 通用规则

- 状态字段使用 `Enum` 定义
- 状态转换必须通过 Service 方法，不要直接在 API 层修改
- 非法状态转换返回 400：`INVALID_STATUS_TRANSITION`

### 软删除

- 使用 `deleted_at` 字段（DateTime, nullable）
- 列表查询默认过滤 `deleted_at IS NULL`
- 删除接口设置 `deleted_at = now()`，不物理删除

---

## 六、JSONB 字段

- `config`、`spec`、`buyer_info` 等字段使用 PostgreSQL `JSONB`
- Python 层使用 `dict` 类型
- 不要嵌套过深（建议不超过 3 层）

---

## 七、租户隔离

- 所有业务表必须包含 `tenant_id: UUID`
- 所有业务查询必须过滤 `tenant_id`
- 跨租户访问返回 403：`TENANT_ACCESS_DENIED`

---

## 八、变更记录

| 时间 | 变更人 | 变更内容 |
|------|--------|---------|
| 2026-06-24 | OpenCode | 创建 v1.0 |
