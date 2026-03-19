"""Signal scorer: contract proximity."""

import pandas as pd


def score_contract_proximity(months_until_renewal: float) -> int:
    """Score based on months until contract renewal. Closer = more urgent.

    Args:
        months_until_renewal: Months remaining until contract renewal.

    Returns:
        int 0-3: 0=far (>12), 1=approaching (6-12), 2=near (3-6), 3=imminent (<3).
    """
    if pd.isna(months_until_renewal):
        return 0
    if months_until_renewal > 12:
        return 0
    elif months_until_renewal >= 6:
        return 1
    elif months_until_renewal >= 3:
        return 2
    else:
        return 3
