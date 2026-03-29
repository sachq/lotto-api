.PHONY: build rebuild up down logs fetch-data mcp

build:
	docker compose build

rebuild:
	docker compose up --build -d

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

fetch-data:
	docker exec lotto_api python -m app.scripts.lotto_data

mcp:
	docker compose run --rm mcp
