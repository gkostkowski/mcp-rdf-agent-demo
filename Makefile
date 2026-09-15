SHELL := /bin/sh

COMPOSE_FILE := infra/docker-compose.yaml
COMPOSE := docker compose -f $(COMPOSE_FILE)

.DEFAULT_GOAL := help

.PHONY: help install test test-unit test-integration demo-up up down logs ps graphdb-load graphdb-smoke down-volumes

help:
	@printf '%s\n' 'Available targets:'
	@printf '%s\n' '  install        Install Python dependencies with Poetry'
	@printf '%s\n' '  test           Run all Python tests'
	@printf '%s\n' '  test-unit      Run tests that do not require GraphDB'
	@printf '%s\n' '  test-integration Run tests requiring a local GraphDB instance'
	@printf '%s\n' '  demo-up        Start the currently available demo services'
	@printf '%s\n' '  up             Start normal services'
	@printf '%s\n' '  down           Stop normal services'
	@printf '%s\n' '  logs           Follow service logs'
	@printf '%s\n' '  ps             Show service status'
	@printf '%s\n' '  graphdb-load   DESTRUCTIVE: reset and load library-demo'
	@printf '%s\n' '  graphdb-smoke  Verify GraphDB and both named graphs'
	@printf '%s\n' '  down-volumes   DESTRUCTIVE: stop services and remove volumes'

install:
	poetry install

test:
	poetry run pytest

test-unit:
	poetry run pytest -m "not integration"

test-integration:
	poetry run pytest -m integration

demo-up: up

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

graphdb-load:
	@printf '%s\n' 'This deletes and reloads the library-demo repository.'
	@printf '%s' "Type 'load' to continue: "; read answer; test "$$answer" = 'load' || { printf '%s\n' 'Aborted.'; exit 1; }
	$(COMPOSE) up -d graphdb
	$(COMPOSE) build graphdb-loader
	$(COMPOSE) --profile loader run --rm --no-deps graphdb-loader load

graphdb-smoke:
	$(COMPOSE) --profile loader run --rm --no-deps graphdb-loader smoke

down-volumes:
	@printf '%s\n' 'This stops all services and removes all Compose-managed volumes.'
	@printf '%s' "Type 'delete' to continue: "; read answer; test "$$answer" = 'delete' || { printf '%s\n' 'Aborted.'; exit 1; }
	$(COMPOSE) down --volumes
