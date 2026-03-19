"""Tests for the ISPN ROI financial calculation engine."""

from decimal import Decimal

import pytest

from api.models.requests import ROICalculationRequest
from api.services.cost_model import (
    _round_money,
    _service_multiplier,
    _volume_discount,
    calculate_roi,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_request(**overrides) -> ROICalculationRequest:
    """Build a request with sensible defaults, overridden as needed."""
    defaults = dict(
        subscriber_count=1000,
        monthly_call_volume=5000,
        support_staff_headcount=10,
        avg_hourly_wage=18.0,
        services_internet=True,
        services_voice=False,
        services_video=False,
        services_managed_wifi=False,
        after_hours_coverage=True,
        turnover_rate=None,
    )
    defaults.update(overrides)
    return ROICalculationRequest(**defaults)


def _is_clean_decimal(value: float) -> bool:
    """Check that the float has no more than 2 decimal places (no fp noise)."""
    d = Decimal(str(value))
    return d == d.quantize(Decimal("0.01"))


# ---------------------------------------------------------------------------
# 1. Typical ISP profile
# ---------------------------------------------------------------------------

class TestTypicalISP:
    """1000 subscribers, 5000 calls/month, 10 staff, $18/hr."""

    @pytest.fixture()
    def result(self):
        return calculate_roi(_make_request())

    def test_returns_response(self, result):
        assert result.success is True

    def test_in_house_total_positive(self, result):
        assert result.in_house.total > 0

    def test_ispn_total_positive(self, result):
        assert result.ispn.total > 0

    def test_savings_matches_difference(self, result):
        expected = round(result.in_house.total - result.ispn.total, 2)
        assert abs(result.annual_savings - expected) < 0.02

    def test_savings_percentage_computed(self, result):
        if result.in_house.total > 0:
            expected_pct = (result.annual_savings / result.in_house.total) * 100
            assert abs(result.savings_percentage - round(expected_pct, 2)) < 0.1

    def test_recommendation_is_valid(self, result):
        assert result.recommendation in ("outsource", "in_house", "flex")

    def test_breakeven_positive(self, result):
        assert result.breakeven_subscribers > 0


# ---------------------------------------------------------------------------
# 2. Large ISP — should recommend outsource
# ---------------------------------------------------------------------------

class TestLargeISP:
    """Large ISP with high staff costs — outsource expected."""

    @pytest.fixture()
    def result(self):
        return calculate_roi(
            _make_request(
                subscriber_count=50000,
                monthly_call_volume=8000,
                support_staff_headcount=150,
                avg_hourly_wage=22.0,
                services_internet=True,
                services_voice=True,
                services_video=True,
                after_hours_coverage=True,
            )
        )

    def test_recommends_outsource(self, result):
        # 150 staff at $22/hr is expensive; 8K calls/month via ISPN is cheaper
        assert result.recommendation == "outsource", (
            f"Expected 'outsource', got '{result.recommendation}'. "
            f"In-house: {result.in_house.total}, ISPN: {result.ispn.total}"
        )

    def test_positive_savings(self, result):
        assert result.annual_savings > 0

    def test_ispn_cheaper_than_in_house(self, result):
        assert result.ispn.total < result.in_house.total


# ---------------------------------------------------------------------------
# 3. Small ISP — should recommend in_house
# ---------------------------------------------------------------------------

class TestSmallISP:
    """100 subscribers, 500 calls/month, 2 staff — in-house expected."""

    @pytest.fixture()
    def result(self):
        return calculate_roi(
            _make_request(
                subscriber_count=100,
                monthly_call_volume=500,
                support_staff_headcount=2,
                avg_hourly_wage=16.0,
                services_internet=True,
                after_hours_coverage=False,
            )
        )

    def test_recommends_in_house(self, result):
        assert result.recommendation == "in_house", (
            f"Expected 'in_house', got '{result.recommendation}'. "
            f"Savings: {result.savings_percentage}%"
        )

    def test_ispn_more_expensive(self, result):
        assert result.ispn.total > result.in_house.total


# ---------------------------------------------------------------------------
# 4. Single vs multiple services pricing
# ---------------------------------------------------------------------------

class TestServiceMultiplier:

    def test_single_service_multiplier_is_one(self):
        assert _service_multiplier(1) == Decimal("1.0")

    def test_two_services(self):
        assert _service_multiplier(2) == Decimal("1.1")

    def test_four_services_capped(self):
        assert _service_multiplier(4) == Decimal("1.3")

    def test_five_services_still_capped(self):
        # Even if somehow 5+ services, cap at 1.3
        assert _service_multiplier(5) == Decimal("1.3")

    def test_multi_service_costs_more(self):
        single = calculate_roi(
            _make_request(
                services_internet=True,
                services_voice=False,
                services_video=False,
                services_managed_wifi=False,
            )
        )
        multi = calculate_roi(
            _make_request(
                services_internet=True,
                services_voice=True,
                services_video=True,
                services_managed_wifi=False,
            )
        )
        assert multi.ispn.total > single.ispn.total


# ---------------------------------------------------------------------------
# 5. All monetary outputs are Decimal-rounded (no floating-point artifacts)
# ---------------------------------------------------------------------------

class TestDecimalPrecision:
    """Verify no floating-point noise in any monetary output."""

    @pytest.fixture()
    def result(self):
        return calculate_roi(
            _make_request(avg_hourly_wage=18.73)  # awkward wage to stress precision
        )

    def test_in_house_fields_clean(self, result):
        for field in ("labor", "training_ramp", "after_hours", "technology",
                       "management_overhead", "qa_monitoring", "total"):
            val = getattr(result.in_house, field)
            assert _is_clean_decimal(val), f"in_house.{field} = {val!r} has fp noise"

    def test_ispn_fields_clean(self, result):
        for field in ("labor", "total"):
            val = getattr(result.ispn, field)
            assert _is_clean_decimal(val), f"ispn.{field} = {val!r} has fp noise"

    def test_savings_clean(self, result):
        assert _is_clean_decimal(result.annual_savings)

    def test_savings_pct_clean(self, result):
        assert _is_clean_decimal(result.savings_percentage)


# ---------------------------------------------------------------------------
# 6. Breakeven is reasonable
# ---------------------------------------------------------------------------

class TestBreakeven:
    """Breakeven should fall between small and large ISP subscriber counts."""

    def test_breakeven_between_small_and_large(self):
        result = calculate_roi(
            _make_request(
                subscriber_count=5000,
                monthly_call_volume=25000,
                support_staff_headcount=30,
                avg_hourly_wage=18.0,
            )
        )
        # Breakeven should be a positive integer, somewhere reasonable
        assert result.breakeven_subscribers > 0
        # It should not be astronomically high or zero
        assert result.breakeven_subscribers < 10_000_000


# ---------------------------------------------------------------------------
# 7. Volume discount thresholds
# ---------------------------------------------------------------------------

class TestVolumeDiscount:

    def test_no_discount_below_50k(self):
        assert _volume_discount(50000) == Decimal("0")

    def test_five_pct_above_50k(self):
        assert _volume_discount(50001) == Decimal("0.05")

    def test_ten_pct_above_100k(self):
        assert _volume_discount(100001) == Decimal("0.10")


# ---------------------------------------------------------------------------
# 8. After-hours toggle
# ---------------------------------------------------------------------------

class TestAfterHours:

    def test_after_hours_adds_cost_in_house(self):
        with_ah = calculate_roi(_make_request(after_hours_coverage=True))
        without_ah = calculate_roi(_make_request(after_hours_coverage=False))
        assert with_ah.in_house.after_hours > 0
        assert without_ah.in_house.after_hours == 0.0
        assert with_ah.in_house.total > without_ah.in_house.total

    def test_after_hours_no_ispn_surcharge(self):
        with_ah = calculate_roi(_make_request(after_hours_coverage=True))
        without_ah = calculate_roi(_make_request(after_hours_coverage=False))
        # ISPN price is the same regardless of after_hours_coverage
        assert with_ah.ispn.total == without_ah.ispn.total
