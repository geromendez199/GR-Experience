.PHONY: dev api web ingest test lint

PYTHON ?= python3
PIP ?= pip
NPM ?= npm

setup-backend:
cd backend && $(PIP) install -r requirements.txt

setup-frontend:
cd frontend && $(NPM) install

api: setup-backend
cd backend && uvicorn app.main:app --host $${API_HOST:-0.0.0.0} --port $${API_PORT:-8000}

web: setup-frontend
cd frontend && $(NPM) run dev

dev:
docker-compose up --build

ingest: setup-backend
@if [ -z "$(ZIP)" ]; then echo "ZIP variable required"; exit 1; fi
@if [ -z "$(SESSION)" ]; then echo "SESSION variable required"; exit 1; fi
cd backend && $(PYTHON) -m app.cli ingest $(SESSION) $(ZIP)

test: setup-backend setup-frontend
cd backend && pytest -q
cd frontend && $(NPM) run test -- --runInBand

lint: setup-backend setup-frontend
cd backend && ruff check app && mypy app
cd frontend && $(NPM) run lint
