"""WCS weekly contact summary connector stub.

Replace with: WCS Reporting API
- API key authentication
- GET /api/reports/weekly-contact-summary
- Returns 13-week rolling window per partner
See STUB_REPLACEMENT_GUIDE.md for full API details.
"""
import numpy as np
import pandas as pd


class WCSConnector:
    """Mock WCS weekly contact summaries. Returns weekly volume patterns per partner."""

    def get_data(self) -> pd.DataFrame:
        rng = np.random.default_rng(789)
        n = 30
        weeks = 13
        partner_ids = [f"P{i:03d}" for i in range(1, n + 1)]

        rows = []
        for i in range(n):
            base = rng.integers(500, 5000)

            # 6 partners get high seasonality (CoV > 0.25)
            if i < 6:
                seasonal = np.sin(np.linspace(0, 2 * np.pi, weeks)) * base * 0.4
                noise = rng.normal(0, base * 0.05, weeks)
                weekly = np.maximum(base + seasonal + noise, 50).astype(int)
            else:
                noise = rng.normal(0, base * 0.08, weeks)
                weekly = np.maximum(base + noise, 50).astype(int)

            weekly_list = weekly.tolist()
            mean_vol = np.mean(weekly_list)
            std_vol = np.std(weekly_list)
            cov = round(std_vol / mean_vol, 4) if mean_vol > 0 else 0.0

            rows.append({
                "partner_id": partner_ids[i],
                "weekly_volumes": weekly_list,
                "seasonal_variance_coeff": cov,
            })

        return pd.DataFrame(rows)
