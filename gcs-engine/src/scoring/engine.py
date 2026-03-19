"""Composite scoring engine — computes weighted GCS for all partners."""

import pandas as pd

from src.config import config
from src.signals import (
    score_volume_growth,
    score_sla_degradation,
    score_service_concentration,
    score_bead_exposure,
    score_utilization_headroom,
    score_repeat_contacts,
    score_contract_proximity,
    score_seasonal_volatility,
)


def compute_signal_scores(partner_data: dict) -> dict[str, int]:
    """Compute all 8 signal scores for a single partner.

    Args:
        partner_data: Dict with keys matching connector column names.

    Returns:
        Dict mapping signal name to score (0-3).
    """
    return {
        "volume_growth": score_volume_growth(partner_data.get("volume_growth_rate", float("nan"))),
        "sla_degradation": score_sla_degradation(partner_data.get("service_level_pct", float("nan"))),
        "service_concentration": score_service_concentration(partner_data.get("num_services", float("nan"))),
        "bead_exposure": score_bead_exposure(partner_data.get("bead_status", "")),
        "utilization_headroom": score_utilization_headroom(partner_data.get("utilization_rate", float("nan"))),
        "repeat_contacts": score_repeat_contacts(partner_data.get("repeat_contact_rate", float("nan"))),
        "contract_proximity": score_contract_proximity(partner_data.get("months_until_renewal", float("nan"))),
        "seasonal_volatility": score_seasonal_volatility(partner_data.get("seasonal_variance_coeff", float("nan"))),
    }


def compute_composite_score(
    signal_scores: dict[str, int],
    missing_signals: set[str] | None = None,
) -> float:
    """Weighted sum of signal scores, normalized to 0-100.

    Signals with NaN inputs (scored as 0) where the original data was missing
    are excluded from the weighted sum — the remaining weights are rescaled.

    Args:
        signal_scores: Dict mapping signal name to score (0-3).
        missing_signals: Set of signal names whose source data was missing/NaN.
            These signals are excluded from the weighted sum so that NaN-sourced
            zeros do not drag down the composite score.

    Returns:
        Composite score in range 0-100.
    """
    weight_map = {sw.name: sw.weight for sw in config.signal_weights}
    max_signal = config.signal_max

    weighted_sum = 0.0
    total_weight = 0.0

    for name, score in signal_scores.items():
        w = weight_map.get(name, 0.0)
        if w <= 0:
            continue
        if missing_signals and name in missing_signals:
            continue
        weighted_sum += score * w
        total_weight += w

    if total_weight <= 0:
        return 0.0

    # Normalize: max possible is max_signal * total_weight
    raw = weighted_sum / (max_signal * total_weight)
    return round(raw * 100.0, 2)


def get_top_signals(signal_scores: dict[str, int], n: int = 3) -> list[tuple[str, int]]:
    """Return the top N contributing signals by score x weight.

    Args:
        signal_scores: Dict mapping signal name to score (0-3).
        n: Number of top signals to return.

    Returns:
        List of (signal_name, score) tuples sorted by contribution descending.
    """
    weight_map = {sw.name: sw.weight for sw in config.signal_weights}

    contributions = []
    for name, score in signal_scores.items():
        w = weight_map.get(name, 0.0)
        contributions.append((name, score, score * w))

    contributions.sort(key=lambda x: x[2], reverse=True)
    return [(name, score) for name, score, _ in contributions[:n]]


def assign_tier(composite_score: float) -> str:
    """Assign tier label based on composite score.

    Args:
        composite_score: Score in 0-100 range.

    Returns:
        "green", "amber", or "red".
    """
    if composite_score > config.tier_green:
        return "green"
    elif composite_score >= config.tier_amber:
        return "amber"
    else:
        return "red"


def _build_bead_lookup(bead_df: pd.DataFrame) -> dict[str, str]:
    """Pre-build a dict mapping partner_id → highest BEAD status (O(m) once)."""
    status_rank = {"none": 0, "approved": 1, "imminent": 2, "active": 3}
    lookup: dict[str, str] = {}

    for _, row in bead_df.iterrows():
        pids = str(row["partner_ids"]).split(",")
        status = str(row["status"]).lower().strip()
        rank = status_rank.get(status, 0)
        for pid in pids:
            pid = pid.strip()
            if not pid:
                continue
            if rank > status_rank.get(lookup.get(pid, "none"), 0):
                lookup[pid] = status

    return lookup


def _build_service_count_lookup(service_mix_df: pd.DataFrame) -> dict[str, int | float]:
    """Pre-build a dict mapping partner_id → service count (O(m) once)."""
    lookup: dict[str, int | float] = {}
    for _, row in service_mix_df.iterrows():
        pid = row["partner_id"]
        services_str = str(row["services"])
        count = len([s.strip() for s in services_str.split(",") if s.strip()])
        lookup[pid] = count
    return lookup


_FIELD_TO_SIGNAL = {
    "volume_growth_rate": "volume_growth",
    "service_level_pct": "sla_degradation",
    "num_services": "service_concentration",
    "bead_status": "bead_exposure",
    "utilization_rate": "utilization_headroom",
    "repeat_contact_rate": "repeat_contacts",
    "months_until_renewal": "contract_proximity",
    "seasonal_variance_coeff": "seasonal_volatility",
}


def score_all_partners(
    genesys_df: pd.DataFrame,
    helpdesk_df: pd.DataFrame,
    ukg_df: pd.DataFrame,
    wcs_df: pd.DataFrame,
    service_mix_df: pd.DataFrame,
    bead_df: pd.DataFrame,
) -> pd.DataFrame:
    """Score all partners and return ranked DataFrame.

    Merges all connector DataFrames on partner_id, computes signal scores,
    composite score, tier, and top signals for each partner.

    Returns:
        DataFrame sorted by composite_score descending with columns:
        partner_id, all signal scores, composite_score, tier, top_signals, missing_signals.
    """
    from src.scoring.recommender import recommend_play

    # Merge on partner_id (left join from genesys as base)
    merged = genesys_df[["partner_id", "volume_growth_rate", "service_level_pct"]].copy()
    merged = merged.merge(
        helpdesk_df[["partner_id", "repeat_contact_rate"]],
        on="partner_id", how="left",
    )
    merged = merged.merge(
        ukg_df[["partner_id", "utilization_rate"]],
        on="partner_id", how="left",
    )
    merged = merged.merge(
        wcs_df[["partner_id", "seasonal_variance_coeff"]],
        on="partner_id", how="left",
    )

    # Pre-build lookup dicts once — O(m) each instead of O(n*m) in the loop
    bead_lookup = _build_bead_lookup(bead_df)
    service_count_lookup = _build_service_count_lookup(service_mix_df)

    results = []
    for _, row in merged.iterrows():
        pid = row["partner_id"]

        partner_data = {
            "volume_growth_rate": row.get("volume_growth_rate", float("nan")),
            "service_level_pct": row.get("service_level_pct", float("nan")),
            "num_services": service_count_lookup.get(pid, float("nan")),
            "bead_status": bead_lookup.get(pid, "none"),
            "utilization_rate": row.get("utilization_rate", float("nan")),
            "repeat_contact_rate": row.get("repeat_contact_rate", float("nan")),
            "months_until_renewal": float("nan"),  # No data source yet
            "seasonal_variance_coeff": row.get("seasonal_variance_coeff", float("nan")),
        }

        # Track which inputs are missing/NaN
        missing = []
        for key, val in partner_data.items():
            if pd.isna(val):
                missing.append(key)
            elif isinstance(val, str) and not val:
                missing.append(key)

        signal_scores = compute_signal_scores(partner_data)
        missing_signal_names = {_FIELD_TO_SIGNAL[f] for f in missing if f in _FIELD_TO_SIGNAL}
        composite = compute_composite_score(signal_scores, missing_signals=missing_signal_names)
        tier = assign_tier(composite)
        top = get_top_signals(signal_scores, n=3)
        play = recommend_play(signal_scores, composite)

        result = {"partner_id": pid}
        for sig_name, sig_score in signal_scores.items():
            result[f"sig_{sig_name}"] = sig_score
        result["composite_score"] = composite
        result["tier"] = tier
        result["top_signals"] = ", ".join(f"{name}={score}" for name, score in top)
        result["recommended_play"] = play
        result["missing_signals"] = ", ".join(missing) if missing else ""

        results.append(result)

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values("composite_score", ascending=False).reset_index(drop=True)
    return result_df
