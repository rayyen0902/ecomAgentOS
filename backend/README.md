# ecomAgentOS Backend

FastAPI backend core for ecomAgentOS.

## Requirements

- Python 3.12+

## Local development

```bash
cd /Users/caopinggege/Desktop/ecomAgentOS/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## LLM configuration

Set the active provider via `LLM_PROVIDER` and its API key:

```bash
# Agnes (default)
export LLM_PROVIDER=agnes
export AGNES_API_KEY=sk-xxx

# OpenAI
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-xxx

# DeepSeek
export LLM_PROVIDER=deepseek
export DEEPSEEK_API_KEY=sk-xxx

# Mock provider for tests / offline development
export LLM_PROVIDER=mock
```

Optional environment variables:

- `AGNES_BASE_URL` (default: `https://api.agnes.ai/v1`)
- `AGNES_DEFAULT_MODEL` (default: `agnes-large-latest`)
- `OPENAI_BASE_URL` (default: `https://api.openai.com/v1`)
- `OPENAI_DEFAULT_MODEL` (default: `gpt-4o`)
- `DEEPSEEK_BASE_URL` (default: `https://api.deepseek.com/v1`)
- `DEEPSEEK_DEFAULT_MODEL` (default: `deepseek-chat`)

## Run the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 6200 --reload
```

## Run tests

```bash
pytest tests/test_health.py
```

## API documentation

- Swagger UI: <http://localhost:6200/docs>
- ReDoc: <http://localhost:6200/redoc>

## Health check

```bash
curl -s http://localhost:6200/api/v1/health | python -m json.tool
```
