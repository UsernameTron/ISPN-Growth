"""Signal scorer: service concentration."""

import pandas as pd


def score_service_concentration(num_services: int | float) -> int:
    """Score based on number of services. Fewer services = higher upsell opportunity.

    Args:
        num_services: Count of distinct services a partner offers.

    Returns:
        int 0-3: 0=diversified (4+), 1=three, 2=two, 3=one (concentrated).
    """
    if pd.isna(num_services):
        return 0
    num_services = int(num_services)
    if num_services >= 4:
        return 0
    elif num_services == 3:
        return 1
    elif num_services == 2:
        return 2
    else:
        return 3
