SHELL := /bin/bash

VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
BLACK := $(VENV)/bin/black
FLAKE8 := $(VENV)/bin/flake8
UVICORN := $(VENV)/bin/uvicorn

.PHONY: setup run test quality verify

setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(UVICORN) main:app --reload

test:
	$(PYTEST) tests/ -v

quality:
	$(BLACK) . --check
	$(FLAKE8) .

verify: test quality
