"""Tests for the expansion play recommender."""

from src.scoring.recommender import recommend_play


def _make_scores(**overrides) -> dict[str, int]:
    """Create a base signal scores dict with all zeros, then apply overrides."""
    scores = {
        "volume_growth": 0,
        "sla_degradation": 0,
        "service_concentration": 0,
        "bead_exposure": 0,
        "utilization_headroom": 0,
        "repeat_contacts": 0,
        "contract_proximity": 0,
        "seasonal_volatility": 0,
    }
    scores.update(overrides)
    return scores


class TestRecommendPlay:
    def test_service_tier_upgrade(self):
        scores = _make_scores(volume_growth=2, service_concentration=2)
        assert recommend_play(scores, 50.0) == "Service tier upgrade"

    def test_service_tier_upgrade_high_scores(self):
        scores = _make_scores(volume_growth=3, service_concentration=3)
        assert recommend_play(scores, 80.0) == "Service tier upgrade"

    def test_capacity_expansion(self):
        scores = _make_scores(sla_degradation=2, utilization_headroom=2)
        assert recommend_play(scores, 50.0) == "Capacity expansion"

    def test_capacity_expansion_high_scores(self):
        scores = _make_scores(sla_degradation=3, utilization_headroom=3)
        assert recommend_play(scores, 80.0) == "Capacity expansion"

    def test_bead_preparation(self):
        scores = _make_scores(bead_exposure=2, volume_growth=1)
        assert recommend_play(scores, 50.0) == "BEAD preparation package"

    def test_bead_preparation_high_scores(self):
        scores = _make_scores(bead_exposure=3, volume_growth=2)
        assert recommend_play(scores, 80.0) == "BEAD preparation package"

    def test_flex_seasonal_staffing(self):
        scores = _make_scores(seasonal_volatility=2, utilization_headroom=1)
        assert recommend_play(scores, 50.0) == "Flex/seasonal staffing"

    def test_flex_seasonal_staffing_high_scores(self):
        scores = _make_scores(seasonal_volatility=3, utilization_headroom=2)
        assert recommend_play(scores, 60.0) == "Flex/seasonal staffing"

    def test_l2_l3_cross_sell(self):
        scores = _make_scores(repeat_contacts=2)
        assert recommend_play(scores, 30.0) == "L2/L3 or NOC cross-sell"

    def test_l2_l3_cross_sell_high(self):
        scores = _make_scores(repeat_contacts=3)
        assert recommend_play(scores, 40.0) == "L2/L3 or NOC cross-sell"

    def test_default_general_conversation(self):
        scores = _make_scores()  # all zeros
        assert recommend_play(scores, 10.0) == "General expansion conversation"

    def test_default_with_low_scores(self):
        scores = _make_scores(volume_growth=1, sla_degradation=1, repeat_contacts=1)
        assert recommend_play(scores, 20.0) == "General expansion conversation"

    def test_priority_order_service_upgrade_over_capacity(self):
        """Service tier upgrade has higher priority than capacity expansion."""
        scores = _make_scores(
            volume_growth=2, service_concentration=2,
            sla_degradation=2, utilization_headroom=2,
        )
        assert recommend_play(scores, 70.0) == "Service tier upgrade"

    def test_priority_order_capacity_over_bead(self):
        """Capacity expansion has higher priority than BEAD."""
        scores = _make_scores(
            sla_degradation=2, utilization_headroom=2,
            bead_exposure=2, volume_growth=1,
        )
        assert recommend_play(scores, 60.0) == "Capacity expansion"

    def test_priority_order_bead_over_flex(self):
        """BEAD has higher priority than flex staffing."""
        scores = _make_scores(
            bead_exposure=2, volume_growth=1,
            seasonal_volatility=2, utilization_headroom=1,
        )
        assert recommend_play(scores, 50.0) == "BEAD preparation package"

    def test_priority_order_flex_over_cross_sell(self):
        """Flex staffing has higher priority than cross-sell."""
        scores = _make_scores(
            seasonal_volatility=2, utilization_headroom=1,
            repeat_contacts=2,
        )
        assert recommend_play(scores, 50.0) == "Flex/seasonal staffing"
