"""Signal scorer: seasonal volatility."""

import pandas as pd


def score_seasonal_volatility(coefficient_of_variation: float) -> int:
    """Score based on coefficient of variation of weekly volumes.

    Args:
        coefficient_of_variation: std / mean of weekly volumes.

    Returns:
        int 0-3: 0=stable, 1=mild, 2=moderate, 3=high volatility.
    """
    if pd.isna(coefficient_of_variation):
        return 0
    if coefficient_of_variation < 0.10:
        return 0
    elif coefficient_of_variation < 0.15:
        return 1
    elif coefficient_of_variation < 0.25:
        return 2
    else:
        return 3
