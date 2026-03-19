"""Scoring module — composite engine and recommender."""

from src.scoring.engine import (
    compute_signal_scores,
    compute_composite_score,
    get_top_signals,
    assign_tier,
    score_all_partners,
)
from src.scoring.recommender import recommend_play
