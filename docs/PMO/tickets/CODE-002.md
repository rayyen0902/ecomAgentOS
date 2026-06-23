# CODE-002: Docker Compose + 服务编排

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-002 |
| **阶段** | Phase 0 |
| **负责 Agent** | `devops-qa` |
| **协作 Agent** | `backend-core` |
| **依赖** | CODE-001 |
| **被依赖** | CODE-006 |
| **原文档章节** | `PORT_CONFIG.md`, `重写开发计划.md` Phase 0 |
| **优先级** | P0 |

---

## 目标

创建项目级 Docker Compose 编排，包含：
- `api`：FastAPI 后端服务
- `db`：PostgreSQL 16
- `redis`：Redis 7
- `flower`：Celery 监控（先占位，CODE-024 扩展）

所有服务端口限制在 **6200-6300**。

---

## 交付文件

```
.
├── docker-compose.yml
├── backend/Dockerfile
├── backend/.dockerignore
└── .env.example           # 不提交真实密钥
```

---

## 端口与服务映射

| 服务 | 容器内端口 | 宿主机端口 | 说明 |
|------|-----------|-----------|------|
| api | 6200 | 6200 | FastAPI 服务 |
| db | 5432 | 6210 | PostgreSQL 16 |
| redis | 6379 | 6211 | Redis 7 |
| flower | 5555 | 6212 | Celery 监控 |

---

## 环境变量要求

`.env.example` 需包含：

```bash
# 应用
APP_ENV=development
APP_NAME=ecomAgentOS
APP_VERSION=0.1.0
API_HOST=0.0.0.0
API_PORT=6200
SECRET_KEY=change-me-in-production

# 数据库
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=ecom
POSTGRES_PASSWORD=change-me
POSTGRES_DB=ecomagentos
DATABASE_URL=postgresql+asyncpg://ecom:change-me@db:5432/ecomagentos

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# LLM（可选，占位）
LLM_PROVIDER=agnes
AGNES_API_KEY=your-key-here
```

---

## 验收标准

### 1. Dockerfile
- [ ] 基于 `python:3.12.4-slim`
- [ ] 安装系统依赖（gcc、libpq-dev 等）
- [ ] 使用非 root 用户运行
- [ ] 暴露端口 6200
- [ ] 启动命令：`uvicorn app.main:app --host 0.0.0.0 --port 6200 --reload`

### 2. docker-compose.yml
- [ ] 定义 `api`、`db`、`redis`、`flower` 四个服务
- [ ] 使用 `.env` 文件加载环境变量
- [ ] `api` 依赖 `db` 和 `redis` 健康检查
- [ ] `db` 使用 named volume `postgres_data`
- [ ] `redis` 使用 named volume `redis_data`
- [ ] 端口严格限制在 6200-6300

### 3. 可运行
- [ ] `docker compose up -d` 能启动所有服务
- [ ] `docker compose ps` 显示所有服务 healthy/up
- [ ] `curl http://localhost:6200/api/v1/health` 返回 `{"status":"ok",...}`
- [ ] `docker compose logs api` 无报错

### 4. 清理
- [ ] `docker compose down -v` 能清理数据

---

## 约束

- 不要提交真实 `.env` 文件
- 所有密码/密钥必须从环境变量读取
- `flower` 服务可以先使用占位镜像或简单配置，后续工单扩展
- 保持 `backend/Dockerfile` 与本地开发一致

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS
cp .env.example .env
# 编辑 .env 填入本地可用密码
docker compose up -d --build
sleep 10
docker compose ps
curl -s http://localhost:6200/api/v1/health | python -m json.tool
docker compose logs api --tail 20
```

---

## 回执格式

1. 修改的文件列表
2. `docker compose ps` 输出
3. `/health` 返回示例
4. 是否通过全部验收标准
