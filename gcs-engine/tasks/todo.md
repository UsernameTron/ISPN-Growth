# Current Task: Review Remediation
**Branch**: `main`
**Started**: 2026-03-19

## Completed Phases

### Phase 1: Project Setup
- [x] Create project structure (src/, tests/, data/, output/)
- [x] Create CLAUDE.md with governance framework and signal weights
- [x] Create config.py with signal weights and configuration
- [x] Generate specialist agents

### Phase 2: Connectors
- [x] Genesys connector (stub: `src/connectors/genesys_stub.py`)
- [x] HelpDesk connector (stub: `src/connectors/helpdesk_stub.py`)
- [x] UKG connector (stub: `src/connectors/ukg_stub.py`)
- [x] WCS connector (stub: `src/connectors/wcs_stub.py`)
- [x] Service Mix connector (live CSV: `src/connectors/service_mix.py`)
- [x] BEAD connector (live CSV: `src/connectors/bead_data.py`)
- [x] Connector registry in `src/connectors/__init__.py`

### Phase 3: Signal Scorers (8 signals)
- [x] volume_growth scorer (`src/signals/volume_growth.py`)
- [x] sla_degradation scorer (`src/signals/sla_degradation.py`)
- [x] service_concentration scorer (`src/signals/service_concentration.py`)
- [x] bead_exposure scorer (`src/signals/bead_exposure.py`)
- [x] utilization_headroom scorer (`src/signals/utilization_headroom.py`)
- [x] repeat_contacts scorer (`src/signals/repeat_contacts.py`)
- [x] contract_proximity scorer (`src/signals/contract_proximity.py`)
- [x] seasonal_volatility scorer (`src/signals/seasonal_volatility.py`)

### Phase 4: Scoring Engine
- [x] Composite scoring engine (`src/scoring/engine.py`)
- [x] Remediation recommender (`src/scoring/recommender.py`)

### Phase 5: Output Generation
- [x] Excel report generation (`src/output/report.py`)
- [x] Markdown summary generation (`src/output/summary.py`)

### Phase 6: Testing
- [x] Config tests (`tests/test_config.py`)
- [x] Connector tests (`tests/test_connectors.py`)
- [x] Scoring engine tests (`tests/test_engine.py`)
- [x] Output tests (`tests/test_output.py`)
- [x] Pipeline integration tests (`tests/test_pipeline.py`)
- [x] Recommender tests (`tests/test_recommender.py`)
- [x] Signal scorer tests (`tests/test_signals.py`)

### Phase 7: Integration
- [x] CLI entry point (`src/main.py` — run via `python -m src.main`)
- [x] End-to-end pipeline working
- [x] Reports generated to `output/`

## Review Remediation — Completed (2026-03-19)
- [x] Implemented NaN exclusion in compute_composite_score with missing_signals parameter
- [x] Switched all signal scorers from isinstance/math.isnan to pd.isna()
- [x] Decorrelated stub connector seeds (unique per connector via default_rng)
- [x] Renamed format → output_format in report.py
- [x] Removed dead connector_mode config field
- [x] Removed unused import sys
- [x] Fixed step numbering in main.py
- [x] Removed empty outputs/ directory
- [x] Fixed CLAUDE.md: scoring/ and output/ paths, connector swap location
- [x] Optimized _resolve_bead_status and _count_services with pre-built lookup dicts
- [x] Created per-project .claude/settings.local.json

## Remaining for Ops
- [ ] Replace stub connectors with live implementations (see STUB_REPLACEMENT_GUIDE.md)
- [ ] Tag v1.0.0 after confirming all fixes
- [ ] Add isolated unit tests for _build_bead_lookup and _build_service_count_lookup
- [ ] Add test for main() CLI argument parsing

## Verification
- [x] Directory structure matches CLAUDE.md
- [x] `python -m src.main` completes without errors
- [x] All 7 test files present and passing
- [x] Full `pytest tests/` run verified this session
- [x] No regressions introduced
