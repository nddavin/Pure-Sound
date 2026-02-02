# Pure Sound - Docker Makefile
# Docker commands for building, running, and managing containers

.PHONY: build build-dev build-prod up up-dev up-prod down down-prod logs logs-dev logs-prod \
        clean clean-volumes rebuild rebuild-dev rebuild-prod test test-in-docker \
        push pull status shell shell-dev shell-prod help

# Docker Compose files
DOCKER_COMPOSE = docker-compose -f docker-compose.yml
DOCKER_COMPOSE_DEV = docker-compose -f docker-compose.yml -f docker-compose.dev.yml
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.yml -f docker-compose.prod.yml

# Image names
IMAGE_NAME = pure-sound
IMAGE_DEV = pure-sound-dev
IMAGE_PROD = pure-sound-prod

# Default target
help:
	@echo "Pure Sound Docker Management"
	@echo ""
	@echo "Development Commands:"
	@echo "  build-dev      - Build development Docker image"
	@echo "  up-dev         - Start development environment"
	@echo "  down-dev       - Stop development environment"
	@echo "  logs-dev       - View development logs"
	@echo "  shell-dev      - Open shell in development container"
	@echo "  rebuild-dev    - Rebuild and restart development"
	@echo ""
	@echo "Production Commands:"
	@echo "  build-prod     - Build production Docker image"
	@echo "  up-prod        - Start production environment"
	@echo "  down-prod      - Stop production environment"
	@echo "  logs-prod      - View production logs"
	@echo "  shell-prod     - Open shell in production container"
	@echo "  rebuild-prod   - Rebuild and restart production"
	@echo ""
	@echo "General Commands:"
	@echo "  build          - Build all Docker images"
	@echo "  up             - Start all services"
	@echo "  down           - Stop all services"
	@echo "  logs           - View all logs"
	@echo "  clean          - Stop and remove containers"
	@echo "  clean-volumes  - Stop and remove volumes"
	@echo "  rebuild        - Rebuild and restart"
	@echo "  test           - Run tests in Docker"
	@echo "  status         - Show container status"
	@echo "  push           - Push images to registry"
	@echo "  pull           - Pull images from registry"

# Development commands
build-dev:
	@echo "Building development image..."
	docker build -t $(IMAGE_DEV) -f docker/Dockerfile.dev .

up-dev:
	@echo "Starting development environment..."
	$(DOCKER_COMPOSE_DEV) up -d

down-dev:
	@echo "Stopping development environment..."
	$(DOCKER_COMPOSE_DEV) down

logs-dev:
	$(DOCKER_COMPOSE_DEV) logs -f

shell-dev:
	@echo "Opening shell in development container..."
	$(DOCKER_COMPOSE_DEV) exec pure-sound-dev /bin/bash

rebuild-dev: down-dev build-dev up-dev

# Production commands
build-prod:
	@echo "Building production image..."
	docker build -t $(IMAGE_PROD) -f docker/Dockerfile .

up-prod:
	@echo "Starting production environment..."
	$(DOCKER_COMPOSE_PROD) up -d

down-prod:
	@echo "Stopping production environment..."
	$(DOCKER_COMPOSE_PROD) down

logs-prod:
	$(DOCKER_COMPOSE_PROD) logs -f

shell-prod:
	@echo "Opening shell in production container..."
	$(DOCKER_COMPOSE_PROD) exec pure-sound-api /bin/bash

rebuild-prod: down-prod build-prod up-prod

# General commands
build:
	@echo "Building all images..."
	docker build -t $(IMAGE_NAME) -f docker/Dockerfile .
	docker build -t $(IMAGE_DEV) -f docker/Dockerfile.dev .

up:
	@echo "Starting all services..."
	$(DOCKER_COMPOSE) up -d

down:
	@echo "Stopping all services..."
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

clean:
	@echo "Stopping and removing containers..."
	$(DOCKER_COMPOSE) down --remove-orphans

clean-volumes:
	@echo "Stopping and removing containers and volumes..."
	$(DOCKER_COMPOSE) down -v --remove-orphans

rebuild: down build up

test:
	@echo "Running tests in Docker..."
	$(DOCKER_COMPOSE) run --rm pure-sound python -m pytest tests/ -v

test-in-docker:
	@echo "Running comprehensive tests..."
	docker run --rm -v $$(pwd):/app -w /app $(IMAGE_NAME) \
		python test_comprehensive.py

status:
	@echo "Showing container status..."
	$(DOCKER_COMPOSE) ps

push:
	@echo "Pushing images to registry..."
	docker tag $(IMAGE_NAME):latest $${REGISTRY:-docker.io}/$(IMAGE_NAME):latest
	docker push $${REGISTRY:-docker.io}/$(IMAGE_NAME):latest

pull:
	@echo "Pulling images from registry..."
	docker pull $(IMAGE_NAME):latest
