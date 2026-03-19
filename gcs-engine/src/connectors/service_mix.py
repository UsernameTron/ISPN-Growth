"""Service mix connector — reads partner service portfolio from CSV.

Replace with: CRM or billing system API
- Query partner service subscriptions
- Map to standardized service categories
See STUB_REPLACEMENT_GUIDE.md for full API details.
"""
import os

import pandas as pd


class ServiceMixConnector:
    """Reads service mix data from data/service_mix.csv."""

    def __init__(self, csv_path: str | None = None) -> None:
        if csv_path is None:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            csv_path = os.path.join(base, "data", "service_mix.csv")
        self.csv_path = csv_path

    def get_data(self) -> pd.DataFrame:
        return pd.read_csv(self.csv_path)
