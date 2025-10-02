.PHONY: help generate build up down restart logs ps clean

DEVICES ?= 10

help:
	@echo "Available commands:"
	@echo "  make generate DEVICES=N  - Generate docker-compose.yml with N devices (default: 10)"
	@echo "  make build               - Build all edge device images"
	@echo "  make up                  - Start all edge devices"
	@echo "  make down                - Stop all edge devices"
	@echo "  make restart             - Restart all edge devices"
	@echo "  make logs                - View logs from all devices"
	@echo "  make ps                  - Show status of all devices"
	@echo "  make clean               - Remove all containers and images"
	@echo ""
	@echo "Examples:"
	@echo "  make generate DEVICES=50   # Generate compose file with 50 devices"
	@echo "  make generate DEVICES=1000 # Generate compose file with 1000 devices"

generate:
	python3 generate-compose.py --devices $(DEVICES)

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
