.PHONY: help install dev lint format test run-api run-dashboard run-local clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install with dev dependencies
	pip install -e ".[dev]"
	pre-commit install

lint: ## Run linter
	ruff check . --fix

format: ## Format code
	ruff format .
	black .

test: ## Run tests
	pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=html

run-api: ## Run FastAPI server locally
	uvicorn src.api.routes:app --reload --host 0.0.0.0 --port 8000

run-dashboard: ## Run Streamlit dashboard
	streamlit run dashboard/app.py --server.port 8501

run-local: ## Run all services locally
	python scripts/run_local.py

init-db: ## Initialize database indexes
	python scripts/init_db.py

seed-watchlist: ## Seed default watchlist
	python scripts/seed_watchlist.py

clean: ## Clean temporary files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage