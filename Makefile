.PHONY: setup run test quality verify

setup:
	python3 -m venv venv
	. venv/bin/activate
	pip install -r requirements.txt

run:
	. venv/bin/activate
	uvicorn main:app --reload

test:
	. venv/bin/activate
	pytest tests/ -v

quality:
	. venv/bin/activate
	black . --check
	flake8 .

verify: test quality