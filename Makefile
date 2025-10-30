.PHONY: help install test lint format run docker-build docker-up docker-down migrate

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make run           - Run development server"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make migrate       - Run database migrations"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

lint:
	flake8 app tests --max-line-length=100 --extend-ignore=E203,W503
	mypy app

format:
	black app tests
	isort app tests

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(msg)"
