# CODE-008: 多租户中间件 + AES 加密

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-008 |
| **阶段** | Phase 1 |
| **负责 Agent** | `backend-core` |
| **验收 Agent** | `acceptance` |
| **依赖** | CODE-006, CODE-007 |
| **被依赖** | CODE-009, CODE-013, CODE-017 |
| **原文档章节** | 原设计 18.2 租户模块；AD-008 |
| **优先级** | P0 |

---

## 目标

实现多租户数据隔离、tenant_id 自动注入、PostgreSQL RLS、AES 加密敏感数据。

---

## 交付文件

```
backend/app/
├── core/
│   ├── security.py          # 扩展：AES 加密工具
│   └── tenant.py            # 当前租户上下文
├── middleware/
│   └── tenant.py            # 多租户中间件
├── db/
│   ├── base.py              # 扩展：TenantMixin
│   ├── rls.py               # RLS 工具函数
│   └── session.py           # 扩展：set search_path / RLS
├── api/v1/
│   └── tenants.py           # 租户管理接口（管理员）
├── schemas/
│   └── tenant.py            # Tenant Schema
├── services/
│   └── tenant_service.py    # 租户业务逻辑
└── tests/
    ├── test_tenant.py       # 多租户测试
    └── test_crypto.py       # AES 加密测试
```

---

## 多租户中间件

### 行为

1. 从 JWT token 中提取 `tenant_id`
2. 将 `tenant_id` 存入 `contextvars` 或依赖注入上下文
3. 所有数据库查询自动过滤 `tenant_id`
4. 未携带 token 的公开接口（如 /health）跳过

### 隔离策略

**应用层隔离（必须）：**
- 所有业务 Service 查询必须带 `tenant_id=...`
- `TenantMixin` 基类提供 `tenant_id` 字段

**数据库层 RLS（预留）：**
- 为每张业务表创建 RLS policy
- policy：`USING (tenant_id = current_setting('app.current_tenant')::UUID)`
- 通过 `SET LOCAL app.current_tenant = '...'` 启用
- 本次实现但**默认关闭 enforcement**，避免影响开发

---

## AES 加密

### 用途

- 加密店铺 Cookie（`shops.cookies_encrypted`）
- 加密平台 access_token/refresh_token
- 加密其他敏感配置

### 实现

```python
class AESCipher:
    def encrypt(self, plaintext: str) -> str: ...
    def decrypt(self, ciphertext: str) -> str: ...
```

- 使用 `cryptography.fernet` 或 AES-GCM
- 密钥从 `settings.secret_key` 派生
- 输出 base64 编码字符串

---

## 租户管理接口

### GET /api/v1/tenants/me

返回当前用户所属租户信息。

### PUT /api/v1/tenants/me

更新当前租户配置（名称、logo、配置等）。

### GET /api/v1/tenants/configs

返回租户套餐限制（先 mock）。

---

## 验收标准

- [ ] 多租户中间件从 JWT 正确提取 tenant_id
- [ ] 业务模型查询自动按 tenant_id 过滤
- [ ] 用户 A 无法访问用户 B 的租户数据
- [ ] RLS policy 已创建（默认 enforcement=off）
- [ ] AES 加密/解密可逆
- [ ] 相同明文加密后不应完全相同（使用 IV/nonce）
- [ ] `pytest tests/test_tenant.py` 通过
- [ ] `pytest tests/test_crypto.py` 通过
- [ ] `make check` 通过

---

## 测试要求

- 创建两个租户和两个用户
- 用户 A 访问自己的数据成功
- 用户 A 访问用户 B 的数据返回 403/404
- AES 加密解密测试
- RLS policy 存在性检查

---

## 约束

- 不要泄露其他租户的 tenant_id
- AES 密钥不可硬编码
- RLS enforcement 默认关闭，通过配置 `ENABLE_RLS=true` 开启

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
source .venv/bin/activate
export SECRET_KEY=test-secret
export DATABASE_URL=postgresql+asyncpg://ecom:password@localhost:6210/ecomagentos
export REDIS_URL=redis://localhost:6211/0

alembic upgrade head
pytest tests/test_tenant.py tests/test_crypto.py -v
make check
```

---

## 回执格式

1. 修改的文件列表
2. 多租户隔离测试结果
3. AES 加解密示例
4. `pytest` 输出
5. 是否通过全部验收标准
