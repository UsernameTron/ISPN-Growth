# CLAUDE.md

You are operating under an agent governance framework. This file is your operating system. Follow every rule exactly.

---

## Session Initialization (Execute Every Time)

On every session start, execute this sequence before doing ANY work:

1. Read this file (`CLAUDE.md`) in full.
2. Read `tasks/lessons.md`. If it does not exist, create it from the template below.
3. Read `tasks/todo.md`. If a task is in progress, summarize its current state.
4. Report to user: "Session initialized. [N] active lessons loaded. [Current task status or 'No active task']."

Do not skip this sequence. Do not begin work before completing it.

---

## Commands

| Command | Purpose |
|---------|---------|
| `/prime` | Boot session — load context, check state, detect continuity |
| `/plan <request>` | Create implementation plan (auto-scales to complexity) |
| `/build <plan-path>` | Execute plan with git branches and step-by-step commits |
| `/status` | Dashboard — plans, sessions, git state, workspace health |
| `/wrap` | Close session — log work, note next steps, persist state |

---

## Operator Context

Load at session start (skip any that don't exist):

| File | Contains |
|------|----------|
| `context/role.md` | Operator's role, responsibilities, working style |
| `context/org.md` | Organization background, team structure |
| `context/priorities.md` | Current goals, success criteria, deadlines |
| `context/metrics.md` | Live metrics, KPIs, current state data |

Context files are private — never commit or echo their contents.

---

## Workflow Rules

### 1. Plan Before Building
- Enter plan mode for ANY task with 3+ steps or architectural decisions.
- Write a plan to `tasks/todo.md` with checkable items before writing code.
- If implementation deviates from the plan, **STOP**. Re-plan. Do not push through.
- Include verification steps in your plan, not just build steps.
- **Scope guard**: If a task grows beyond the original plan by more than 50% (new steps, new files, new dependencies), stop and re-plan with the user.

### 2. Use Subagents
- Offload research, exploration, and parallel analysis to subagents.
- One task per subagent. Keep the main context window clean.
- The orchestrating context synthesizes subagent results. Subagents do not make final decisions.
- **Efficiency rule**: Do not spawn subagents for tasks completable in under 2 minutes. Use subagents for tasks requiring exploration of multiple files, research, or parallel analysis.

### 3. Learn From Corrections
- After ANY correction from the user, immediately update `tasks/lessons.md` with:
  - What went wrong
  - The rule that prevents it from happening again
- Write the rule so it is actionable and specific, not vague.
- Review `tasks/lessons.md` at the start of every session before doing any work.

### 4. Prove It Works Before Saying Done
- Never mark a task complete without demonstrating correctness.
- Run tests. Check logs. Diff behavior between main and your changes.
- Quality checks (all must pass before marking done):
  - [ ] Linting passes with no new warnings
  - [ ] All existing tests still pass
  - [ ] New code paths have error handling
  - [ ] No TODO/FIXME/HACK comments left behind
  - [ ] Changes only touch what is necessary for the task
- If any check fails, you are not done.

### 5. Choose Elegance Over Expedience (When It Matters)
- For non-trivial changes: pause and evaluate whether a more elegant solution exists.
- If a fix feels hacky, step back and implement the clean solution.
- For simple, obvious fixes: skip this step. Do not over-engineer.

### 6. Track State
- After completing significant work, append to `state/session-log.md`. Log key decisions to `state/decisions.md`.
- Context is private — never commit files in `context/` or `state/`. Never echo their contents in outputs.
- Keep CLAUDE.md current — if you add commands, change structure, or modify workflows, update this file immediately.

### 7. Fix Bugs Autonomously
- When given a bug report: read the logs, identify the root cause, fix it.
- Do not ask clarifying questions if the error message or stack trace provides the answer.
- Do not ask the user how to fix it. Investigate and resolve.
- If CI tests are failing, go fix them without being told.

---

## Autonomy Decision Tree

Use this to determine when to act vs. when to ask:

```
Is this a bug fix with a clear error/stack trace?
  → YES: Act autonomously. Fix it. Report what you did.
  → NO: Continue ↓

Is this a feature, refactor, or architectural change?
  → YES: Write plan to todo.md. Present to user. Wait for confirmation.
  → NO: Continue ↓

Is this a minor cleanup (formatting, typo, dead code)?
  → YES: Act autonomously. Mention it in your summary.
  → NO: Continue ↓

Is the failure ambiguous (no clear root cause)?
  → YES: Investigate first. Present findings and proposed fix. Wait for confirmation.
  → NO: Default to asking.
```

When in doubt, investigate first, then present findings. Do not ask questions that you could answer by reading the code or logs.

---

## Git Workflow

Follow these rules for every code change:

### Branching
- Create a branch for every task: `feat/<task-name>`, `fix/<task-name>`, or `chore/<task-name>`.
- Never commit directly to `main` or `master`.
- Branch from the latest `main` unless instructed otherwise.

### Commits
- Write clear, imperative commit messages: "Add validation for email input" not "added stuff".
- One logical change per commit. Do not bundle unrelated changes.
- Keep commits small and reviewable.

### Before Pushing
- Run the full test suite.
- Ensure linting passes.
- Verify no untracked files are left behind.
- Review your own diff: `git diff --staged` before committing.

### Pull Requests
- If the project uses PRs, create one with a clear description of what changed and why.
- Link the PR to the task in `todo.md`.

---

## Rollback Protocol

If something goes wrong during implementation:

1. **Tests break unrelated to your change**: Stop immediately. Do not attempt to fix unrelated test failures by modifying tests. Run `git stash` or `git checkout -- .` to revert your changes. Re-plan.
2. **Build breaks**: Check if your change caused it. If yes, revert and fix. If no, flag to user.
3. **Unexpected side effects**: If your change causes behavior changes outside the intended scope, revert to last known good state and re-plan with a smaller blast radius.
4. **Partial completion**: If you must stop mid-task, commit working code to the branch, update `todo.md` with exactly where you stopped, and leave a clear handoff note.

The rule: **Never leave main in a broken state. Never push broken code.**

---

## Context Window & Session Management

Long tasks will exceed context limits. Manage this proactively:

### Checkpointing
- After completing each major step in a plan, write a brief status update to `tasks/todo.md`.
- Mark completed items. Note any decisions made or deviations from plan.
- This ensures the next session (or a fresh context) can pick up cleanly.

### Session Handoff
- If you detect context is getting long (many files read, extensive back-and-forth), proactively summarize the current state:
  - What has been completed
  - What remains
  - Any open decisions or blockers
- Write this summary to `tasks/todo.md` under a `## Session Handoff` section.

### Splitting Work
- If a task requires touching more than 5 files or involves more than 10 plan steps, consider whether it should be split into subtasks.
- Propose the split to the user rather than attempting everything in one session.

---

## Task Lifecycle

Execute this sequence for every task:

1. **Plan**: Write plan to `tasks/todo.md` with checkable items.
2. **Confirm**: Present the plan to the user before starting implementation.
3. **Execute**: Mark items complete in `tasks/todo.md` as you go. Checkpoint after each major step.
4. **Narrate**: Provide a high-level summary of what changed at each step.
5. **Verify**: Run all quality checks from Rule 4. Demonstrate results.
6. **Document**: Add a results/review section to `tasks/todo.md` when finished.
7. **Learn**: If the user corrects anything, update `tasks/lessons.md` immediately.

---

## Code Standards

These apply to every change you make:

- **Simplicity**: Make every change as simple as possible. Touch minimal code.
- **Root Causes**: Find and fix root causes. No temporary fixes. No band-aids.
- **Minimal Blast Radius**: Changes should only touch what is necessary. Do not introduce regressions.
- **Consistency**: Follow existing patterns in the codebase. Do not introduce new patterns without justification.
- **No Silent Failures**: Every error path must be handled explicitly.
- **No Orphaned Code**: Do not leave dead code, unused imports, or commented-out blocks.

---

## Rule Authority & Conflict Resolution

Rules come from three sources. When they conflict, apply this precedence:

1. **CLAUDE.md** (this file) — highest authority. Overrides everything.
2. **Project-Specific Rules** (bottom of this file) — second authority. Refine and extend CLAUDE.md.
3. **tasks/lessons.md** — third authority. Additive refinements from past corrections. If a lesson contradicts CLAUDE.md, CLAUDE.md wins.

### Decision Framework

When facing ambiguity, apply these in order:

1. Check this file for an applicable governance rule. If one exists, follow it.
2. Check Project-Specific Rules below. If one exists, follow it.
3. Check `tasks/lessons.md` for a relevant prior rule. If one exists, follow it.
4. Follow existing patterns in the codebase.
5. If still ambiguous, choose the simplest option and flag the assumption to the user.

Do not guess silently. If you make an assumption, state it.

---

## File Structure

Maintain this structure in the project root:

```
tasks/                   # Task tracking (committed)
├── todo.md              # Current task plan with checkable items
├── lessons.md           # Accumulated rules from past corrections
└── session-log.md       # Audit trail across sessions (optional)

context/                 # Private operator identity (gitignored)
├── role.md
├── org.md
├── priorities.md
└── metrics.md

state/                   # Session audit trail (gitignored)
├── session-log.md       # Chronological log of all sessions
└── decisions.md         # Design decision records

plans/                   # Implementation plans from /plan (gitignored)
outputs/                 # Deliverables and work products (gitignored)
decisions/               # Architecture Decision Records (committed)
```

**Note**: `tasks/` tracks the current task and correction rules. `state/` is a separate chronological audit trail across sessions. Both serve distinct purposes.

### tasks/todo.md Format
```markdown
# Current Task: [Task Name]
**Branch**: `feat/task-name`
**Started**: YYYY-MM-DD

## Plan
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Verification
- [ ] Linting passes
- [ ] All tests pass (command: `[specific test command]`)
- [ ] No regressions introduced
- [ ] Error handling on all new paths
- [ ] No TODO/FIXME left behind
- [ ] Diff reviewed: only intended files changed

## Results
<!-- Add after completion -->

## Session Handoff
<!-- Add if task spans multiple sessions -->
<!-- What is done, what remains, open decisions -->
```

### tasks/lessons.md Format
```markdown
# Lessons

## Active Rules

### Seed Rules (Pre-loaded)
- [YYYY-MM-DD] [Config]: Never modify shared configuration files without checking all downstream consumers first.
- [YYYY-MM-DD] [Scope]: If a "quick fix" requires touching more than 3 files, it is not a quick fix. Re-plan.
- [YYYY-MM-DD] [Testing]: Always run the full test suite, not just tests for the changed module. Cross-module regressions are common.
- [YYYY-MM-DD] [Dependencies]: Never add a new dependency without explicit user approval. Check if a built-in or existing dependency already solves the problem.
- [YYYY-MM-DD] [Data]: Never delete or overwrite production data, migration files, or seed data without explicit user approval.

### Learned Rules
<!-- Added during sessions when corrections occur -->

## Patterns
<!-- Recurring themes across multiple rules -->

## Archived
<!-- Rules that no longer apply -->
```

### tasks/session-log.md Format
```markdown
# Session Log

## [YYYY-MM-DD HH:MM] Session Start
- **Task**: [Task name or "No active task"]
- **Lessons loaded**: [N]
- **Actions taken**: [Brief summary]
- **Outcome**: [Completed / In progress / Blocked]
- **Handoff notes**: [If applicable]
```

---

## Do Not Touch List

Never modify these without explicit user approval:

- Production configuration files (`.env.production`, deployment configs)
- Migration files that have already been run
- CI/CD pipeline configurations
- Lock files (`package-lock.json`, `yarn.lock`) — except when adding approved dependencies
- Secrets, API keys, credentials of any kind

If a task requires modifying any of these, stop and ask.

---

## Project-Specific Rules

<!-- ═══════════════════════════════════════════════════════════════════════ -->
<!-- ROI Calculator — Full-Stack Web Application                            -->
<!-- ═══════════════════════════════════════════════════════════════════════ -->

### Architecture
- This is a **full-stack web application** — React+TypeScript (Vite) frontend + Python/FastAPI backend.
- No database (stateless calculations). No authentication (public calculator). No PII collection.
- Frontend serves from Vite dev server (port 5173), backend from uvicorn (port 8000).
- `api/` contains all Python/FastAPI code. `frontend/src/` contains all React/TypeScript code.

### ISPN Financial Constants
- Blended rate: $21.00
- Multiplier: 1.35x
- Utilization target: 60%
- Industry turnover: 35%
- Training ramp: 6 weeks
- After-hours premium: 1.5x (nights/weekends)
- Technology overhead: Genesys licensing estimate
- Management overhead: 15%
- QA/monitoring overhead: 8%

### Conventions
- TypeScript strict mode enabled.
- All monetary values use `Decimal` in Python, formatted as USD with commas.
- Percentages displayed to 1 decimal place.
- Pydantic models for ALL API request/response contracts.
- Recharts for data visualization.
- SkillResult typed response envelope for all API responses.
- Backend structure: app factory pattern, config module (`api/config.py`), middleware (`api/middleware/`).
- Frontend structure: BFF-aware fetch, typed API client (`frontend/src/utils/`, `frontend/src/types/`).

### Testing
- Backend: `pytest` (run from project root: `python -m pytest tests/ -v`)
- Frontend: `vitest` (run from project root: `npx vitest run`)
- BOTH must pass before marking any task complete.

### Boundaries
- Never hardcode ISPN constants — always reference from `api/config.py`.
- Never use `float` for monetary calculations — always `Decimal`.
- Never commit `.env` files or credentials.
