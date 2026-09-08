.PHONY: help install dev install-dev init-db train predict run test lint clean docker-up docker-down

help:
	@echo "Predicción Deportiva - Makefile"
	@echo ""
	@echo "Comandos disponibles:"
	@echo "  make install      Instalar dependencias"
	@echo "  make dev          Instalar dependencias de desarrollo"
	@echo "  make init-db      Inicializar base de datos"
	@echo "  make train        Entrenar modelos"
	@echo "  make predict      Ejecutar predicción (usa MATCH_ID=1)"
	@echo "  make run          Iniciar servidor de desarrollo"
	@echo "  make test         Ejecutar tests"
	@echo "  make lint         Verificar código con flake8"
	@echo "  make typecheck    Verificar tipos con mypy"
	@echo "  make clean        Limpiar archivos temporales"
	@echo "  make docker-up    Iniciar servicios Docker"
	@echo "  make docker-down  Detener servicios Docker"

install:
	pip install -r requirements.txt

dev: install
	pip install -r requirements-dev.txt

init-db:
	python scripts/init_db.py

train:
	python scripts/train_models.py

predict:
	python scripts/run_prediction.py $(MATCH_ID)

run:
	python -m src.api.app

scrape:
	python scripts/run_scraping.py

scheduler:
	python -m src.etl.scheduler

test:
	pytest tests/ -v --cov=src --cov-report=term

lint:
	flake8 src/ tests/

typecheck:
	mypy src/

clean:
	rm -rf data/raw/*
	rm -rf data/processed/*
	rm -rf data/cache/*
	rm -rf data/exports/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down
