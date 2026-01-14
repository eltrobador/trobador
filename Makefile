.PHONY: dev prod build down logs clean

# Development mode with hot reload
dev:
	docker compose -f compose.yml -f compose.dev.yml up --build

# Production mode
prod:
	docker compose -f compose.yml -f compose.prod.yml up --build -d

# Build images without starting
build:
	docker compose -f compose.yml -f compose.prod.yml build

# Stop all services
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Clean up everything
clean:
	docker compose down -v --rmi local
