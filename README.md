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

## Repository Structure

```
ISPN Growth/
├── roi-calculator/         # Full-stack ROI web app
│   ├── api/                # FastAPI backend
│   ├── frontend/           # React + TypeScript (Vite)
│   └── tests/              # pytest suite
├── gcs-engine/             # Growth Capacity Scoring pipeline
│   ├── src/                # Python CLI (connectors, signals, scoring, output)
│   ├── tests/              # pytest suite
│   └── data/               # Input CSVs
├── ISPN_Growth_Planning.md # Build plan and architecture notes
└── Fix-codebase.md         # Code review remediation tracker
```

## Status

Both projects are scaffolded with real implementations and stub data connectors. See `Fix-codebase.md` for the current remediation checklist before operational handoff.
