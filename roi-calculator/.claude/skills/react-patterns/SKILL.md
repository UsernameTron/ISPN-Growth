---
name: react-patterns
description: |
  ISPN React patterns reference for the ROI Calculator frontend.
  Provides project structure, BFF-aware API client, data fetching hooks,
  component templates, and TypeScript types matching Pydantic models.
  Auto-loaded by frontend specialist agents.
user-invocable: false
---

<!-- Content sourced from Claude MCP Ecosystem: subagent-lifecycle/references/ispn/react-patterns.md -->

## Key Patterns for ROI Calculator

### Project Structure
```
frontend/src/
├── api/client.ts          # BFF-aware fetch client
├── components/
│   ├── common/            # Shared: LoadingSpinner, ErrorBanner
│   └── calculator/        # InputForm, ComparisonView, Recommendation
├── hooks/
│   └── useCalculator.ts   # ROI calculation hook
├── types/api.ts           # TypeScript types matching Pydantic models
└── styles/theme.css       # ISPN branded styles
```

### API Client (BFF-Aware Fetch)
- Base URL from `VITE_API_BASE` env var (default: `/api`)
- Include credentials for auth cookies
- Typed `ApiResponse<T>` wrapper matching backend response envelope
- Centralized error handling

### TypeScript Types
- Mirror Pydantic models exactly:
  - `ROICalculationRequest` matches `api/models/requests.py`
  - `CostBreakdown`, `ROICalculationResponse` matches `api/models/responses.py`
- Never use `any` — all API responses fully typed

### Component Patterns
- Controlled form components with validation
- Loading/error/success states for all API calls
- Responsive layout using CSS Grid/Flexbox
- Recharts for data visualization (bar chart, comparison)

### Conventions
- TypeScript strict mode
- USD formatting: `new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })`
- Percentages: `value.toFixed(1) + '%'`
