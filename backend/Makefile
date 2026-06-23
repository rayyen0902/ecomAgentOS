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
