# CODE-007: 认证模块（注册/登录/JWT/刷新）

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-007 |
| **阶段** | Phase 1 |
| **负责 Agent** | `backend-core` |
| **验收 Agent** | `acceptance` |
| **依赖** | CODE-005, CODE-006 |
| **被依赖** | CODE-008, CODE-009, CODE-013, CODE-017 |
| **原文档章节** | 原设计 20.3 认证模块 |
| **优先级** | P0 |

---

## 目标

实现用户认证系统：注册、登录、修改密码、刷新 Token。

**必须遵守 Phase 1 通用规范：** `docs/PMO/phase1_common_spec.md`

---

## 交付文件

```
backend/app/
├── api/v1/
│   └── auth.py              # /auth/* 路由
├── schemas/
│   └── auth.py              # 请求/响应 Schema
├── services/
│   └── auth_service.py      # 认证业务逻辑
├── core/
│   └── security.py          # JWT、密码哈希工具
└── tests/
    └── test_auth.py         # 认证接口测试
```

---

## API 接口

### POST /api/v1/auth/register

**请求：**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "tenant_name": "我的公司"
}
```

**响应：**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

行为：
- 如果 `tenant_name` 提供，创建新租户并把用户设为该租户管理员
- 如果不提供 `tenant_name`，要求 `tenant_id` 已存在（邀请注册场景，可选）
- 密码使用 bcrypt 哈希
- 邮箱唯一
- 邮箱重复返回 409，body 格式见通用规范：
  ```json
  {"code": "EMAIL_ALREADY_EXISTS", "message": "该邮箱已被注册", "details": {"field": "email"}}
  ```

### POST /api/v1/auth/login

**请求：**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**响应：** 同 register

### POST /api/v1/auth/refresh

**请求：**
```json
{
  "refresh_token": "..."
}
```

**响应：**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

- refresh_token 存储在 Redis，支持轮换（rotation）
- access_token 过期时间：15 分钟
- refresh_token 过期时间：7 天
- 调用 `/auth/refresh` 时：
  1. 校验旧 refresh_token 有效且不在黑名单
  2. 生成新的 access_token + refresh_token
  3. 将旧 refresh_token 加入黑名单
  4. 返回新的双 token
- 调用 `/auth/logout` 时：将当前 refresh_token 加入 Redis 黑名单，TTL 7 天

### POST /api/v1/auth/change-password

**请求：**
```json
{
  "old_password": "...",
  "new_password": "..."
}
```

**响应：**
- 成功：`{"message": "password changed"}`
- 旧密码错误：返回 400，body：
  ```json
  {"code": "INVALID_OLD_PASSWORD", "message": "旧密码不正确", "details": {"field": "old_password"}}
  ```

- 需要登录（access_token）

### POST /api/v1/auth/logout

**请求：** Header `Authorization: Bearer <access_token>`

**响应：** `{"message": "logged out"}`

- 将 refresh_token 加入 Redis 黑名单

---

## JWT 要求

- 算法：`HS256`
- Secret：`settings.secret_key`
- Payload 包含：`sub` (user_id), `tenant_id`, `email`, `exp`, `iat`
- Redis 中存储 refresh_token：`refresh:<token_hash>` → user_id，TTL 7 天

---

## 密码要求

- 最小 8 位
- 至少 1 个大写字母
- 至少 1 个小写字母
- 至少 1 个数字
- 使用 `passlib[bcrypt]`

---

## 验收标准

- [ ] `/auth/register` 可创建用户和租户
- [ ] 注册时重复邮箱返回 409
- [ ] `/auth/login` 正确返回双 token
- [ ] 密码错误返回 401，body：
  ```json
  {"code": "INVALID_PASSWORD", "message": "邮箱或密码错误"}
  ```
- [ ] `/auth/refresh` 能用 refresh_token 换取新 token
- [ ] refresh_token 过期或被吊销后无法刷新，body：
  ```json
  {"code": "REFRESH_TOKEN_INVALID", "message": "refresh token 已失效或过期"}
  ```
- [ ] `/auth/change-password` 需要旧密码正确
- [ ] `/auth/logout` 使 refresh_token 失效
- [ ] access_token 可解析出 tenant_id
- [ ] `pytest tests/test_auth.py` 通过
- [ ] `make check` 通过

---

## 数据库依赖

需要 CODE-006 创建的表：
- `tenants`
- `users`

---

## 测试要求

至少覆盖：
- 注册成功
- 邮箱重复（验证 409 body 格式）
- 登录成功
- 登录密码错误（验证 401 body 格式）
- 刷新 token（验证旧 refresh_token 失效）
- 使用失效 refresh_token 刷新失败
- 修改密码成功
- 修改密码时旧密码错误（验证 400 body 格式）
- 注销后 refresh_token 无法使用
- access_token payload 包含 tenant_id

---

## 约束

- 不要硬编码密钥
- 不要返回密码哈希
- Redis 操作使用 `redis.asyncio`：
  ```python
  import redis.asyncio as redis
  redis_client = redis.from_url(settings.redis_url, decode_responses=True)
  ```
- 所有路由函数必须是 async

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
source .venv/bin/activate
export SECRET_KEY=test-secret
export DATABASE_URL=postgresql+asyncpg://ecom:password@localhost:6210/ecomagentos
export REDIS_URL=redis://localhost:6211/0

alembic upgrade head
pytest tests/test_auth.py -v
make check
```

---

## 回执格式

1. 修改的文件列表
2. 各接口测试输出
3. `pytest` 输出
4. 是否通过全部验收标准
