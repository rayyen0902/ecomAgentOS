# 端口与服务配置规范

> **文档版本：** v1.0
> **最后更新：** 2026-06-23
> **适用范围：** 开发环境、测试环境、生产环境（阿里云）

---

## 一、端口分配总表（6200 ~ 6300）

所有服务端口集中在 `6200 ~ 6300` 区间，便于防火墙管理和冲突排查。

| 端口 | 服务 | 说明 | 环境 |
|------|------|------|------|
| **6200** | FastAPI API | 主后端服务（HTTP + WebSocket） | 所有 |
| **6201** | Vite Dev (Desktop) | 桌面端前端开发服务器 | 仅开发 |
| **6202** | Vite Dev (PWA) | 移动端前端开发服务器 | 仅开发 |
| **6210** | PostgreSQL | 主数据库 | 所有 |
| **6211** | Redis | 缓存 + Celery消息队列 | 所有 |
| **6212** | Celery Flower | 任务队列监控面板（可选） | 开发/测试 |
| **6220** | ComfyUI | 本地AI图片生成（可选扩展） | 本地 |
| **6221** | CosyVoice2 | 本地TTS语音合成（可选扩展） | 本地 |
| **6222** | MuseTalk | 本地口播视频（可选扩展） | 本地 |
| **6230** | QEMU VNC | 虚拟机微信控制（可选扩展） | 本地 |

### 端口预留

| 端口段 | 用途 |
|--------|------|
| 6200 ~ 6209 | 核心服务（API + 前端开发） |
| 6210 ~ 6219 | 数据层（数据库 + 缓存 + 监控） |
| 6220 ~ 6249 | AI扩展服务（ComfyUI / CosyVoice / MuseTalk等） |
| 6250 ~ 6299 | 预留（未来微服务拆分） |
| 6300 | 保留（网关/负载均衡） |

---

## 二、环境配置

### 2.1 环境变量文件

项目使用 `.env` 文件管理配置，**`.env.example` 提交到仓库，`.env` 不提交**。

```bash
# .env
# =============================================================================
# 核心服务端口配置
# =============================================================================
API_PORT=6200
API_HOST=0.0.0.0

# =============================================================================
# 数据库配置
# =============================================================================
DATABASE_URL=postgresql+asyncpg://ecommerce:ecommerce_dev@localhost:6210/ecommerce_agent
DB_HOST=localhost
DB_PORT=6210
DB_NAME=ecommerce_agent
DB_USER=ecommerce
DB_PASSWORD=ecommerce_dev

# 同步数据库URL（Alembic迁移用）
SYNC_DATABASE_URL=postgresql://ecommerce:ecommerce_dev@localhost:6210/ecommerce_agent

# =============================================================================
# Redis配置
# =============================================================================
REDIS_URL=redis://localhost:6211/0
REDIS_HOST=localhost
REDIS_PORT=6211

# Celery专用Redis库（与缓存隔离）
CELERY_BROKER_URL=redis://localhost:6211/1
CELERY_RESULT_BACKEND=redis://localhost:6211/2

# =============================================================================
# LLM提供商配置（默认Agnes）
# =============================================================================
LLM_PROVIDER=agnes
LLM_API_KEY=your_agnes_api_key_here
LLM_BASE_URL=https://apihub.agnes-ai.com/v1
LLM_TEXT_MODEL=agnes-2.0-flash
LLM_IMAGE_MODEL=agnes-image-2.1-flash
LLM_VIDEO_MODEL=agnes-video-v2.0

# LLM Thinking模式（编码/Agent任务建议开启）
LLM_ENABLE_THINKING=true

# =============================================================================
# 图片/视频生成提供商（可与LLM不同）
# =============================================================================
IMAGE_PROVIDER=agnes
VIDEO_PROVIDER=agnes

# 本地ComfyUI（可选，当IMAGE_PROVIDER=comfyui时生效）
COMFYUI_URL=http://localhost:6220

# =============================================================================
# 安全与认证
# =============================================================================
SECRET_KEY=change_this_to_a_random_32_char_string_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440          # 24小时
REFRESH_TOKEN_EXPIRE_DAYS=7

# AES-256加密密钥（32字节hex，用于Cookie/买家信息加密）
AES_KEY=change_this_to_64_hex_chars_32_bytes_aes_key_in_production

# =============================================================================
# API限流
# =============================================================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_LOGIN=10/minute
RATE_LIMIT_WEBSOCKET=1000/minute

# =============================================================================
# 可选本地AI服务
# =============================================================================
COSYVOICE_URL=http://localhost:6221
MUSETALK_URL=http://localhost:6222

# =============================================================================
# 虚拟机微信（可选）
# =============================================================================
VM_VNC_HOST=127.0.0.1
VM_VNC_PORT=6230
VM_VNC_PASSWORD=

# =============================================================================
# 文件存储
# =============================================================================
STORAGE_TYPE=local                        # local / oss / s3
STORAGE_LOCAL_PATH=./storage

# 阿里云OSS（可选）
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET=your-bucket
OSS_ACCESS_KEY=your_key
OSS_SECRET_KEY=your_secret

# =============================================================================
# 告警通知
# =============================================================================
DEV_ALERT_WEBHOOK=                        # 钉钉/企微机器人webhook

# =============================================================================
# 环境标识
# =============================================================================
APP_ENV=development                       # development / staging / production
APP_DEBUG=true

# =============================================================================
# 日志
# =============================================================================
LOG_LEVEL=INFO
LOG_FORMAT=json                           # json / simple
```

---

## 三、不同环境的端口映射

### 3.1 开发环境（本地单机）

```
localhost:6200  → FastAPI
localhost:6201  → Desktop Vite Dev
localhost:6202  → PWA Vite Dev
localhost:6210  → PostgreSQL
localhost:6211  → Redis
localhost:6212  → Celery Flower (可选)
```

### 3.2 阿里云服务器（生产/测试）

```
云服务器公网IP:6200  → FastAPI（Nginx反向代理到443）
云服务器内网:6210    → PostgreSQL（不暴露公网）
云服务器内网:6211    → Redis（不暴露公网，或绑定127.0.0.1）
```

**安全要求：**
- PostgreSQL 和 Redis **不绑定公网IP**，仅内网/127.0.0.1访问
- FastAPI 通过 Nginx 反向代理，对外暴露 443（HTTPS）
- 阿里云安全组只开放 443 和 22（SSH）

### 3.3 混合部署（阿里云API + 本地RPA）

```
┌─────────────────┐         HTTPS/WSS          ┌─────────────────┐
│   阿里云服务器   │◄──────────────────────────►│   本地电脑      │
│                 │        api.yourdomain.com   │                 │
│  FastAPI :6200  │                            │  Tauri桌面端    │
│  PostgreSQL     │                            │  RPA浏览器集群   │
│  Redis          │                            │                 │
└─────────────────┘                            └─────────────────┘
       ▲                                              │
       │         WebSocket实时推送                     │
       └──────────────────────────────────────────────┘

本地RPA通过HTTPS连接阿里云API，WebSocket保持长连接接收推送
```

---

## 四、Docker Compose 端口映射

```yaml
# docker-compose.yml 端口映射示例
services:
  postgres:
    image: postgres:16-alpine
    ports:
      - "6210:5432"          # 主机:6210 → 容器:5432
    environment:
      POSTGRES_USER: ecommerce
      POSTGRES_PASSWORD: ecommerce_dev
      POSTGRES_DB: ecommerce_agent

  redis:
    image: redis:7-alpine
    ports:
      - "6211:6379"          # 主机:6211 → 容器:6379

  fastapi:
    build: ./backend
    ports:
      - "6200:6200"          # 主机:6200 → 容器:6200
    environment:
      - API_PORT=6200
      - DATABASE_URL=postgresql+asyncpg://ecommerce:ecommerce_dev@postgres:5432/ecommerce_agent
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  celery_worker:
    build: ./backend
    command: celery -A tasks.celery_app worker --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      - redis

  celery_beat:
    build: ./backend
    command: celery -A tasks.celery_app beat --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - redis

  # 可选：Flower任务监控
  flower:
    build: ./backend
    command: celery -A tasks.celery_app flower --port=5555
    ports:
      - "6212:5555"
    depends_on:
      - redis
```

---

## 五、防火墙/安全组配置

### 5.1 阿里云安全组（生产环境）

| 方向 | 协议 | 端口 | 授权对象 | 说明 |
|------|------|------|---------|------|
| 入 | TCP | 22 | 你的IP/段 | SSH管理 |
| 入 | TCP | 443 | 0.0.0.0/0 | HTTPS（Nginx→FastAPI） |
| 入 | TCP | 80 | 0.0.0.0/0 | HTTP（自动跳转HTTPS） |
| 入 | TCP | 6200 | 0.0.0.0/0 | FastAPI直接访问（开发用） |
| 入 | TCP | 6212 | 你的IP/段 | Flower监控面板 |
| 出 | 全部 | 全部 | 0.0.0.0/0 | 出站任意 |

**注意：** 生产环境应关闭 6200 直接访问，只保留 443。

### 5.2 本地防火墙（开发环境）

```bash
# macOS / Linux 开发环境无需特别配置
# Windows 开发环境确保防火墙不拦截 6200-6300
```

---

## 六、常用命令速查

```bash
# 检查端口占用
lsof -i :6200              # macOS/Linux
netstat -ano | findstr 6200 # Windows

# Docker查看端口映射
docker-compose ps

# 测试FastAPI是否运行
curl http://localhost:6200/health

# 测试PostgreSQL
psql -h localhost -p 6210 -U ecommerce -d ecommerce_agent

# 测试Redis
redis-cli -p 6211 ping

# 测试WebSocket
wscat -c ws://localhost:6200/ws/test-client-id
```

---

## 七、变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-06-23 | v1.0 | 初始版本，端口范围 6200-6300 |
