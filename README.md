# ISPN Growth

Monorepo for ISPN's growth strategy tools — two greenfield projects built to support prospect engagement and internal capacity planning.

## Projects

### ROI Calculator (`roi-calculator/`)

Prospect-facing web application that calculates the return on investment for outsourcing contact center operations to ISPN.

- **Frontend**: React + TypeScript (Vite)
- **Backend**: Python / FastAPI
- **No database** — stateless calculations using ISPN financial constants
- **No auth** — public-facing calculator

Key features:
- Cost modeling with ISPN's blended rate ($21.00), multiplier (1.35x), utilization (60%), and turnover (35%) constants
- Scenario comparison with after-hours, management, QA, and technology overhead
- Recharts-based data visualization
- Pydantic-validated API contracts with typed response envelopes

```bash
# Backend
cd roi-calculator
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Frontend
cd roi-calculator/frontend
npm install
npm run dev  # port 5173

# Docker (development)
cd roi-calculator
docker compose up

# Tests
python -m pytest tests/ -v   # backend
npx vitest run               # frontend
```

### GCS Engine (`gcs-engine/`)

Internal scoring pipeline that evaluates growth capacity across ISPN's client portfolio using a weighted signal model.

- **Python CLI** — pandas, numpy, openpyxl
- **No web server, no database**
- Connector pattern with stub/live swap for data sources

Scoring model (8 signals, weighted 0–100):

| Signal | Weight |
|--------|--------|
| Volume Growth | 25% |
| SLA Degradation | 20% |
| Service Concentration | 15% |
| BEAD Exposure | 15% |
| Utilization Headroom | 10% |
| Repeat Contacts | 10% |
| Seasonal Volatility | 5% |

Tiers: **Green** (>70) · **Amber** (40–70) · **Red** (<40)

```bash
cd gcs-engine
pip install -r requirements.txt
python -m src.main          # run pipeline
pytest tests/               # run tests
```

## Monorepo Commands

```bash
make test              # run all 177 tests across both projects
make test-roi-backend  # ROI Calculator backend only
make test-roi-frontend # ROI Calculator frontend only
make test-gcs          # GCS Engine only
make lint              # ruff check both projects
```

## CI/CD

GitHub Actions runs three parallel jobs on every PR and push to `main`:
- **roi-backend** — Python 3.12, pytest
- **roi-frontend** — Node 20, vitest
- **gcs-engine** — Python 3.12, pytest

See `.github/workflows/pr-validation.yml`.

## Repository Structure

```
ISPN Growth/
├── roi-calculator/         # Full-stack ROI web app
│   ├── api/                # FastAPI backend
│   │   ├── config.py       # ISPN constants (env-overridable)
│   │   ├── middleware/      # Error handling + request logging
│   │   ├── models/         # Pydantic request/response schemas
│   │   ├── routers/        # /api/calculate, /api/health
│   │   └── services/       # Cost model (Decimal math)
│   ├── frontend/           # React + TypeScript (Vite)
│   ├── tests/              # pytest suite
│   ├── Dockerfile          # Multi-stage (Node build + Python runtime)
│   └── docker-compose.yml  # Dev: backend + frontend services
├── gcs-engine/             # Growth Capacity Scoring pipeline
│   ├── src/                # Python CLI
│   │   ├── connectors/     # Data source stubs (swap to live via __init__.py)
│   │   ├── signals/        # 8 signal scorers (0–3 each)
│   │   ├── scoring/        # Composite engine + recommender
│   │   └── output/         # Excel report + markdown summary
│   ├── tests/              # pytest suite
│   └── data/               # Input CSVs
├── .github/workflows/      # CI/CD pipeline
├── Makefile                # Monorepo test runner
├── CLAUDE.md               # AI assistant guidance
├── ISPN_Growth_Planning.md # Build plan and architecture notes
└── Fix-codebase.md         # Code review remediation tracker
```

## Current Status

All critical remediation items resolved. 177 tests passing across both projects (ROI backend 42, ROI frontend 10, GCS Engine 125). Structured JSON logging, request ID tracking, and normalized error responses in place. CI/CD pipeline green. See `Fix-codebase.md` for the complete audit trail and `docs/DEVOPS-HANDOFF.md` for operational deployment guidance.

---

## DevOps: Next Steps to Make This Operational

### ROI Calculator — Production Deployment

**1. Configure production environment variables**

The backend uses Pydantic Settings loaded from `.env`. Create a production `.env` or inject via your platform's env config:

```bash
ENVIRONMENT=production
CORS_ORIGINS=["https://roi.ispn.com"]  # replace with actual domain
LOG_LEVEL=warning
```

All ISPN financial constants have sensible defaults in `api/config.py` and do not need overriding unless business values change.

**2. Set the frontend API base URL**

The Vite frontend defaults to `/api` (relative). For production builds where the API is on a different origin:

```bash
VITE_API_BASE=https://api.ispn.com  # set before npm run build
cd roi-calculator/frontend && npm run build
```

The built assets land in `frontend/dist/`.

**3. Serve the production build**

Option A — **Single container** (Dockerfile already handles this):
```bash
cd roi-calculator
docker build -t ispn-roi-calculator .
docker run -p 8000:8000 \
  -e CORS_ORIGINS='["https://roi.ispn.com"]' \
  -e ENVIRONMENT=production \
  ispn-roi-calculator
```
Frontend static assets are served from `/app/static` inside the container. You'll need to either:
- Add a `StaticFiles` mount in FastAPI to serve them, or
- Put nginx/Cloudfront in front

Option B — **Separate services** (recommended for scale):
- Deploy the API container behind a load balancer
- Serve `frontend/dist/` from a CDN (Netlify, Vercel, S3+CloudFront)
- Point `VITE_API_BASE` at the API URL

**4. Lock down CORS for production**

Current default: `["http://localhost:5173"]`. Override via `CORS_ORIGINS` env var with the actual production domain. Also consider setting `allow_credentials=False` in `api/main.py` (currently `True` but no auth exists).

### GCS Engine — Operational Deployment

**5. Replace stub connectors with live data sources**

All 6 connectors follow the same `get_data() -> pd.DataFrame` interface. To swap:

1. Create `src/connectors/<name>_live.py` implementing the same interface
2. Change the import in `src/connectors/__init__.py`
3. No downstream code changes needed

Connectors to implement:

| Connector | Stub File | Data Source | Returns |
|-----------|-----------|-------------|---------|
| Genesys | `genesys_stub.py` | Genesys Cloud CX API | volume_growth_rate, service_level_pct |
| HelpDesk | `helpdesk_stub.py` | ISPN HelpDesk system | repeat_contact_rate |
| UKG | `ukg_stub.py` | UKG Workforce API | utilization_rate |
| WCS | `wcs_stub.py` | Weekly Call Stats export | seasonal_variance_coeff |
| Service Mix | `service_mix.py` | Manual CSV or CRM | partner_id, services list |
| BEAD | `bead_data.py` | BEAD program tracker | state, status, partner_ids |

**6. Schedule the pipeline**

GCS Engine runs as a CLI. For monthly scoring:

```bash
# Cron, Airflow, or CI scheduled job
cd gcs-engine && python -m src.main --format both --output-dir /shared/reports/
```

Output: `output/gcs_report_YYYY-MM.xlsx` + CSV.

### Infrastructure — Both Projects

**7. Set up secrets management**

Neither project currently requires secrets (no database, no auth). When live connectors are added to GCS Engine, store API keys in:
- AWS Secrets Manager / Parameter Store
- HashiCorp Vault
- Platform-native env injection (Heroku, Railway, etc.)

Never commit `.env` files — they are gitignored.

**8. Add monitoring**

The ROI Calculator now has request logging middleware (`api/middleware/logging_middleware.py`) that logs method, path, status, and duration. Connect this to your observability stack:
- Structured JSON logs → CloudWatch / Datadog / ELK
- Healthcheck endpoint: `GET /api/health`
- Key metric: response time on `POST /api/calculate`

**9. DNS and TLS**

- Point your chosen domain at the deployment target
- Enable TLS (Let's Encrypt, ACM, or platform-managed)
- Update `CORS_ORIGINS` to match the final domain
