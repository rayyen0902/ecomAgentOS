# CODE-001: FastAPI 0.138+ 项目骨架

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-001 |
| **阶段** | Phase 0 |
| **负责 Agent** | `backend-core` |
| **协作 Agent** | `devops-qa` |
| **依赖** | 无 |
| **被依赖** | CODE-002, CODE-003, CODE-004, CODE-005, CODE-006 |
| **原文档章节** | 重写开发计划 Phase 0 |
| **优先级** | P0 |

---

## 目标

搭建 FastAPI 0.138+ 后端项目骨架，建立清晰的目录结构，实现一个可运行的 `/health` 健康检查接口。

---

## 交付目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── health.py    # /health 路由
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # 基础配置（先占位，CODE-005 扩展）
│   └── schemas/
│       ├── __init__.py
│       └── health.py        # HealthCheckResponse
├── tests/
│   ├── __init__.py
│   └── test_health.py       # /health 测试
├── pyproject.toml           # 项目元数据、工具配置
└── README.md                # 本地启动说明
```

> 注意：`backend/` 当前为空目录，需要从零创建。旧代码已归档到 `archive/`，不要复制旧代码。

---

## 技术要求

- Python 3.12.4
- FastAPI >= 0.138.0, < 0.140.0
- Uvicorn >= 0.30.0
- Pydantic >= 2.7.0
- HTTPX（用于测试）

---

## 验收标准

### 1. 目录与文件
- [ ] `backend/app/main.py` 存在，能创建 FastAPI app
- [ ] `backend/app/api/v1/health.py` 存在
- [ ] `backend/app/schemas/health.py` 存在
- [ ] `backend/tests/test_health.py` 存在

### 2. /health 接口
- [ ] `GET /api/v1/health` 返回 JSON：
  ```json
  {
    "status": "ok",
    "version": "0.1.0",
    "timestamp": "2026-06-24T00:00:00Z"
  }
  ```
- [ ] HTTP 状态码 200
- [ ] `timestamp` 为 ISO 8601 UTC 格式

### 3. 可运行
- [ ] 在 `backend/` 目录下执行 `uvicorn app.main:app --host 0.0.0.0 --port 6200` 能启动
- [ ] 浏览器访问 `http://localhost:6200/api/v1/health` 返回上述 JSON
- [ ] 访问 `http://localhost:6200/docs` 能打开 Swagger UI

### 4. 测试
- [ ] `pytest tests/test_health.py` 通过

---

## 约束

- 不要引入数据库、Redis、Celery 等依赖（后续工单处理）
- 不要硬编码密钥
- 不要使用旧代码 `archive/` 中的任何文件
- 代码需通过 `ruff check .` 和 `ruff format --check .`

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn pydantic httpx pytest ruff
uvicorn app.main:app --host 0.0.0.0 --port 6200 &
sleep 3
curl -s http://localhost:6200/api/v1/health | python -m json.tool
pytest tests/test_health.py
```

---

## 回执格式

执行完成后请返回：
1. 修改的文件列表
2. `/health` 接口的实际返回示例
3. `pytest` 输出结果
4. 是否通过全部验收标准
