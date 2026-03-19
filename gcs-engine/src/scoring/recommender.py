"""Expansion play recommender — maps signal patterns to action recommendations."""


def recommend_play(signal_scores: dict[str, int], composite_score: float) -> str:
    """Map signal pattern to expansion play recommendation.

    Rules are checked in priority order (first match wins).

    Args:
        signal_scores: Dict mapping signal name to score (0-3).
        composite_score: Weighted composite score (0-100).

    Returns:
        Recommended expansion play string.
    """
    vg = signal_scores.get("volume_growth", 0)
    sc = signal_scores.get("service_concentration", 0)
    sla = signal_scores.get("sla_degradation", 0)
    uh = signal_scores.get("utilization_headroom", 0)
    bead = signal_scores.get("bead_exposure", 0)
    sv = signal_scores.get("seasonal_volatility", 0)
    rc = signal_scores.get("repeat_contacts", 0)

    # Priority 1: Volume growth + concentrated services -> upsell
    if vg >= 2 and sc >= 2:
        return "Service tier upgrade"

    # Priority 2: SLA degradation + capacity available -> expand
    if sla >= 2 and uh >= 2:
        return "Capacity expansion"

    # Priority 3: BEAD exposure + some growth -> BEAD package
    if bead >= 2 and vg >= 1:
        return "BEAD preparation package"

    # Priority 4: Seasonal volatility + some headroom -> flex staffing
    if sv >= 2 and uh >= 1:
        return "Flex/seasonal staffing"

    # Priority 5: High repeat contacts -> cross-sell
    if rc >= 2:
        return "L2/L3 or NOC cross-sell"

    # Default
    return "General expansion conversation"
