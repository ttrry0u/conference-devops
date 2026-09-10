SHELL := /bin/bash

.PHONY: setup run test quality verify

setup:
	python3 -m venv venv
	. venv/bin/activate
	pip install --upgrade pip
	pip install -r requirements.txt

run: setup
	. venv/bin/activate
	uvicorn main:app --reload

test: setup
	. venv/bin/activate
	pytest tests/ -v

quality: setup
	. venv/bin/activate
	black . --check
	flake8 .

verify: test quality