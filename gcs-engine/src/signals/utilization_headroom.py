"""Signal scorer: utilization headroom."""

import pandas as pd


def score_utilization_headroom(utilization_rate: float) -> int:
    """Score based on agent utilization rate. Lower util = more headroom for growth.

    Args:
        utilization_rate: Current utilization (e.g., 0.85 = 85% utilized).

    Returns:
        int 0-3: 0=no headroom, 1=tight, 2=moderate, 3=ample headroom.
    """
    if pd.isna(utilization_rate):
        return 0
    if utilization_rate >= 0.95:
        return 0
    elif utilization_rate >= 0.85:
        return 1
    elif utilization_rate >= 0.70:
        return 2
    else:
        return 3
