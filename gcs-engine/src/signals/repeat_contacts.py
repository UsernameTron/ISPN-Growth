"""Signal scorer: repeat contacts."""

import pandas as pd


def score_repeat_contacts(repeat_contact_rate: float) -> int:
    """Score based on repeat contact rate. Higher repeats = cross-sell opportunity.

    Args:
        repeat_contact_rate: Fraction of contacts that are repeats (e.g., 0.25 = 25%).

    Returns:
        int 0-3: 0=low, 1=moderate, 2=high, 3=very high.
    """
    if pd.isna(repeat_contact_rate):
        return 0
    if repeat_contact_rate < 0.10:
        return 0
    elif repeat_contact_rate <= 0.20:
        return 1
    elif repeat_contact_rate <= 0.30:
        return 2
    else:
        return 3
