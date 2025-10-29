# GR-Experience

GR-Experience is a full-stack telemetry analytics platform for the Toyota GR Cup. It ingests raw timing archives, normalises and stores telemetry to columnar Parquet datasets, models tyre degradation and lap performance, and exposes insights via a FastAPI backend and a Next.js dashboard.

## Features

- **Data ingestion pipeline**: ZIP extraction with checksum validation, schema normalisation and Parquet persistence partitioned by `session_id/track`.
- **Machine learning models**: RandomForest baseline for lap prediction, linear tyre degradation regression and Dynamic Time Warping comparisons for driver coaching.
- **API + WebSocket**: Typed FastAPI endpoints for ingestion, telemetry pagination, strategy simulation, training comparisons and live telemetry streaming.
- **Interactive frontend**: React Query powered dashboards with Plotly charts, strategic recommendations and a Three.js 3D replay.
- **Tooling**: pytest + React Testing Library coverage, Ruff/Mypy linting, GitHub Actions CI and Docker Compose sandbox.

## Getting started

### Requirements

- Python 3.11
- Node.js 20
- Redis (only required when running the API with caching)

### Environment variables

Copy `.env.example` to `.env` and adjust if required:

```bash
cp .env.example .env
```

### Installing dependencies

```bash
# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Frontend
cd frontend
npm install
```

### Running the stack

Local development with Docker Compose:

```bash
make dev
```

Manual terminals:

```bash
# API
make api

# Frontend
make web
```

### Ingesting telemetry archives

Archives must live under `DATA_DIR` (default `./data`). The CLI orchestrates extraction, normalisation and persistence:

```bash
python scripts/prepare_sample_archive.py --data-dir ./data
make ingest ZIP=./data/input/barber-motorsports-park.zip SESSION=grcup_barber_2025
```

The API also exposes `POST /api/sessions/{session_id}/ingest` for remote pipelines.

### Tests & Quality

```bash
# Backend tests + linters
make test
make lint

# Frontend only
cd frontend
npm run test
npm run build
```

Continuous Integration runs the same suite in `.github/workflows/ci.yml`.

## Project layout

```
backend/
  app/
    config.py          # Pydantic settings
    main.py            # FastAPI application
    dataio/            # Extraction, normalisation and Parquet store
    models/            # Feature engineering, ML baselines & strategy engine
    routes/            # REST + WebSocket routers
  tests/               # pytest integration & unit tests
frontend/
  src/
    pages/             # Next.js pages (sessions, training, replay)
    components/        # Layout, charts, strategy & telemetry widgets
    lib/               # API helpers & React Query client
    types/             # Shared API typings
```

## Demo dataset

Sample telemetry ships as CSV under `data/samples/barber-motorsports-park.csv`. Generate an archive with `python scripts/prepare_sample_archive.py --data-dir ./data` before running `make ingest` to explore the dashboards at `http://localhost:3000`.

## Scripts

- `backend/app/cli.py`: command line utilities (currently ingestion).
- `scripts/prepare_sample_archive.py`: build ZIP archives from the sample CSVs.
- `scripts/demo_seed.py`: populate a demo session for the web UI.

## Docker images

- `api`: FastAPI backend served by Uvicorn.
- `web`: Next.js dev server.
- `redis`: caching layer for telemetry summaries & lap pagination.

## CI/CD

GitHub Actions run linting, mypy, pytest, Jest and Next.js builds on every push/PR. Ensure the suite is green before opening a pull request.

## Contributing

Install pre-commit hooks locally:

```bash
pip install pre-commit
pre-commit install
```

This enforces Ruff formatting and mypy checks before every commit.
