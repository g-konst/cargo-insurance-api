.DEFAULT_GOAL := run

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
