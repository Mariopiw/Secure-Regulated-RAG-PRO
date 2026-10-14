install:
	python -m venv .venv
	. .venv/bin/activate && pip install -e ".[dev]"

up:
	docker compose up --build

down:
	docker compose down

reset:
	docker compose down -v

test:
	pytest -q

lint:
	ruff check .

migrate:
	alembic upgrade head
