# CODE-003: Python 依赖与工具链

---

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-003 |
| **阶段** | Phase 0 |
| **负责 Agent** | `devops-qa` |
| **协作 Agent** | `backend-core` |
| **依赖** | CODE-001 |
| **被依赖** | CODE-004, CODE-005, CODE-006 |
| **原文档章节** | `重写开发计划.md` Phase 0 |
| **优先级** | P0 |

---

## 目标

建立 backend 的依赖管理体系和代码质量工具链。

---

## 交付文件

```
backend/
├── requirements.txt        # 生产依赖
├── requirements-dev.txt    # 开发依赖
├── pyproject.toml          # 工具配置（ruff, pytest, mypy）
├── .pre-commit-config.yaml # pre-commit 钩子
└── Makefile                # 常用命令快捷方式
```

---

## 依赖要求

### requirements.txt（生产依赖）

```txt
fastapi>=0.138.0,<0.140.0
uvicorn[standard]>=0.30.0
pydantic>=2.7.0
pydantic-settings>=2.3.0
sqlalchemy[asyncio]>=2.0.30
alembic>=1.13.0
asyncpg>=0.29.0
redis>=5.0.0
celery>=5.4.0
flower>=2.0.0
httpx>=0.27.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.0
cryptography>=42.0.0
python-multipart>=0.0.9
openai>=1.30.0,<2.0.0
langgraph>=0.2.0
langchain>=0.2.0
pydantic-ai>=0.0.12
openai-whisper>=20231117
playwright>=1.44.0
pillow>=10.3.0
python-dotenv>=1.0.0
structlog>=24.1.0
tenacity>=8.3.0
```

### requirements-dev.txt（开发依赖）

```txt
-r requirements.txt
pytest>=8.2.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0
httpx>=0.27.0
ruff>=0.4.0
mypy>=1.10.0
pre-commit>=3.7.0
factory-boy>=3.3.0
faker>=25.0.0
```

---

## 工具链配置

### pyproject.toml 必须包含

```toml
[tool.ruff]
target-version = "py312"
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
ignore = []

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### .pre-commit-config.yaml 必须包含

- ruff check
- ruff format --check
- 禁止提交 `.env` 文件
- 禁止提交大文件

### Makefile 必须包含

```makefile
.PHONY: install dev install-dev test lint format check docker-up docker-down

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

check:
	ruff check . && ruff format --check .

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v
```

---

## 验收标准

- [ ] `requirements.txt` 和 `requirements-dev.txt` 存在且可安装
- [ ] `pyproject.toml` 配置了 ruff、mypy、pytest
- [ ] `.pre-commit-config.yaml` 存在并包含 `.env` 提交拦截
- [ ] `Makefile` 存在且命令可用
- [ ] `make check` 通过（当前代码无错误）
- [ ] `make test` 通过（至少包含 CODE-001 的 health 测试）

---

## 约束

- `openai-whisper` 不能写成 `whisper`（PyPI 上 `whisper` 是别的包）
- `openai` 必须 `<2.0.0`
- 所有依赖必须指定最低版本，不固定死版本（便于更新）
- 不要包含未使用的依赖

---

## 验收命令

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
make check
make test
pre-commit install
pre-commit run --all-files
```

---

## 回执格式

1. 修改的文件列表
2. `make check` 输出
3. `make test` 输出
4. `pre-commit run --all-files` 输出
5. 是否通过全部验收标准
