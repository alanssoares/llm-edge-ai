.PHONY: help build up down restart logs ps clean

help:
	@echo "Available commands:"
	@echo "  make build    - Build all edge device images"
	@echo "  make up       - Start all edge devices"
	@echo "  make down     - Stop all edge devices"
	@echo "  make restart  - Restart all edge devices"
	@echo "  make logs     - View logs from all devices"
	@echo "  make ps       - Show status of all devices"
	@echo "  make clean    - Remove all containers and images"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	docker compose down -v --rmi all
