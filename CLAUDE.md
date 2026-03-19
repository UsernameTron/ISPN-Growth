# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Monorepo Layout

Two independent projects under one repo. Each has its own `CLAUDE.md` with project-specific governance rules — read the relevant one before working in that project.

| Project | Path | Stack |
|---------|------|-------|
| ROI Calculator | `roi-calculator/` | React+TS (Vite) frontend + Python/FastAPI backend |
| GCS Engine | `gcs-engine/` | Python CLI pipeline (pandas, numpy, openpyxl) |

Reference-only directories (`Claude MCP Ecosystem copy/`, `claude-code-factory copy/`) are gitignored and not part of the build.

## Build & Test Commands

### ROI Calculator

```bash
# Backend
cd roi-calculator
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn api.main:app --reload --port 8000

# Frontend
cd roi-calculator/frontend
npm install
npm run dev          # Vite dev server on :5173, proxies /api → :8000

# Tests (run from roi-calculator/)
python -m pytest tests/ -v              # backend
cd frontend && npx vitest run           # frontend
python -m pytest tests/ -v -k "test_breakeven"  # single test
```

### GCS Engine

```bash
# Run
cd gcs-engine
pip install -r requirements.txt
python -m src.main                              # full pipeline
python -m src.main --partners 5 --format both   # limited run

# Tests (run from gcs-engine/)
python -m pytest tests/ -v
python -m pytest tests/test_signals.py -v       # single file
python -m pytest tests/ -v -k "test_volume"     # single test
```

## Architecture

### ROI Calculator

Stateless cost comparison tool — no database, no auth.

**Backend pipeline:** `api/routers/calculate.py` → `api/services/cost_model.py` → returns `ROICalculationResponse`

- App factory pattern in `api/main.py` (`create_app()`)
- All ISPN financial constants live in `api/config.py` (Pydantic Settings, env-overridable)
- All monetary math uses `Decimal` — never `float` for money
- Response envelope: `ROICalculationResponse` wraps `CostBreakdown` for both in-house and ISPN scenarios
- Recommendation logic: >15% savings → "outsource", 5–15% → "flex", <5% → "in_house"
- Breakeven calculation uses binary search on subscriber count

**Frontend:** Three-step wizard (input → comparison → recommendation). State via React hooks only. API client in `frontend/src/api/client.ts` uses `VITE_API_BASE` env var. Vite proxies `/api` to backend in dev.

### GCS Engine

CLI pipeline that scores partners on 8 weighted signals (0–3 each), computes a composite (0–100), assigns tiers.

**Pipeline:** `src/main.py` → load 6 connectors → `scoring/engine.py:score_all_partners()` → `output/report.py` (Excel) + `output/summary.py` (markdown)

- Signal weights are in `src/config.py` (`GCSConfig` dataclass) — never hardcode in scorers
- **Connector pattern:** all implement `get_data() -> pd.DataFrame`. Stubs in `*_stub.py`, live replacements in `*_live.py`. Swap by changing import in `src/connectors/__init__.py`
- Missing data handling: signals with NaN source data are excluded from composite score; remaining weights are rescaled
- Tiers: green (>70), amber (40–70), red (<40)
- Output: multi-sheet Excel (Ranked Partners, Signal Detail, Methodology) + optional CSV

## Key Constraints

- **ROI Calculator:** `Decimal` for all money. Constants from `api/config.py` only. Both pytest and vitest must pass.
- **GCS Engine:** Signal weights from `src/config.py` only (must sum to 1.0 excluding contract_proximity at 0%). Each scorer handles NaN input. Never commit generated Excel files.
- **Both projects:** Python 3.12+. Type hints on public functions. Each has its own `tasks/`, `context/`, `state/` directories — `context/` and `state/` are gitignored and private.
