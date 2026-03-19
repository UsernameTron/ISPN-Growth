"""HelpDesk ticketing connector stub.

Replace with: HelpDesk/ServiceNow/Zendesk API
- REST API with API key authentication
- GET /api/v2/tickets with date range filters
- Aggregation by partner_id and category
See STUB_REPLACEMENT_GUIDE.md for full API details.
"""
import numpy as np
import pandas as pd


class HelpDeskConnector:
    """Mock HelpDesk ticketing data. Returns ticket metrics per partner."""

    def get_data(self) -> pd.DataFrame:
        rng = np.random.default_rng(123)
        n = 30
        partner_ids = [f"P{i:03d}" for i in range(1, n + 1)]

        # 10 growing, 10 stable, 10 declining ticket volumes
        growth_profiles = np.concatenate([
            rng.uniform(0.08, 0.20, 10),
            rng.uniform(-0.03, 0.05, 10),
            rng.uniform(-0.12, -0.02, 10),
        ])
        rng.shuffle(growth_profiles)

        categories = ["billing", "technical", "account", "service_change", "outage"]

        return pd.DataFrame({
            "partner_id": partner_ids,
            "monthly_ticket_volume": rng.integers(100, 5000, n),
            "ticket_growth_rate": np.round(growth_profiles, 4),
            "repeat_contact_rate": np.round(rng.uniform(0.05, 0.40, n), 4),
            "avg_resolution_hours": np.round(rng.uniform(1.0, 48.0, n), 1),
            "top_category": rng.choice(categories, n),
        })
