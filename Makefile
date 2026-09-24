.PHONY: help install seed train test run-backend run-frontend docker-up docker-down

help:
	@echo "AI Prompt Injection and Jailbreak Detection Firewall"
	@echo "======================================================"
	@echo "make install      : Install Python backend requirements"
	@echo "make seed         : Seed database with rules, datasets, and initial model"
	@echo "make train        : Train or re-train the ML classifier"
	@echo "make test         : Run automated test suite with pytest"
	@echo "make run-backend  : Start FastAPI backend on http://localhost:8000"
	@echo "make run-frontend : Start Vite frontend on http://localhost:5173"
	@echo "make docker-up    : Build and start all containers via docker compose"
	@echo "make docker-down  : Stop all running containers"

install:
	pip install -r backend/requirements.txt

seed:
	cd backend && python -m app.seed.seed_database

train:
	cd backend && python -m app.ml.train

test:
	cd backend && pytest -v

run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
