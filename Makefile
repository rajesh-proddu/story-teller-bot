.PHONY: help docker-build docker-run docker-compose-up docker-compose-down docker-compose-logs test test-fast lint clean

help: ## Show this help message
	@echo 'Story Teller Bot - Makefile targets'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'

## Docker Development Targets

docker-build: ## Build Docker image with models pre-cached
	docker build -t story-teller-bot:latest -f deployment/Dockerfile .

docker-build-test: ## Build test Docker image
	docker build -t story-teller-bot:test -f deployment/Dockerfile.test .

docker-run: ## Run bot in interactive Docker container
	docker run -it \
		-v $(PWD)/audio_output:/app/audio_output \
		--device /dev/snd:/dev/snd \
		story-teller-bot:latest

docker-compose-up: ## Start bot with Docker Compose
	docker-compose -f deployment/docker-compose.yml up -d

docker-compose-down: ## Stop bot with Docker Compose
	docker-compose -f deployment/docker-compose.yml down

docker-compose-logs: ## View bot logs
	docker-compose -f deployment/docker-compose.yml logs -f story-teller-bot

docker-compose-logs-test: ## View test logs
	docker-compose -f deployment/docker-compose.yml logs -f

## Testing Targets

test: ## Run tests in Docker container
	./scripts/test_in_container.sh

test-fast: ## Run tests without coverage (faster)
	docker-compose -f deployment/docker-compose.extended.yml run tests \
		pytest tests/ -v --tb=short

test-interactive: ## Run tests in interactive shell
	docker-compose -f deployment/docker-compose.extended.yml run tests bash

## Quality & Linting

lint: ## Run linting in Docker container
	docker run --rm -v $(PWD):/app story-teller-bot:test \
		bash -c "flake8 src tests && mypy src --ignore-missing-imports"

lint-only: ## Run flake8 only
	docker run --rm -v $(PWD):/app story-teller-bot:test flake8 src tests

type-check: ## Run type checking only
	docker run --rm -v $(PWD):/app story-teller-bot:test \
		mypy src --ignore-missing-imports

shell: ## Get interactive shell in running container
	docker-compose -f deployment/docker-compose.yml exec story-teller-bot bash

## Maintenance

clean: ## Clean up local generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf test_results/
	@echo "✓ Cleanup completed"

clean-docker: ## Remove Docker images and containers
	docker-compose -f deployment/docker-compose.yml down --rmi all
	docker system prune -f

.DEFAULT_GOAL := help
