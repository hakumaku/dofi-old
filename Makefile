.PHONY: install install-dev \
	format lint test coverage \
	migrate makemigrations

install:
	@poetry install --no-root --without dev

install-dev:
	@poetry install --no-root

format:
	@poetry run black .
	@poetry run ruff check --fix .

lint:
	@poetry run black --check .
	@poetry run ruff check --show-source .
	@poetry run mypy .

test:
	@poetry run \
		python -m pytest -v \
		--junitxml=public/test/junit.xml \
		--html=public/test/report.html

coverage:
	@poetry run coverage run -m pytest
	@poetry run coverage report

makemigrations:
	@read -p "new commit message: " message; \
	poetry run python -m alembic revision --autogenerate -m "$$message"

migrate:
	@poetry run python -m alembic upgrade head
