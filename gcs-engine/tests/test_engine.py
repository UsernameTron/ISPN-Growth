"""Tests for the composite scoring engine."""

import pandas as pd
import pytest

from src.config import config
from src.scoring.engine import (
    compute_signal_scores,
    compute_composite_score,
    get_top_signals,
    assign_tier,
    score_all_partners,
)


class TestComputeSignalScores:
    def test_all_signals_returned(self):
        data = {
            "volume_growth_rate": 0.10,
            "service_level_pct": 0.85,
            "num_services": 2,
            "bead_status": "active",
            "utilization_rate": 0.75,
            "repeat_contact_rate": 0.15,
            "months_until_renewal": 6.0,
            "seasonal_variance_coeff": 0.20,
        }
        scores = compute_signal_scores(data)
        assert len(scores) == 8
        assert all(isinstance(v, int) for v in scores.values())
        assert all(0 <= v <= 3 for v in scores.values())

    def test_known_values(self):
        data = {
            "volume_growth_rate": 0.20,  # tier 3
            "service_level_pct": 0.65,   # tier 3
            "num_services": 1,           # tier 3
            "bead_status": "active",     # tier 3
            "utilization_rate": 0.50,    # tier 3
            "repeat_contact_rate": 0.35, # tier 3
            "months_until_renewal": 1.0, # tier 3
            "seasonal_variance_coeff": 0.30,  # tier 3
        }
        scores = compute_signal_scores(data)
        assert all(v == 3 for v in scores.values())

    def test_missing_data_defaults_to_zero(self):
        scores = compute_signal_scores({})
        # All NaN/empty -> all score 0
        assert all(v == 0 for v in scores.values())


class TestComputeCompositeScore:
    def test_all_max_scores_100(self):
        scores = {sw.name: 3 for sw in config.signal_weights}
        composite = compute_composite_score(scores)
        assert composite == 100.0

    def test_all_zero_scores_0(self):
        scores = {sw.name: 0 for sw in config.signal_weights}
        composite = compute_composite_score(scores)
        assert composite == 0.0

    def test_partial_scores(self):
        scores = {sw.name: 0 for sw in config.signal_weights}
        scores["volume_growth"] = 3  # weight 0.25
        # Expected: (3 * 0.25) / (3 * 1.0) * 100 = 25.0
        composite = compute_composite_score(scores)
        assert composite == 25.0

    def test_mixed_scores(self):
        scores = {sw.name: 0 for sw in config.signal_weights}
        scores["volume_growth"] = 2       # 0.25 * 2 = 0.50
        scores["sla_degradation"] = 1     # 0.20 * 1 = 0.20
        # Total weighted: 0.70, max possible: 3 * 1.0 = 3.0
        # Score: 0.70 / 3.0 * 100 = 23.33
        composite = compute_composite_score(scores)
        assert composite == pytest.approx(23.33, abs=0.01)

    def test_empty_scores_returns_zero(self):
        composite = compute_composite_score({})
        assert composite == 0.0


class TestGetTopSignals:
    def test_returns_n_signals(self):
        scores = {
            "volume_growth": 3,
            "sla_degradation": 2,
            "service_concentration": 1,
            "bead_exposure": 0,
            "utilization_headroom": 0,
            "repeat_contacts": 0,
            "contract_proximity": 0,
            "seasonal_volatility": 0,
        }
        top = get_top_signals(scores, n=3)
        assert len(top) == 3

    def test_ordered_by_contribution(self):
        scores = {
            "volume_growth": 3,          # 3 * 0.25 = 0.75
            "sla_degradation": 2,        # 2 * 0.20 = 0.40
            "service_concentration": 1,  # 1 * 0.15 = 0.15
            "bead_exposure": 0,
            "utilization_headroom": 0,
            "repeat_contacts": 0,
            "contract_proximity": 0,
            "seasonal_volatility": 0,
        }
        top = get_top_signals(scores, n=3)
        assert top[0][0] == "volume_growth"
        assert top[1][0] == "sla_degradation"
        assert top[2][0] == "service_concentration"

    def test_returns_tuples_of_name_and_score(self):
        scores = {"volume_growth": 2, "sla_degradation": 1}
        top = get_top_signals(scores, n=2)
        for name, score in top:
            assert isinstance(name, str)
            assert isinstance(score, int)


class TestAssignTier:
    def test_green(self):
        assert assign_tier(75.0) == "green"
        assert assign_tier(100.0) == "green"

    def test_amber(self):
        assert assign_tier(40.0) == "amber"
        assert assign_tier(55.0) == "amber"
        assert assign_tier(70.0) == "amber"

    def test_red(self):
        assert assign_tier(39.0) == "red"
        assert assign_tier(0.0) == "red"

    def test_boundary_green(self):
        # >70 is green, 70 is amber
        assert assign_tier(70.01) == "green"
        assert assign_tier(70.0) == "amber"

    def test_boundary_amber(self):
        # >=40 is amber, <40 is red
        assert assign_tier(40.0) == "amber"
        assert assign_tier(39.99) == "red"


class TestScoreAllPartners:
    def _make_mock_data(self, n: int = 3):
        """Create minimal mock DataFrames for testing."""
        pids = [f"P{i:03d}" for i in range(1, n + 1)]

        genesys_df = pd.DataFrame({
            "partner_id": pids,
            "volume_growth_rate": [0.20, 0.03, -0.05],
            "service_level_pct": [0.65, 0.85, 0.92],
        })

        helpdesk_df = pd.DataFrame({
            "partner_id": pids,
            "repeat_contact_rate": [0.35, 0.15, 0.05],
        })

        ukg_df = pd.DataFrame({
            "partner_id": pids,
            "utilization_rate": [0.50, 0.80, 0.96],
        })

        wcs_df = pd.DataFrame({
            "partner_id": pids,
            "seasonal_variance_coeff": [0.30, 0.12, 0.05],
        })

        service_mix_df = pd.DataFrame({
            "partner_id": pids,
            "services": ["internet", "internet,voice,video", "internet,voice,video,managed_wifi"],
        })

        bead_df = pd.DataFrame({
            "state": ["Texas", "California"],
            "status": ["active", "none"],
            "partner_ids": ["P001", "P002,P003"],
        })

        return genesys_df, helpdesk_df, ukg_df, wcs_df, service_mix_df, bead_df

    def test_returns_dataframe_with_required_columns(self):
        dfs = self._make_mock_data()
        result = score_all_partners(*dfs)
        assert isinstance(result, pd.DataFrame)
        assert "partner_id" in result.columns
        assert "composite_score" in result.columns
        assert "tier" in result.columns
        assert "top_signals" in result.columns
        assert "recommended_play" in result.columns

    def test_sorted_by_composite_score_descending(self):
        dfs = self._make_mock_data()
        result = score_all_partners(*dfs)
        scores = result["composite_score"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_all_partners_scored(self):
        dfs = self._make_mock_data()
        result = score_all_partners(*dfs)
        assert len(result) == 3

    def test_tier_values_valid(self):
        dfs = self._make_mock_data()
        result = score_all_partners(*dfs)
        assert set(result["tier"].unique()).issubset({"green", "amber", "red"})

    def test_missing_signals_flagged(self):
        dfs = self._make_mock_data()
        result = score_all_partners(*dfs)
        # months_until_renewal has no data source, so always missing
        for _, row in result.iterrows():
            assert "months_until_renewal" in row["missing_signals"]

    def test_full_pipeline_with_real_stubs(self):
        """Integration test using actual stub connector data."""
        from src.connectors import (
            GenesysConnector, HelpDeskConnector, UKGConnector,
            WCSConnector, ServiceMixConnector, BEADConnector,
        )
        genesys_df = GenesysConnector().get_data()
        helpdesk_df = HelpDeskConnector().get_data()
        ukg_df = UKGConnector().get_data()
        wcs_df = WCSConnector().get_data()
        service_mix_df = ServiceMixConnector().get_data()
        bead_df = BEADConnector().get_data()

        result = score_all_partners(
            genesys_df, helpdesk_df, ukg_df, wcs_df, service_mix_df, bead_df
        )
        assert len(result) == 30
        assert result["composite_score"].max() <= 100.0
        assert result["composite_score"].min() >= 0.0
