.DEFAULT_GOAL := up

VENV = venv

include .env.example
-include .env
export

venv:
	python3.12 -m venv $(VENV)

install: venv
	poetry use $(VENV)/bin/python
	poetry install

build:
	poetry build

up: build
	docker-compose up --build

revision:
	alembic revision --autogenerate -m "$(msg)"

migration_up:
	alembic upgrade "$(r)"

migration_down:
	alembic downgrade "$(r)"

run:
	gunicorn -k uvicorn.workers.UvicornWorker \
        --workers 4 \
        --threads 2 \
        --bind ${APP__API__HOST}:${APP__API__PORT} \
        app.api.http_server:application