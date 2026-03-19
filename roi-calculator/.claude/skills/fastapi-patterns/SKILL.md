---
name: fastapi-patterns
description: |
  ISPN FastAPI patterns reference for the ROI Calculator backend.
  Provides app factory, Pydantic models, middleware, skill wrapper pattern,
  dependency injection, and response caching patterns. Auto-loaded by
  backend specialist agents.
user-invocable: false
---

<!-- Content sourced from Claude MCP Ecosystem: subagent-lifecycle/references/ispn/fastapi-patterns.md -->
<!-- See that file for the full reference. Key patterns used in this project: -->

## Key Patterns for ROI Calculator

### App Factory (api/main.py)
- Use `create_app()` factory pattern
- CORS middleware for frontend dev server (localhost:5173)
- Request logging middleware
- Global error handler

### Pydantic Models
- All request inputs validated via Pydantic BaseModel
- All responses use typed response envelope (CostBreakdown, ROICalculationResponse)
- Use `Decimal` for monetary values, never `float`

### Configuration
- Use `pydantic-settings` for environment-based config
- ISPN constants in `api/config.py` (blended rate, multiplier, etc.)
- Never hardcode financial constants in business logic

### Testing
- Use `pytest` with `httpx.AsyncClient` for API tests
- Test edge cases: zero inputs, negative margins, very large subscriber counts
- Verify all monetary outputs are properly rounded

### Requirements
- Pin major versions: `>=X.Y.0,<X+1.0.0`
- Separate dev deps in `requirements-dev.txt`
