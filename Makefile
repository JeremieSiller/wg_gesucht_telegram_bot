FILES := $(wildcard *.py)

python-install-dependencies:
	poetry install

python-test: $(FILES)
	poetry run pytest

python-sort: python-remove-unused-imports
	poetry run isort .

python-remove-unused-imports: $(FILES)
	poetry run autoflake -i -r --remove-all-unused-imports .

python-format: python-sort
	poetry run black .

flake8: $(FILES)
	poetry run flake8 --max-complexity 10 --ignore E501 .

mypy: $(FILES)
	poetry run mypy --ignore-missing-imports --python-version 3.10 --follow-imports=normal --show-column-numbers --disallow-untyped-defs .

python-check: flake8 mypy

python-pre-commit: python-format python-check python-test
