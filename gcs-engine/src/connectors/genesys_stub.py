"""Genesys Cloud CX connector stub.

Replace with: Genesys Cloud CX Platform API
- OAuth2 client credentials flow
- GET /api/v2/analytics/queues/observations
- GET /api/v2/analytics/conversations/aggregates
See STUB_REPLACEMENT_GUIDE.md for full API details.
"""
import numpy as np
import pandas as pd


class GenesysConnector:
    """Mock Genesys Cloud CX data. Returns call center metrics per partner."""

    def get_data(self) -> pd.DataFrame:
        rng = np.random.default_rng(42)
        n = 30
        partner_ids = [f"P{i:03d}" for i in range(1, n + 1)]

        # 10 growing, 10 stable, 10 declining
        growth_profiles = np.concatenate([
            rng.uniform(0.10, 0.25, 10),   # growing
            rng.uniform(-0.03, 0.05, 10),   # stable
            rng.uniform(-0.15, -0.03, 10),  # declining
        ])
        rng.shuffle(growth_profiles)

        base_volume = rng.integers(2000, 50000, n)

        return pd.DataFrame({
            "partner_id": partner_ids,
            "monthly_call_volume": base_volume,
            "volume_growth_rate": np.round(growth_profiles, 4),
            "answer_rate": np.round(rng.uniform(0.75, 0.98, n), 4),
            "abandon_rate": np.round(rng.uniform(0.02, 0.15, n), 4),
            "avg_handle_time_sec": rng.integers(180, 600, n),
            "first_call_resolution": np.round(rng.uniform(0.55, 0.90, n), 4),
            "service_level_pct": np.round(rng.uniform(0.60, 0.95, n), 4),
        })
