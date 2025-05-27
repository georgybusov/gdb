# Makefile

setup:
	python -m venv env
	. env/bin/activate && pip install -r requirements.txt

test:
	. env/bin/activate && pytest

format:
	. env/bin/activate && black src tests

lint:
	. env/bin/activate && flake8 src tests
