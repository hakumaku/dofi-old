.PHONY: format lint

format:
	@poetry run isort .
	@poetry run black .

lint:
	@poetry run \
		isort --check-only .
	@poetry run \
		black --check .
	@poetry run \
		flake8 . --config setup.cfg
	@poetry run \
		mypy .
