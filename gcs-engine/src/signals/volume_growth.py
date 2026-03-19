"""Signal scorer: volume growth trend."""

import pandas as pd


def score_volume_growth(growth_rate: float) -> int:
    """Score volume growth trend. Higher growth = higher expansion opportunity.

    Args:
        growth_rate: Monthly call volume growth rate (e.g., 0.15 = 15%).

    Returns:
        int 0-3: 0=declining, 1=flat, 2=moderate growth, 3=strong growth.
    """
    if pd.isna(growth_rate):
        return 0
    if growth_rate < -0.03:
        return 0
    elif growth_rate < 0.05:
        return 1
    elif growth_rate <= 0.15:
        return 2
    else:
        return 3
