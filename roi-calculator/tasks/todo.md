# Current Task: Review Remediation
**Branch**: `main`
**Started**: 2026-03-19

## Completed Phases

### Project Setup (Done)
- [x] Create project structure
- [x] Scaffold frontend (Vite + React + TypeScript)
- [x] Scaffold backend (FastAPI)
- [x] Generate specialist agents (roi-api-builder, roi-deployer, roi-frontend, roi-tester)

### Backend Implementation (Done)
- [x] FastAPI app with app factory pattern (`api/main.py`)
- [x] Configuration module with ISPN financial constants (`api/config.py`)
- [x] Pydantic models for request/response contracts (`api/models/`)
- [x] API routers (`api/routers/`)
- [x] Cost calculation engine / services (`api/services/`)
- [x] Middleware layer (`api/middleware/`)
- [x] Backend tests — 27 passing (`tests/test_cost_model.py`)

### Frontend Implementation (Done)
- [x] Vite + React + TypeScript scaffold (`frontend/`)
- [x] Input form component (`frontend/src/components/InputForm.tsx`)
- [x] Comparison view component (`frontend/src/components/ComparisonView.tsx`)
- [x] Recommendation view component (`frontend/src/components/RecommendationView.tsx`)
- [x] Type definitions (`frontend/src/types/`)
- [x] Utility / API client layer (`frontend/src/utils/`)
- [x] Styles (`frontend/src/styles/`)

### Infrastructure (Done)
- [x] Docker Compose configuration (`docker-compose.yml`)
- [x] Requirements files (`requirements.txt`, `requirements-dev.txt`)

## Review Remediation — Completed (2026-03-19)
- [x] Fixed datetime.utcnow() → datetime.now(timezone.utc) in responses.py
- [x] Created Dockerfile (multi-stage, non-root, healthcheck)
- [x] Created conftest.py for pytest discovery from project root
- [x] Removed deprecated version key from docker-compose.yml
- [x] Fixed negative savings display in ComparisonView.tsx (no more +-$X,XXX)
- [x] Set up vitest with @testing-library/react, created component + utility tests
- [x] Fixed CLAUDE.md: frontend path (src/ → frontend/src/), test command
- [x] Documented breakeven search assumptions in cost_model.py
- [x] Flagged after-hours 1.5x premium for business review
- [x] Created per-project .claude/settings.local.json

## Remaining for Ops
- [ ] Verify after-hours cost business intent (1.5x full rate vs 0.5x incremental)
- [ ] Implement middleware (api/middleware/logging.py, error_handler.py)
- [ ] Add API integration tests (POST /api/calculate via TestClient)
- [ ] Add frontend Docker Compose service
- [ ] PDF export functionality
- [ ] Mobile responsive polish

## Verification
- [x] `python -m pytest tests/ -v` — all tests pass
- [x] `npx vitest run` — all frontend tests pass
- [x] No regressions introduced
- [x] CLAUDE.md reflects actual project state
