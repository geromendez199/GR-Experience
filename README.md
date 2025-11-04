# GR-Experience

GR-Experience is a full-stack telemetry analytics platform for the Toyota GR Cup. It ingests raw timing archives, normalises and stores telemetry to columnar Parquet datasets, models tyre degradation and lap performance, and exposes insights via a FastAPI backend and a Next.js dashboard.

## Features

- **Data ingestion pipeline**: ZIP extraction with checksum validation, schema normalisation and Parquet persistence partitioned by `session_id/track`.
- **Machine learning models**: RandomForest baseline for lap prediction, linear tyre degradation regression and Dynamic Time Warping comparisons for driver coaching.
- **API + WebSocket**: Typed FastAPI endpoints for ingestion, telemetry pagination, strategy simulation, training comparisons and live telemetry streaming.
- **Interactive frontend**: React Query powered dashboards with Plotly charts, strategic recommendations and a Three.js 3D replay.
- **Tooling**: pytest + React Testing Library coverage, Ruff/Mypy linting, GitHub Actions CI and Docker Compose sandbox.

## Getting started

The following quickstart walks through the exact steps required to spin up the
platform locally. Each item expands on the high-level checklist in the project
board.

1. **Install prerequisites**
   - Verify Python and Node.js meet the required versions:

     ```bash
     python --version  # expected 3.11.x
     node --version    # expected v20.x
     ```

     > If `node --version` prints v21 or newer (Windows often bundles a newer
     > build), install Node 20 using your version manager before continuing.
     > Examples:
     >
     > - **macOS/Linux**: `nvm install 20 && nvm use 20`
     > - **Windows**: `nvm install 20.12.2 && nvm use 20.12.2` (from
     >   [nvm-windows](https://github.com/coreybutler/nvm-windows))

   - Install Redis if you plan to enable the API cache (the development stack
     starts a Redis container automatically, but a local binary is handy for
     manual runs).

2. **Clone the repository**

   ```bash
   git clone https://github.com/geromendez199/GR-Experience.git
   cd GR-Experience
   ```

3. **Copy environment variables**

   ```bash
   cp .env.example .env
   ```

4. **Install dependencies**
   - Backend:

     ```bash
     python -m venv .venv
     source .venv/bin/activate  # PowerShell: .\.venv\Scripts\Activate.ps1
     pip install -r backend/requirements.txt
     ```

   - Frontend:

     ```bash
     cd frontend
     npm install
     cd ..
     ```

5. **Run the stack in development mode**

   ```bash
   make dev
   ```

   This targets the same `api`, `web`, and `redis` services as the Docker
   Compose configuration for parity with CI.

   > **Tip for Visual Studio Code users**: open the workspace folder in VS
   > Code and run `make dev` from the integrated terminal so both services log
   > inline next to your editor.

6. **Verify the API and dashboard**
   - Open <http://localhost:8000/docs> to browse the FastAPI-generated schema
     and try live requests.
   - Navigate to <http://localhost:3000> to interact with the Next.js dashboard.

7. **Ingest sample telemetry (optional)**

   ```bash
   python scripts/prepare_sample_archive.py --data-dir ./data
   make ingest ZIP=./data/input/barber-motorsports-park.zip SESSION=grcup_barber_2025
   ```

   After ingestion completes, the session appears on the dashboard with lap and
   strategy visualisations. The API also exposes
   `POST /api/sessions/{session_id}/ingest` for remote pipelines.

### Manual service startup (without `make`)

If you prefer to run the backend and frontend individually—whether to debug in
VS Code, to work around a limited shell environment, or to control logging—you
can start each service with the commands below once dependencies are installed
and the virtual environment is activated.

1. **Backend (FastAPI + Uvicorn)**

   - **macOS/Linux**

     ```bash
     export $(grep -v '^#' .env | xargs)  # load environment variables
     uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
     ```

   - **Windows (PowerShell)**

     ```powershell
     Get-Content .env | ForEach-Object {
       if ($_ -match '^(?<key>[^#=]+)=(?<value>.*)$') {
         $name = $Matches['key']
         $value = $Matches['value']
         [System.Environment]::SetEnvironmentVariable($name, $value)
       }
     }
     uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
     ```

   The `--reload` flag enables hot reloading so code edits immediately refresh
   the API server.

2. **Frontend (Next.js)**

   ```bash
   cd frontend
   npm run dev -- --hostname 0.0.0.0 --port 3000
   ```

   If you are following along in VS Code, run the backend and frontend from two
   integrated terminals so both remain active. On Windows make sure these
   commands execute inside the Developer PowerShell (or Git Bash) that already
   sourced the virtual environment; invoking `npm exec` directly will not start
   the dashboard.

With both commands running, revisit <http://localhost:8000/docs> and
<http://localhost:3000> to validate the stack end-to-end.

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
