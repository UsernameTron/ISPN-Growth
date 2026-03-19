# Stub Replacement Guide

How to swap each stub connector for live data sources in the GCS Engine.

## Overview

All connectors implement the same interface: `get_data() -> pd.DataFrame`. To replace a stub with a live connector, create a new file (e.g., `genesys_live.py`) implementing the same class name and `get_data()` method, then update the import in `src/connectors/__init__.py`.

---

## Connector Replacement Table

| Stub File | Live Replacement | API / Source |
|-----------|------------------|--------------|
| `genesys_stub.py` | Genesys Cloud CX Platform API | OAuth2, REST API |
| `helpdesk_stub.py` | HelpDesk / ServiceNow / Zendesk API | API key auth, REST API |
| `ukg_stub.py` | UKG Pro Workforce Management API | OAuth2, REST API |
| `wcs_stub.py` | WCS Reporting API or CSV export | API key auth or CSV import |
| `service_mix.py` | Already reads CSV | Update `data/service_mix.csv` with real data |
| `bead_data.py` | Already reads CSV | Update `data/bead_status.csv` with real data |

---

## Detailed Replacement Instructions

### 1. Genesys Cloud CX (`genesys_stub.py`)

**API Endpoint:** Genesys Cloud CX Platform API v2

**Authentication:** OAuth2 client credentials flow
- Register an OAuth client in Genesys Cloud Admin > Integrations > OAuth
- Required scopes: `analytics:readonly`, `routing:readonly`
- Token endpoint: `POST https://login.{region}.pure.cloud/oauth/token`

**Key Endpoints:**
- `GET /api/v2/analytics/queues/observations` — real-time queue metrics
- `POST /api/v2/analytics/conversations/aggregates/query` — historical call volume and handle times

**Response Mapping:**

| API Field | DataFrame Column | Notes |
|-----------|-----------------|-------|
| `nOffered` (aggregated) | `monthly_call_volume` | Sum over 30-day window |
| Month-over-month delta | `volume_growth_rate` | Calculate from two consecutive periods |
| `nConnected / nOffered` | `answer_rate` | Ratio |
| `nAbandoned / nOffered` | `abandon_rate` | Ratio |
| `tHandle` (avg) | `avg_handle_time_sec` | Average across all conversations |
| `oServiceLevel` | `service_level_pct` | Service level percentage |
| FCR metric | `first_call_resolution` | May require custom attribute |

**Implementation Notes:**
- Use the `POST /analytics/conversations/aggregates/query` endpoint with `interval` set to a 30-day window
- Group by queue or routing attribute that maps to partner_id
- The partner_id mapping may require a lookup table (queue ID to partner ID)

---

### 2. HelpDesk Ticketing (`helpdesk_stub.py`)

**API Endpoint:** HelpDesk / ServiceNow / Zendesk REST API

**Authentication:** API key in header (`X-API-Key` or `Authorization: Bearer`)

**Key Endpoints (Zendesk example):**
- `GET /api/v2/search.json?query=type:ticket created>{start_date}` — ticket search
- `GET /api/v2/tickets/{id}.json` — individual ticket details

**Response Mapping:**

| API Field | DataFrame Column | Notes |
|-----------|-----------------|-------|
| Count of tickets | `monthly_ticket_volume` | Filter by partner org and date range |
| Month-over-month delta | `ticket_growth_rate` | Calculate from two consecutive periods |
| Tickets with `is_followup=true` / total | `repeat_contact_rate` | Ratio of repeat contacts |
| `solved_at - created_at` (avg) | `avg_resolution_hours` | Average resolution time |
| Most common `category` | `top_category` | Group by category, take mode |

**Implementation Notes:**
- Partner mapping via organization ID or custom field on tickets
- Use date range filters to pull 60-day window (current + previous for growth calculation)
- For repeat contact detection, check `via.source` or custom tags

---

### 3. UKG Workforce Management (`ukg_stub.py`)

**API Endpoint:** UKG Pro Workforce Management API

**Authentication:** OAuth2
- Client credentials grant
- Token endpoint varies by UKG deployment (cloud vs on-prem)

**Key Endpoints:**
- `GET /api/workforce/schedules` — scheduled shifts by team/department
- `GET /api/workforce/adherence` — schedule adherence metrics
- `GET /api/workforce/timecards` — actual hours worked

**Response Mapping:**

| API Field | DataFrame Column | Notes |
|-----------|-----------------|-------|
| Count of active agents | `agent_count` | Distinct employees with active schedules |
| Actual hours / scheduled hours | `utilization_rate` | Ratio (0.0 to 1.0) |
| Adherence percentage | `schedule_adherence` | From adherence endpoint |
| `agent_count * (1 - utilization_rate)` | `available_capacity` | Calculated field |

**Implementation Notes:**
- Map UKG departments/teams to partner_id via a lookup table
- Pull schedule data for the current week or rolling 2-week window
- Utilization rate should reflect productive time vs total scheduled time

---

### 4. WCS Contact Summary (`wcs_stub.py`)

**API Endpoint:** WCS Reporting API or manual CSV export

**Authentication:** API key authentication
- `GET /api/reports/weekly-contact-summary` — 13-week rolling window

**Alternative:** Export CSV from the WCS portal manually and place at `data/wcs_weekly.csv`

**Response Mapping:**

| API Field | DataFrame Column | Notes |
|-----------|-----------------|-------|
| Weekly contact counts (13 weeks) | `weekly_volumes` | List of 13 integers |
| `std(weekly) / mean(weekly)` | `seasonal_variance_coeff` | Coefficient of variation |

**Implementation Notes:**
- The key output is the coefficient of variation across 13 weeks
- If using CSV export, format should be: `partner_id, week_1, week_2, ..., week_13`
- Calculate CoV in the connector: `np.std(weeks) / np.mean(weeks)`

---

### 5. Service Mix (`service_mix.py`)

**Status:** Already reads from CSV. No API replacement needed.

**To update:**
1. Export the current partner service portfolio from your CRM or billing system
2. Format as CSV with columns: `partner_id, partner_name, services, contract_tier`
3. The `services` column should be a comma-separated list of service names
4. Save to `data/service_mix.csv`

**Example row:**
```
P001,Summit Broadband,"internet,voice,video",premium
```

---

### 6. BEAD Status (`bead_data.py`)

**Status:** Already reads from CSV. No API replacement needed.

**To update:**
1. Check the NTIA BEAD tracker (https://broadbandusa.ntia.gov/funding-programs/bead) for current state statuses
2. Format as CSV with columns: `state, status, partner_ids`
3. Status values: `none`, `approved`, `imminent`, `active`
4. `partner_ids` is a comma-separated list of partner IDs operating in that state
5. Save to `data/bead_status.csv`

**Example row:**
```
Texas,active,"P001,P005,P029"
```

---

## Swapping a Connector

1. Create the live connector file (e.g., `src/connectors/genesys_live.py`)
2. Implement the same class name with `get_data() -> pd.DataFrame`
3. Ensure the DataFrame has the same columns as the stub
4. Update the import in `src/connectors/__init__.py`:

```python
# Before
from src.connectors.genesys_stub import GenesysConnector

# After
from src.connectors.genesys_live import GenesysConnector
```

5. Run the test suite to verify: `pytest tests/`
6. Run the full pipeline: `python -m src.main`

No other code changes are required downstream.
