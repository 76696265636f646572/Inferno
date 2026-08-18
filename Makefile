.PHONY: help install backend frontend dev test lint migrate

UV ?= uv
PNPM ?= pnpm

help:
	@echo "Inferno development targets"
	@echo "  make install    Create backend venv and install frontend deps"
	@echo "  make backend    Run FastAPI with reload (http://localhost:8000)"
	@echo "  make frontend   Run Nuxt dev server (http://localhost:3000)"
	@echo "  make dev        Print how to run both locally"
	@echo "  make test       Run backend and frontend tests"
	@echo "  make lint       Ruff + ESLint"
	@echo "  make migrate    Alembic upgrade head"
	@echo "  make docker     docker compose up --build"

install:
	cd backend && $(UV) sync --extra dev
	cd frontend && $(PNPM) install

backend:
	cd backend && $(UV) run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && $(PNPM) dev

dev:
	@echo "Run these in two terminals:"
	@echo "  make backend"
	@echo "  make frontend"
	@echo "API:  http://localhost:8000/docs"
	@echo "UI:   http://localhost:3000"

test:
	cd backend && $(UV) run pytest -q
	cd frontend && $(PNPM) test

lint:
	cd backend && $(UV) run ruff check app tests
	cd frontend && $(PNPM) lint

migrate:
	cd backend && $(UV) run alembic upgrade head

docker:
	docker compose up --build
