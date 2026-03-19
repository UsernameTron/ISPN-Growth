Context
Two greenfield projects (roi-calculator and gcs-engine) are being prepared for handoff to development operations. Both have been scaffolded with real implementations but need structural cleanup, documentation accuracy fixes, and gap identification before ops teams add live endpoints. This review expects stubs for TBD items and focuses on structural readiness.

Review Summary
ProjectCriticalWarningInfoStubs PresentTestsROI Calculator5990 (all real code)Backend only (8 classes), no frontend testsGCS Engine3894 connectors (by design)Comprehensive (7 test files)Cross-Project024——

ROI Calculator — Issues
Critical (must fix before handoff)

No Dockerfile — docker-compose.yml references build: context: . but no Dockerfile exists. docker-compose build will fail.

File: roi-calculator/docker-compose.yml


datetime.utcnow() deprecated (Python 3.12+) — Will emit deprecation warnings.

File: roi-calculator/api/models/responses.py:31
Fix: datetime.now(timezone.utc)


float used for monetary fields — CLAUDE.md mandates Decimal for money. Request model uses float for avg_hourly_wage and turnover_rate; response model uses float for all cost fields.

Files: api/models/requests.py:12,20, api/models/responses.py:11-17


Test runner will fail — No conftest.py, no pyproject.toml. CLAUDE.md says cd api && pytest but that breaks from api.models... imports.

File: roi-calculator/ (missing conftest.py or pyproject.toml)


Docker Compose uses deprecated version key — Minor but generates warnings on modern Docker.

Warnings (should fix)

CLAUDE.md says frontend is in src/ — actual path is frontend/src/. Will confuse agents and developers.

File: roi-calculator/CLAUDE.md:349


No frontend test infrastructure at all — No vitest dependency, no test script in package.json, no test files. CLAUDE.md requires npx vitest run.
node_modules/ never installed — npm install was never run in frontend/.
Missing middleware files — Plan calls for api/middleware/logging.py and error_handler.py. Only __init__.py exists.
After-hours cost may overstate — Applies full 1.5x premium instead of the 0.5x extra cost. Business intent should be verified.

File: api/services/cost_model.py:43


Breakeven search assumption undocumented — Varies subscriber count but holds in-house costs constant. May be intentional but needs a docstring clarification.

File: api/services/cost_model.py:111-144


Negative savings display bug — ComparisonView.tsx always shows "+" prefix, producing +-$5,000 when ISPN is more expensive.

File: frontend/src/components/ComparisonView.tsx:91


httpx/pytest-asyncio listed but unused — No API integration tests exist yet.
Docker Compose has no frontend service — Only backend defined.

Tests NOT Performed (ROI)

No API integration tests (POST /api/calculate via TestClient)
No input validation edge cases (negative numbers, zero, extreme values)
No error response testing
No frontend component tests
No end-to-end browser tests
Phase 5 verification checklist entirely unexecuted (5 ISP profiles, breakeven verification, mobile responsive, PDF download)


GCS Engine — Issues
Critical (must fix before handoff)

NaN exclusion not implemented — Docstring in compute_composite_score promises NaN-sourced signals are excluded from weighted sums, but the code has no way to distinguish NaN-sourced zeros from legitimate zeros. Partners with missing data are penalized.

File: gcs-engine/src/scoring/engine.py:42-71
Fix: Add a missing_signals: set[str] parameter or use a sentinel value.


CLAUDE.md file structure wrong — Documents src/scorers/ and src/reporters/ but actual dirs are src/scoring/ and src/output/.

File: gcs-engine/CLAUDE.md:262-263


Fragile NaN type checking — isinstance(val, float) works for np.float64 in CPython (subclass relationship) but is not guaranteed. Should use pd.isna() or math.isnan() with a type guard.

Files: All 8 signal scorer files in src/signals/



Warnings (should fix)

All stubs share np.random.seed(42) — Correlated random sequences across connectors. Should use np.random.default_rng() with different seeds per connector.

Files: All 4 stub connectors in src/connectors/


CLAUDE.md vs STUB_REPLACEMENT_GUIDE.md contradict on swap location — CLAUDE.md says swap in src/config.py; guide correctly says src/connectors/__init__.py.

File: gcs-engine/CLAUDE.md:374


format parameter shadows Python builtin — generate_report(format: str) should be output_format or fmt.

File: src/output/report.py:225


config.connector_mode defined but never read — Dead config field.

File: src/config.py:43


O(n*m) complexity in _resolve_bead_status and _count_services — Fine for 30 partners, won't scale. Pre-build lookup dicts.

File: src/scoring/engine.py:112-134


Unused import sys in main.py — Dead import.

File: src/main.py:8


Step numbering inconsistency — Print says "Step 3", comment says "Step 4".

File: src/main.py:71-72


outputs/ vs output/ directory duplication — Template artifact. Remove empty outputs/.

Stubs Present (by design — ready for ops handoff)
Stub ConnectorLive Data SourceDocumented in STUB_REPLACEMENT_GUIDE.mdgenesys_stub.pyGenesys Cloud CX APIYes — needs queue stats, agent performancehelpdesk_stub.pyHelpDesk ticket systemYes — needs ticket volumes, escalation ratesukg_stub.pyUKG workforce systemYes — needs attendance, utilizationwcs_stub.pyWeekly Call StatisticsYes — needs call volumes, trends
Two connectors already read real CSV data: service_mix.py and bead_data.py.
Tests NOT Performed (GCS)

No isolated unit tests for _resolve_bead_status or _count_services
No test for main() CLI argument parsing
No test for NaN exclusion behavior (because it's not implemented)
No integration test against live data sources (expected — stubs by design)


Cross-Project Issues

Both tasks/todo.md files are stale — Frozen at "Project Setup" despite 4-6 commits of completed work. Useless for session continuity.
settings.local.json scoped to parent dir — Pre-allows GCS-specific commands (python -m src.main) but not ROI commands (uvicorn). Should be per-project.
No .gitignore in ROI calculator — context/, state/, node_modules/ would be committed.
Master planning doc has no progress tracking — Reads as aspirational with no status indicators.
Neither project tagged v1.0.0 — ROI is not ready (too many gaps). GCS could be tagged after fixes.


Infrastructure Assets Available
Two directories in ISPN Growth/ contain reusable Claude Code infrastructure that can accelerate the fix process:
1. Claude MCP Ecosystem (Claude MCP Ecosystem copy/)
What it is: A subagent lifecycle suite — a framework for organizing Claude Code into specialist agent teams. Contains 5 pipeline agents, 3 orchestration skills, 7 project templates, and 12 ISPN-specific reference docs.
What's useful for this plan:
AssetLocationHow It Helpsweb-app.yaml templatesubagent-lifecycle/templates/web-app.yamlPre-built blueprint for React+FastAPI projects — matches ROI Calculator's architecture exactly. Defines 4 specialist agents (frontend, api, auth, tester) with correct tools and routing.data-dashboard.yaml templatesubagent-lifecycle/templates/data-dashboard.yamlBlueprint for pandas/data pipeline projects — close match for GCS Engine. Defines data-processing + visualization agents.fastapi-patterns.md referencesubagent-lifecycle/references/ispn/fastapi-patterns.mdApp factory patterns, middleware, models, caching — directly addresses ROI's missing middleware (Issue #9) and test setup (Issue #4).react-patterns.md referencesubagent-lifecycle/references/ispn/react-patterns.mdComponent patterns, BFF fetch — informs frontend test strategy for ROI.api-testing.md referencesubagent-lifecycle/references/ispn/api-testing.mdpytest patterns, TestClient usage, promotion gates — addresses ROI's missing API integration tests.docker-kubernetes.md referencesubagent-lifecycle/references/ispn/docker-kubernetes.mdDockerfile templates, docker-compose patterns — directly addresses ROI's missing Dockerfile (Critical #1).logging-observability.md referencesubagent-lifecycle/references/ispn/logging-observability.mdJSON logging, middleware patterns — addresses ROI's missing logging middleware (Issue #9).Governance framework (CLAUDE.md)Root CLAUDE.mdSession workflow (/prime, /plan, /build, /wrap), task tracking, rollback protocol — can be adapted to fix both project CLAUDE.md files.subagent-concierge skillsubagent-lifecycle/skills/subagent-concierge/Can auto-generate specialist agents for both projects using the templates above. Saves manual agent creation.validator agentsubagent-lifecycle/agents/validator.mdPost-fix quality gate — validates agent files, CLAUDE.md structure, ecosystem coherence. Run after all fixes to verify handoff readiness.
How to leverage for this plan:

Use docker-kubernetes.md as the Dockerfile template for ROI (Phase 3)
Use fastapi-patterns.md + api-testing.md to scaffold ROI's missing middleware and test setup (Phase 2-3)
Use the governance CLAUDE.md as a reference when fixing both project CLAUDE.md files (Phase 1)
Optionally run subagent-concierge against each project to generate specialist agents for ongoing development

2. Claude Code Factory (claude-code-factory copy/)
What it is: A distributable Claude Code plugin with two factory systems: an Extension Factory (generates skills, hooks, settings, plugins, CI/CD) and a Dev Team Factory (generates development agents from 72 archetypes across 10 domains).
What's useful for this plan:
AssetLocationHow It Helpsagent-factory skillskills/agent-factory/Generates agent .md files from 72 pre-built archetypes with correct frontmatter. Can create per-project specialist agents (tester, api-builder, data-pipeline) in seconds.team-configurator skillskills/team-configurator/Auto-detects tech stacks from 25+ config file types, then recommends and assembles optimal agent teams. Run against each project to get tailored team recommendations.stack-analyzer agentagents/stack-analyzer.mdHaiku-powered fast stack detection. Can confirm both projects' tech stacks and flag mismatches between detected stack and CLAUDE.md documentation.extension-validator agentagents/extension-validator.mdValidates all Claude Code extensions (skills, hooks, agents, settings) for structural correctness. Run as quality gate after fixes.settings-architect skillskills/settings-architect/Generates correct settings.json files from natural language. Can create proper per-project settings files (Cross-Project Issue #2).hook-factory skillskills/hook-factory/Generates hook configurations. Can create pre-commit hooks, test runners, and lint-on-save hooks for both projects.cc-ref-* reference skills (11)skills/cc-ref-*/Authoritative Claude Code documentation for settings, permissions, hooks, skills, plugins, agents. Ensures all fixes comply with current Claude Code spec.dev-recipes skillskills/dev-recipes/86 pre-built agent recipes. Includes recipes for: Python test runner, FastAPI developer, React component builder, data pipeline operator — all directly applicable.72 agent archetypesskills/cc-ref-agent-archetypes/Pre-built system prompts for agents across 10 domains. Relevant archetypes: api-developer, test-engineer, data-pipeline-engineer, devops-engineer.
How to leverage for this plan:

Run settings-architect to generate proper per-project settings.local.json files (Phase 5)
Run team-configurator against each project to get recommended agent teams for ongoing development
Use agent-factory with relevant archetypes to generate specialist agents for each project
Run extension-validator as a final quality gate after all fixes
Use dev-recipes to find and deploy pre-built agent configurations for testing and API development

Recommended Sequence for Using Infrastructure
Step 1 (Before fixes):
  - Run stack-analyzer against both projects to confirm tech stacks
  - Reference docker-kubernetes.md + fastapi-patterns.md for fix templates

Step 2 (During fixes):
  - Use ISPN reference docs as implementation guides for each fix phase
  - Use settings-architect to generate per-project settings files

Step 3 (After fixes):
  - Run extension-validator as quality gate
  - Run team-configurator to recommend agent teams for ops handoff
  - Use agent-factory to generate recommended agents
  - Run validator from MCP Ecosystem to verify ecosystem coherence

Step 4 (Handoff):
  - Ops team gets: fixed codebase + specialist agents + reference docs
  - Agents guide ops through endpoint additions using reference patterns

Parallel Execution Strategy
Agent Roster
AgentTypeModelOwned FilesPurposeroi-backend-fixergeneral-purposesonnetroi-calculator/api/**, roi-calculator/Dockerfile, roi-calculator/.gitignore, roi-calculator/docker-compose.ymlAll ROI backend critical + infra fixesroi-frontend-fixergeneral-purposesonnetroi-calculator/frontend/**Frontend bug fix, npm install, vitest setuproi-docs-fixergeneral-purposesonnetroi-calculator/CLAUDE.md, roi-calculator/tasks/todo.mdROI documentation accuracygcs-scoring-fixergeneral-purposesonnetgcs-engine/src/scoring/**, gcs-engine/src/signals/**NaN exclusion + pd.isna() migrationgcs-quality-fixergeneral-purposesonnetgcs-engine/src/connectors/**, gcs-engine/src/output/**, gcs-engine/src/main.py, gcs-engine/src/config.pyCode quality: seeds, dead code, renamesgcs-docs-fixergeneral-purposesonnetgcs-engine/CLAUDE.md, gcs-engine/tasks/todo.mdGCS documentation accuracysettings-generatorgeneral-purposesonnetroi-calculator/.claude/, gcs-engine/.claude/Per-project settings.local.json filesroi-verifiergeneral-purposesonnet(read-only)Post-fix verification for ROIgcs-verifiergeneral-purposesonnet(read-only)Post-fix verification for GCS

Wave 1 — All Fixes (7 agents in parallel)
Launch all 7 simultaneously. No agent touches another's files.
Agent 1: roi-backend-fixer
Files: roi-calculator/api/**, Dockerfile, .gitignore, docker-compose.yml

 Replace datetime.utcnow() → datetime.now(timezone.utc) in api/models/responses.py:31
 Convert float → Decimal for monetary fields in api/models/requests.py:12,20 and api/models/responses.py:11-17
 Create Dockerfile (reference: Claude MCP Ecosystem copy/subagent-lifecycle/references/ispn/docker-kubernetes.md)
 Create conftest.py or pyproject.toml for test discovery
 Remove deprecated version key from docker-compose.yml
 Create .gitignore (exclude: context/, state/, node_modules/, __pycache__/, .env)
 Add docstring to api/services/cost_model.py:111-144 documenting breakeven assumptions
 Add comment to api/services/cost_model.py:43 noting after-hours premium is intentional 1.5x (or fix to 0.5x extra — verify with user)

Agent 2: roi-frontend-fixer
Files: roi-calculator/frontend/**

 Fix negative savings display in ComparisonView.tsx:91 — use conditional prefix logic
 Run npm install in frontend/
 Add vitest + @testing-library/react to package.json devDependencies
 Add "test": "vitest run" script to package.json
 Create one smoke test for ComparisonView.tsx

Agent 3: roi-docs-fixer
Files: roi-calculator/CLAUDE.md, roi-calculator/tasks/todo.md

 Fix path reference: src/ → frontend/src/ at line ~349
 Update test commands to match actual project structure
 Update tasks/todo.md to reflect completed work (not frozen at "Project Setup")
 Verify all file path references in CLAUDE.md match actual filesystem

Agent 4: gcs-scoring-fixer
Files: gcs-engine/src/scoring/**, gcs-engine/src/signals/**

 Implement NaN exclusion in compute_composite_score (src/scoring/engine.py:42-71)

Add missing_signals: set[str] tracking
Exclude NaN-sourced signals from weighted sum denominator
Add unit test for NaN exclusion behavior


 Replace isinstance(val, float) with pd.isna() across all 8 signal scorers in src/signals/
 Pre-build lookup dicts for _resolve_bead_status and _count_services (engine.py:112-134)

Agent 5: gcs-quality-fixer
Files: gcs-engine/src/connectors/**, src/output/**, src/main.py, src/config.py

 Replace np.random.seed(42) with np.random.default_rng(seed) using per-connector seeds in all 4 stub connectors
 Rename format → output_format in src/output/report.py:225 and all callers
 Remove dead connector_mode from src/config.py:43
 Remove unused import sys from src/main.py:8
 Fix step numbering in src/main.py:71-72
 Remove empty outputs/ directory if it exists

Agent 6: gcs-docs-fixer
Files: gcs-engine/CLAUDE.md, gcs-engine/tasks/todo.md

 Fix src/scorers/ → src/scoring/ and src/reporters/ → src/output/ at lines ~262-263
 Fix connector swap location: src/config.py → src/connectors/__init__.py at line ~374
 Update tasks/todo.md to reflect completed work
 Verify all file path references match actual filesystem

Agent 7: settings-generator
Files: roi-calculator/.claude/, gcs-engine/.claude/

 Create roi-calculator/.claude/settings.local.json with ROI-specific commands (uvicorn, pytest, npm)
 Create gcs-engine/.claude/settings.local.json with GCS-specific commands (python -m src.main, pytest)
 Reference: Claude MCP Ecosystem copy/subagent-lifecycle/references/ispn/ for pattern guidance


Wave 2 — Verification (2 agents in parallel)
Launch after all Wave 1 agents complete. Read-only verification.
Agent 8: roi-verifier
Checklist:

 datetime.now(timezone.utc) in responses.py — no utcnow remaining
 Decimal types in requests.py and responses.py — no float for money
 Dockerfile exists and is syntactically valid
 docker-compose.yml has no version key
 .gitignore exists with correct exclusions
 conftest.py or pyproject.toml enables cd api && pytest to work
 frontend/node_modules/ exists
 vitest in package.json devDependencies
 At least one .test.tsx file exists
 CLAUDE.md path references match filesystem
 tasks/todo.md reflects actual progress
 ComparisonView.tsx handles negative savings correctly
 settings.local.json exists in .claude/

Agent 9: gcs-verifier
Checklist:

 compute_composite_score excludes NaN-sourced signals from weighted sum
 No isinstance(val, float) for NaN checks — all use pd.isna()
 All stub connectors use np.random.default_rng() with unique seeds
 No format parameter name in report.py — uses output_format
 No connector_mode in config.py
 No import sys in main.py
 Step numbering consistent in main.py
 No empty outputs/ directory
 CLAUDE.md references src/scoring/ and src/output/ (not scorers/reporters)
 CLAUDE.md connector swap points to src/connectors/__init__.py
 tasks/todo.md reflects actual progress
 settings.local.json exists in .claude/


Wave 3 — Final Quality Gate (1 agent)
Launch after Wave 2 confirms all fixes.

 Run extension-validator against both projects' .claude/ directories
 Generate summary report of all fixes applied + remaining deferred items


File Ownership Map (Conflict Prevention)
No two Wave 1 agents share any file. Cross-project agents (settings-generator) only touch .claude/ dirs which no other agent modifies.
roi-backend-fixer:   roi-calculator/api/**, Dockerfile, .gitignore, docker-compose.yml
roi-frontend-fixer:  roi-calculator/frontend/**
roi-docs-fixer:      roi-calculator/CLAUDE.md, roi-calculator/tasks/todo.md
gcs-scoring-fixer:   gcs-engine/src/scoring/**, gcs-engine/src/signals/**
gcs-quality-fixer:   gcs-engine/src/connectors/**, src/output/**, src/main.py, src/config.py
gcs-docs-fixer:      gcs-engine/CLAUDE.md, gcs-engine/tasks/todo.md
settings-generator:  roi-calculator/.claude/, gcs-engine/.claude/
Dependencies

Wave 2 starts only after ALL Wave 1 agents complete
Wave 3 starts only after Wave 2 confirms all fixes
Within Wave 1: all 7 agents are fully independent

Risk Mitigation
RiskMitigationFile conflict between agentsStrict ownership map — no shared filesnpm install network failureroi-frontend-fixer retries once; if still failing, agent reports and continues with other tasksNaN exclusion complexitygcs-scoring-fixer adds test first (TDD), then implements — verifier confirmsDecimal conversion breaks serializationroi-backend-fixer updates Pydantic model serializers to handle Decimal→float for JSON outputoutput_format rename misses callersgcs-quality-fixer uses grep to find ALL format references before renaming
Wall-Clock Time Estimate
ApproachEstimated DurationSequential (Phase 1→5)~25-30 minutesParallel (Wave 1→2→3)~8-10 minutes
Deferred Items (Ops Handles Post-Handoff)

ROI: Middleware stubs (logging.py, error_handler.py)
ROI: PDF export, deploy config, mobile polish
ROI: API integration tests (POST /api/calculate via TestClient)
ROI: Frontend service in docker-compose
GCS: Integration tests against live data sources
Master planning doc progress tracking
Git tagging (GCS v1.0.0 after verification)


What Ops Needs to Know
GCS Engine is structurally sound and nearly handoff-ready. The 4 stub connectors are clearly documented in STUB_REPLACEMENT_GUIDE.md with exact DataFrame schemas. Ops needs to:

Fix NaN exclusion (Critical #1) before trusting composite scores
Replace stubs one at a time following the guide
Run python -m pytest tests/ -v after each connector swap

ROI Calculator has a working calculation engine but infrastructure gaps (no Dockerfile, no frontend tests, stale docs). Ops needs to:

Fix test runner setup before adding endpoints
Create Dockerfile for deployment
The financial model is solid — endpoints can be added to api/routers/ following the existing calculate.py pattern