# CODE-003 验收报告

## 元信息

| 字段 | 值 |
|------|---|
| **工单编号** | CODE-003 |
| **工单名称** | Python 依赖与工具链 |
| **验收 Agent** | acceptance Agent |
| **验收日期** | 2026-06-24 |
| **负责 Agent** | devops-qa |

---

## 验收结果

### 1. 文件存在

| 文件 | 结果 | 证据 |
|------|------|------|
| `backend/requirements.txt` | 通过 | 499 bytes, 25 包，与工单规格完全一致 |
| `backend/requirements-dev.txt` | 通过 | 165 bytes, 含 `-r requirements.txt`，9 个包，与工单规格一致 |
| `backend/pyproject.toml` | 通过 | 887 bytes, 已扩展 |
| `backend/.pre-commit-config.yaml` | 通过 | 1022 bytes |
| `backend/Makefile` | 通过 | 350 bytes |

### 2. 内容合规性

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `requirements.txt` 25 包完整 | 通过 | fastapi, uvicorn, pydantic, sqlalchemy, alembic, asyncpg, redis, celery, flower, httpx, python-jose, passlib, cryptography, python-multipart, openai, langgraph, langchain, pydantic-ai, openai-whisper, playwright, pillow, python-dotenv, structlog, tenacity, pydantic-settings |
| `openai` 版本 `<2.0.0` | 通过 | `openai>=1.30.0,<2.0.0` |
| `openai-whisper` 正确名称 | 通过 | `openai-whisper>=20231117`（非 `whisper`）|
| 所有依赖指定最低版本 | 通过 | 均使用 `>=` 约束 |
| `requirements-dev.txt` 引用 `requirements.txt` | 通过 | 首行 `-r requirements.txt` |

### 3. pyproject.toml 工具链配置

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `[tool.ruff]` target-version | 通过 | `target-version = "py312"` |
| `[tool.ruff]` line-length | 通过 | `line-length = 100`（与工单一致）|
| `[tool.ruff.lint]` select 规则 | 通过 | `["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]` |
| `[tool.ruff.lint.pydocstyle]` convention | 通过 | `convention = "google"` |
| `[tool.mypy]` 完整配置 | 通过 | python_version/warn_return_any/warn_unused_configs/disallow_untyped_defs 均已设置 |
| `[tool.pytest.ini_options]` testpaths | 通过 | `testpaths = ["tests"]` |
| `[tool.pytest.ini_options]` asyncio_mode | 通过 | `asyncio_mode = "auto"`（line 20），pytest 输出 `mode=Mode.AUTO`（修复于 2026-06-24 复测）|

### 4. .pre-commit-config.yaml

| 检查项 | 结果 | 证据 |
|--------|------|------|
| ruff check 钩子 | 通过 | `astral-sh/ruff-pre-commit` v0.4.8 |
| ruff-format 钩子 | 通过 | 同上，`ruff-format` hook |
| 禁止大文件 | 通过 | `check-added-large-files --maxkb=500` |
| 检测密钥 | 通过 | `detect-private-key` |
| 禁止提交 .env | 通过 | local hook `check-env-files`（`\.env$` 匹配） |

### 5. Makefile

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `.PHONY` 声明 | 通过 | 包含 install/dev/install-dev/test/lint/format/check/docker-up/docker-down |
| `install` 命令 | 通过 | `pip install -r requirements.txt` |
| `dev` 命令 | 通过 | `pip install -r requirements-dev.txt` |
| `test` 命令 | 通过 | `pytest` |
| `lint` 命令 | 通过 | `ruff check .` |
| `format` 命令 | 通过 | `ruff format .` |
| `check` 命令 | 通过 | `ruff check . && ruff format --check .` |
| `docker-up` / `docker-down` | 通过 | `docker compose up -d --build` / `docker compose down -v` |

### 6. 运行时验证

| 检查项 | 结果 | 证据 |
|--------|------|------|
| `make check` | 通过 | `All checks passed!` + `11 files already formatted` |
| `make test` | 通过 | `1 passed, 1 warning`（health 测试） |
| `pre-commit run --all-files` | 通过 | 9/9 Passed（ruff, ruff-format, large files, merge conflict, yaml, eof, whitespace, private key, .env check）|

---

## 总体结论

- **[x] 通过**

6 项验收标准（存在/可安装/配置/pre-commit/Makefile/make check/make test）全部通过，工具链完整可用。

初次验收发现 1 个缺陷（`asyncio_mode = "auto"` 缺失），已于 2026-06-24 复测确认修复：`pyproject.toml:20` 已添加 `asyncio_mode = "auto"`，pytest 输出 `mode=Mode.AUTO`，`make test` / `make check` 均通过。

---

## 缺陷列表

无。（初次发现的缺陷已修复并复测通过）

---

## 签名

acceptance Agent
2026-06-24
