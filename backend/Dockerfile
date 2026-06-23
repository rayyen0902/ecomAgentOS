FROM python:3.12.4-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for Python packages (e.g. psycopg2).
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running the application.
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy project metadata and source code.
COPY --chown=appuser:appgroup pyproject.toml README.md ./
COPY --chown=appuser:appgroup app ./app

# Install the backend package.
RUN pip install --no-cache-dir .

USER appuser

EXPOSE 6200

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6200", "--reload"]
