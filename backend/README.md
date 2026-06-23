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
