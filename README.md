# GR-Experience

Repositorio para el proyecto GR Experience del Hack the Track 2025

## Arquitectura

```
GR-Experience/
├── backend/              # API FastAPI y lógica de analítica
├── data/                 # Scripts de ingesta y normalización de datasets
├── frontend/             # Aplicación Next.js + Three.js
├── docker-compose.yml    # Orquestación de frontend y backend
└── requirements.txt      # Dependencias Python para desarrollo y pruebas
```

### Backend (FastAPI)

- Endpoints REST bajo `/api` para métricas agregadas, comparativas de vueltas y recomendaciones de estrategia.
- WebSocket `/ws/live-telemetry` para transmitir frames de telemetría en tiempo real (modo eco por defecto).
- Servicios en `backend/app/services` que simulan la lógica de negocio con datos en memoria listos para reemplazar por la canalización real.

#### Ejecutar backend en local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

La API estará disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

### Frontend (Next.js + TypeScript + Three.js)

- Dashboard interactivo que consume el endpoint de analítica y muestra un gráfico SVG con los tiempos de vuelta.
- Página `/replay` que renderiza una escena 3D simple con `@react-three/fiber` y controles orbitales.

#### Ejecutar frontend en local

```bash
cd frontend
npm install
npm run dev
```

La aplicación se servirá en `http://localhost:3000`.

### Ingesta de datos

`data/scripts/download_datasets.py` contiene utilidades para descargar y extraer datasets comprimidos. Incluye pruebas unitarias en `data/tests/` para validar la extracción ZIP/TAR y la limpieza de directorios.

### Docker Compose

Levanta ambos servicios con recarga automática:

```bash
docker-compose up --build
```

El frontend se conectará al backend mediante `NEXT_PUBLIC_API_BASE_URL` definido en `docker-compose.yml`.

### Pruebas

Ejecuta la suite con:

```bash
pytest
```

Actualmente se cubren los módulos de analítica del backend y utilidades de ingestión de datos.
