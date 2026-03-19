"""UKG workforce management connector stub.

Replace with: UKG Pro Workforce Management API
- OAuth2 authentication
- GET /api/workforce/schedules
- GET /api/workforce/adherence
See STUB_REPLACEMENT_GUIDE.md for full API details.
"""
import numpy as np
import pandas as pd


class UKGConnector:
    """Mock UKG workforce data. Returns staffing metrics per partner."""

    def get_data(self) -> pd.DataFrame:
        rng = np.random.default_rng(456)
        n = 30
        partner_ids = [f"P{i:03d}" for i in range(1, n + 1)]

        agent_count = rng.integers(5, 200, n)
        utilization_rate = np.round(rng.uniform(0.50, 0.95, n), 4)
        available_capacity = np.round(agent_count * (1 - utilization_rate), 1)

        return pd.DataFrame({
            "partner_id": partner_ids,
            "agent_count": agent_count,
            "utilization_rate": utilization_rate,
            "schedule_adherence": np.round(rng.uniform(0.70, 0.98, n), 4),
            "available_capacity": available_capacity,
        })
