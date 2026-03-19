"""BEAD program exposure connector — reads state-level funding status from CSV.

Replace with: NTIA BEAD tracker API or manual data refresh
- Tracks Broadband Equity, Access, and Deployment program status by state
- Maps partners to states for exposure scoring
See STUB_REPLACEMENT_GUIDE.md for full API details.
"""
import os

import pandas as pd


class BEADConnector:
    """Reads BEAD program status data from data/bead_status.csv."""

    def __init__(self, csv_path: str | None = None) -> None:
        if csv_path is None:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            csv_path = os.path.join(base, "data", "bead_status.csv")
        self.csv_path = csv_path

    def get_data(self) -> pd.DataFrame:
        return pd.read_csv(self.csv_path)
