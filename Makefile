.PHONY: help build up down logs clean migrate shell

help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start containers"
	@echo "  make down     - Stop containers"
	@echo "  make logs     - View logs"
	@echo "  make clean    - Remove containers and volumes"
	@echo "  make migrate  - Run database migrations"
	@echo "  make shell    - Open shell in app container"

build:
	docker buildx build . -t ghcr.io/teizeee/sportly:latest

up:
	docker-compose up -d
	@echo "Service is running at http://localhost:8000"
	@echo "phpMyAdmin at http://localhost:8080"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

migrate:
	docker-compose exec sportly alembic upgrade head

shell:
	docker-compose exec sportly /bin/bash

restart:
	docker-compose restart