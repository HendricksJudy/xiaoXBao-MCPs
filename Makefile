.PHONY: lint test run

install:
poetry install

lint:
poetry run black . && poetry run isort . && poetry run flake8

test:
poetry run pytest

run:
poetry run uvicorn api_gateway.main:app --host 0.0.0.0 --port 8080
