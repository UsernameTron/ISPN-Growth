"""Signal scorer: SLA degradation."""

import pandas as pd


def score_sla_degradation(service_level: float) -> int:
    """Score based on service level percentage. Lower SL = higher opportunity.

    Args:
        service_level: Service level percentage (e.g., 0.85 = 85%).

    Returns:
        int 0-3: 0=stable, 1=slight decline, 2=at risk, 3=breached.
    """
    if pd.isna(service_level):
        return 0
    if service_level >= 0.90:
        return 0
    elif service_level >= 0.80:
        return 1
    elif service_level >= 0.70:
        return 2
    else:
        return 3
