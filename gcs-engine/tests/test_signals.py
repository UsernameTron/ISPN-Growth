"""Tests for all 8 signal scorers — each tests all 4 tiers plus NaN handling."""

import math

import pytest

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


class TestVolumeGrowth:
    def test_tier_0_declining(self):
        assert score_volume_growth(-0.10) == 0

    def test_tier_0_boundary(self):
        # -0.03 is the boundary: < -0.03 is declining (tier 0), -0.03 exactly is tier 1
        assert score_volume_growth(-0.031) == 0
        assert score_volume_growth(-0.03) == 1

    def test_tier_1_flat(self):
        assert score_volume_growth(0.0) == 1
        assert score_volume_growth(0.04) == 1

    def test_tier_1_boundary(self):
        assert score_volume_growth(-0.029) == 1

    def test_tier_2_moderate(self):
        assert score_volume_growth(0.05) == 2
        assert score_volume_growth(0.10) == 2
        assert score_volume_growth(0.15) == 2

    def test_tier_3_strong(self):
        assert score_volume_growth(0.16) == 3
        assert score_volume_growth(0.25) == 3

    def test_nan_returns_0(self):
        assert score_volume_growth(float("nan")) == 0


class TestSLADegradation:
    def test_tier_0_stable(self):
        assert score_sla_degradation(0.95) == 0
        assert score_sla_degradation(0.90) == 0

    def test_tier_1_slight_decline(self):
        assert score_sla_degradation(0.89) == 1
        assert score_sla_degradation(0.80) == 1

    def test_tier_2_at_risk(self):
        assert score_sla_degradation(0.79) == 2
        assert score_sla_degradation(0.70) == 2

    def test_tier_3_breached(self):
        assert score_sla_degradation(0.69) == 3
        assert score_sla_degradation(0.50) == 3

    def test_nan_returns_0(self):
        assert score_sla_degradation(float("nan")) == 0


class TestServiceConcentration:
    def test_tier_0_diversified(self):
        assert score_service_concentration(4) == 0
        assert score_service_concentration(5) == 0

    def test_tier_1_three(self):
        assert score_service_concentration(3) == 1

    def test_tier_2_two(self):
        assert score_service_concentration(2) == 2

    def test_tier_3_one(self):
        assert score_service_concentration(1) == 3

    def test_nan_returns_0(self):
        assert score_service_concentration(float("nan")) == 0


class TestBEADExposure:
    def test_tier_0_none(self):
        assert score_bead_exposure("none") == 0

    def test_tier_1_approved(self):
        assert score_bead_exposure("approved") == 1

    def test_tier_2_imminent(self):
        assert score_bead_exposure("imminent") == 2

    def test_tier_3_active(self):
        assert score_bead_exposure("active") == 3

    def test_empty_string_returns_0(self):
        assert score_bead_exposure("") == 0

    def test_none_value_returns_0(self):
        assert score_bead_exposure(None) == 0

    def test_unknown_status_returns_0(self):
        assert score_bead_exposure("unknown") == 0

    def test_case_insensitive(self):
        assert score_bead_exposure("Active") == 3
        assert score_bead_exposure("IMMINENT") == 2


class TestUtilizationHeadroom:
    def test_tier_0_no_headroom(self):
        assert score_utilization_headroom(0.95) == 0
        assert score_utilization_headroom(0.99) == 0

    def test_tier_1_tight(self):
        assert score_utilization_headroom(0.85) == 1
        assert score_utilization_headroom(0.90) == 1

    def test_tier_2_moderate(self):
        assert score_utilization_headroom(0.70) == 2
        assert score_utilization_headroom(0.80) == 2

    def test_tier_3_ample(self):
        assert score_utilization_headroom(0.69) == 3
        assert score_utilization_headroom(0.50) == 3

    def test_nan_returns_0(self):
        assert score_utilization_headroom(float("nan")) == 0


class TestRepeatContacts:
    def test_tier_0_low(self):
        assert score_repeat_contacts(0.05) == 0
        assert score_repeat_contacts(0.09) == 0

    def test_tier_1_moderate(self):
        assert score_repeat_contacts(0.10) == 1
        assert score_repeat_contacts(0.15) == 1
        assert score_repeat_contacts(0.20) == 1

    def test_tier_2_high(self):
        assert score_repeat_contacts(0.21) == 2
        assert score_repeat_contacts(0.25) == 2
        assert score_repeat_contacts(0.30) == 2

    def test_tier_3_very_high(self):
        assert score_repeat_contacts(0.31) == 3
        assert score_repeat_contacts(0.40) == 3

    def test_nan_returns_0(self):
        assert score_repeat_contacts(float("nan")) == 0


class TestContractProximity:
    def test_tier_0_far(self):
        assert score_contract_proximity(13.0) == 0
        assert score_contract_proximity(24.0) == 0

    def test_tier_1_approaching(self):
        assert score_contract_proximity(12.0) == 1
        assert score_contract_proximity(6.0) == 1

    def test_tier_2_near(self):
        assert score_contract_proximity(5.0) == 2
        assert score_contract_proximity(3.0) == 2

    def test_tier_3_imminent(self):
        assert score_contract_proximity(2.0) == 3
        assert score_contract_proximity(0.5) == 3

    def test_nan_returns_0(self):
        assert score_contract_proximity(float("nan")) == 0


class TestSeasonalVolatility:
    def test_tier_0_stable(self):
        assert score_seasonal_volatility(0.05) == 0
        assert score_seasonal_volatility(0.09) == 0

    def test_tier_1_mild(self):
        assert score_seasonal_volatility(0.10) == 1
        assert score_seasonal_volatility(0.14) == 1

    def test_tier_2_moderate(self):
        assert score_seasonal_volatility(0.15) == 2
        assert score_seasonal_volatility(0.20) == 2
        assert score_seasonal_volatility(0.24) == 2

    def test_tier_3_high(self):
        assert score_seasonal_volatility(0.25) == 3
        assert score_seasonal_volatility(0.40) == 3

    def test_nan_returns_0(self):
        assert score_seasonal_volatility(float("nan")) == 0
