# À lancer depuis backend/ (make test, make run…). Le visuel est dans ../frontend/.
.PHONY: install migrate run super test lint format check

install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements/dev.txt

migrate:
	python manage.py migrate

run:
	python manage.py runserver

super:
	python manage.py createsuperuser

test:
	pytest

lint:
	ruff check . && black --check .

format:
	ruff check --fix . && black .

check:
	python manage.py check
