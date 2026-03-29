.PHONY: build rebuild up down logs

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
