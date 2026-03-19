"""Signal scorer: BEAD program exposure."""


def score_bead_exposure(bead_status: str) -> int:
    """Score based on BEAD program funding status.

    Args:
        bead_status: One of "none", "approved", "imminent", "active".

    Returns:
        int 0-3: 0=none, 1=approved, 2=imminent, 3=active.
    """
    if not isinstance(bead_status, str) or not bead_status:
        return 0
    status_map = {
        "none": 0,
        "approved": 1,
        "imminent": 2,
        "active": 3,
    }
    return status_map.get(bead_status.lower().strip(), 0)
