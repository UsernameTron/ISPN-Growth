# DevOps Handoff — ISPN Growth Monorepo

## Executive Summary

Two independent projects under one repository, sharing CI but no runtime dependencies:

| Project | Purpose | Stack | Port |
|---------|---------|-------|------|
| **ROI Calculator** | Cost comparison tool for ISP outsourcing decisions | React+TS (Vite) + Python/FastAPI | 5173 (frontend), 8000 (backend) |
| **GCS Engine** | Partner scoring CLI pipeline | Python (pandas, numpy, openpyxl) | N/A (CLI) |

No database. No authentication. No PII collection. Stateless calculations only.

---

## Environment Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| Node.js | 20+ |
| npm | 10+ (ships with Node 20) |
| pip | Latest |

No external services required (no database, no Redis, no message queue).

---

## How to Run

### ROI Calculator — Development

```bash
# Backend
cd roi-calculator
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Frontend (separate terminal)
cd roi-calculator/frontend
npm install
npm run dev    # Vite dev server on :5173, proxies /api -> :8000
```

### ROI Calculator — Docker

```bash
cd roi-calculator
docker compose up        # backend :8000 + frontend :5173
docker compose up -d     # detached
```

Single-container production build:

```bash
cd roi-calculator
docker build -t ispn-roi .
docker run -p 8000:8000 ispn-roi
# Frontend assets served from /app/static, backend at :8000
```

### GCS Engine

```bash
cd gcs-engine
pip install -r requirements.txt
python -m src.main                              # full pipeline
python -m src.main --partners 5 --format both   # limited run
```

Output: Excel report + optional CSV in `gcs-engine/output/` (gitignored).

### Tests

```bash
# All projects (from repo root)
make test

# Individual
make test-roi-backend     # cd roi-calculator && python -m pytest tests/ -v
make test-roi-frontend    # cd roi-calculator/frontend && npx vitest run
make test-gcs             # cd gcs-engine && python -m pytest tests/ -v

# Lint
make lint                 # ruff check on both projects
```

---

## Configuration Reference

### ROI Calculator — Environment Variables

All settings defined in `roi-calculator/api/config.py` (Pydantic Settings). Override via `.env` file or environment variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Runtime environment identifier |
| `LOG_LEVEL` | `info` | Logging level |
| `BLENDED_RATE` | `21.00` | ISPN blended hourly rate (USD) |
| `MULTIPLIER` | `1.35` | Cost multiplier for overhead |
| `UTILIZATION_TARGET` | `0.60` | Agent utilization target (0-1) |
| `INDUSTRY_TURNOVER` | `0.35` | Industry turnover rate (0-1) |
| `TRAINING_RAMP_WEEKS` | `6` | New hire training ramp period |
| `AFTER_HOURS_PREMIUM` | `1.50` | After-hours rate multiplier |
| `MANAGEMENT_OVERHEAD` | `0.15` | Management overhead percentage (0-1) |
| `QA_MONITORING_OVERHEAD` | `0.08` | QA/monitoring overhead percentage (0-1) |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins (JSON list) |

Frontend env var (set in `roi-calculator/frontend/.env` or build-time):

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE` | (empty, uses proxy) | Backend API base URL |

### GCS Engine — Configuration

All settings in `gcs-engine/src/config.py` (Python dataclass). No env var override — modify the file directly.

| Setting | Value | Description |
|---------|-------|-------------|
| Signal weights | See `GCSConfig.signal_weights` | 8 signals, weights must sum to 1.0 (excl. disabled) |
| `tier_green` | 70.0 | Composite score threshold for green tier |
| `tier_amber` | 40.0 | Composite score threshold for amber tier |
| `score_min` / `score_max` | 0.0 / 100.0 | Composite score range |
| `signal_min` / `signal_max` | 0 / 3 | Per-signal score range |

---

## CI/CD Pipeline

**File**: `.github/workflows/pr-validation.yml`

Triggers on push to `main` and pull requests targeting `main`.

| Job | Runner | What it does |
|-----|--------|--------------|
| `roi-backend` | ubuntu-latest | Python 3.12, install deps, `pytest tests/ -v` |
| `roi-frontend` | ubuntu-latest | Node 20 (npm cache), `npx vitest run` |
| `gcs-engine` | ubuntu-latest | Python 3.12, install deps, `pytest tests/ -v` |

All three jobs run in parallel. All must pass for PR merge.

---

## Container & Deployment

### Dockerfile (`roi-calculator/Dockerfile`)

Multi-stage build:
1. **frontend-builder** — Node 20, `npm ci && npm run build`
2. **builder** — Python 3.12, install pip dependencies to `/install`
3. **runtime** — Python 3.12-slim, non-root user (`appuser`, UID 1000), copies deps + app code + frontend assets

Health check: `GET http://localhost:8000/api/health` every 30s (5s timeout, 10s start period, 3 retries).

### docker-compose.yml (`roi-calculator/docker-compose.yml`)

Development setup with hot-reload:
- **backend**: Builds from Dockerfile, mounts `./api` for live reload, port 8000
- **frontend**: Node 20 image, mounts `./frontend`, port 5173, depends on backend

Shared network: `app-network`.

---

## Security Notes

- **No authentication** — This is an internal/demo calculator tool.
- **No PII collection** — Only financial parameters are submitted; nothing is stored.
- **Non-root container** — Runtime runs as `appuser` (UID 1000).
- **No secrets in code** — All ISPN financial constants are configuration, not secrets.
- **CORS restricted** — Default allows only `localhost:5173`.
- **No database** — Stateless. No migration risk.

---

## Deployment Maturity

| Aspect | Status | Notes |
|--------|--------|-------|
| CI (automated tests) | Done | GitHub Actions, 3 parallel jobs |
| Docker build | Done | Multi-stage, non-root |
| Docker Compose (dev) | Done | Hot-reload for both services |
| Staging environment | Not started | No staging infra yet |
| Production deployment | Not started | No CD pipeline |
| Monitoring/alerting | Not started | Health endpoint exists, no external monitoring |
| Log aggregation | Not started | Structured JSON logging in middleware |

---

## Known Tech Debt

1. **No CD pipeline** — CI validates but does not deploy. Manual deployment only.
2. **No staging environment** — Changes go from local dev to production (when deployed).
3. **GCS Engine has no Docker setup** — CLI tool runs directly on host.
4. **No rate limiting** — Public calculator endpoint has no request throttling.
5. **Frontend proxy only in dev** — Production deployment needs reverse proxy config (nginx/Caddy) or backend static file serving.
6. **No HTTPS termination** — Must be handled by load balancer or reverse proxy in production.
