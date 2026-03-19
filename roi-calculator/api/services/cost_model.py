"""Financial calculation engine for ISPN ROI Calculator.

All monetary math uses Decimal arithmetic to avoid floating-point artifacts.
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from api.config import settings
from api.models.requests import ROICalculationRequest
from api.models.responses import CostBreakdown, ROICalculationResponse


def _to_dec(value: float | int) -> Decimal:
    """Convert a float/int to Decimal via string to avoid float artifacts."""
    return Decimal(str(value))


def _round_money(value: Decimal) -> Decimal:
    """Round to 2 decimal places using banker-friendly rounding."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _calculate_in_house(request: ROICalculationRequest) -> CostBreakdown:
    """Calculate annual in-house support costs."""
    headcount = _to_dec(request.support_staff_headcount)
    hourly_wage = _to_dec(request.avg_hourly_wage)
    annual_hours = Decimal("2080")
    turnover = _to_dec(request.turnover_rate) if request.turnover_rate is not None else settings.INDUSTRY_TURNOVER

    # Core labor
    labor = headcount * hourly_wage * annual_hours

    # Training ramp cost: proportion of year spent training replacements
    training_weeks = _to_dec(settings.TRAINING_RAMP_WEEKS)
    training_ramp = (training_weeks / Decimal("52")) * turnover * labor

    # After-hours surcharge
    after_hours = Decimal("0")
    if request.after_hours_coverage:
        # 30% of calls happen after hours; premium applies to that labor share
        after_hours_labor_share = Decimal("0.30") * labor
        # NOTE: 1.5x is the full premium rate applied to the after-hours labor share,
        # not the 0.5x incremental above base. Verify business intent.
        after_hours = settings.AFTER_HOURS_PREMIUM * after_hours_labor_share

    # Technology: Genesys licensing estimate $150/seat/month
    technology = Decimal("150") * headcount * Decimal("12")

    # Management overhead
    management_overhead = settings.MANAGEMENT_OVERHEAD * labor

    # QA / monitoring overhead
    qa_monitoring = settings.QA_MONITORING_OVERHEAD * labor

    total = labor + training_ramp + after_hours + technology + management_overhead + qa_monitoring

    return CostBreakdown(
        labor=float(_round_money(labor)),
        training_ramp=float(_round_money(training_ramp)),
        after_hours=float(_round_money(after_hours)),
        technology=float(_round_money(technology)),
        management_overhead=float(_round_money(management_overhead)),
        qa_monitoring=float(_round_money(qa_monitoring)),
        total=float(_round_money(total)),
    )


def _service_multiplier(service_count: int) -> Decimal:
    """1.0 for 1 service, +0.1 per additional, max 1.3."""
    if service_count <= 1:
        return Decimal("1.0")
    extra = min(service_count - 1, 3)  # cap at +0.3
    return Decimal("1.0") + _to_dec(extra) * Decimal("0.1")


def _volume_discount(monthly_call_volume: int) -> Decimal:
    """Volume discount rate based on monthly call volume."""
    if monthly_call_volume > 100_000:
        return Decimal("0.10")
    if monthly_call_volume > 50_000:
        return Decimal("0.05")
    return Decimal("0")


def _calculate_ispn(request: ROICalculationRequest) -> CostBreakdown:
    """Calculate annual ISPN outsourced cost."""
    volume = _to_dec(request.monthly_call_volume)

    # Base annual cost
    base = volume * settings.BLENDED_RATE * settings.MULTIPLIER * Decimal("12")

    # Service multiplier
    svc_mult = _service_multiplier(request.service_count)

    # Volume discount
    discount = _volume_discount(request.monthly_call_volume)

    total = base * svc_mult * (Decimal("1") - discount)

    # ISPN bundles after-hours and technology into the price
    return CostBreakdown(
        labor=float(_round_money(total)),
        training_ramp=0.0,
        after_hours=0.0,
        technology=0.0,
        management_overhead=0.0,
        qa_monitoring=0.0,
        total=float(_round_money(total)),
    )


def _calculate_breakeven(request: ROICalculationRequest, in_house_total: Decimal) -> int:
    """Find subscriber count where ISPN cost equals in-house cost.

    Uses binary search over subscriber counts. The ISPN cost scales with
    monthly_call_volume, which we model as proportional to subscriber_count.

    Assumptions:
        - Only subscriber count (and proportionally, call volume) varies during
          the search. The calls-per-subscriber ratio is held constant from the
          original input.
        - In-house costs are held constant at the values computed from the
          original input (headcount, wages, etc. do not change).
        - Therefore the breakeven point represents the subscriber count at which
          ISPN outsourcing becomes cost-competitive against the *current*
          in-house cost structure.
    """
    if in_house_total <= Decimal("0"):
        return 0

    # Ratio: calls per subscriber (from the input)
    calls_per_sub = _to_dec(request.monthly_call_volume) / _to_dec(request.subscriber_count)

    low = 1
    high = max(request.subscriber_count * 10, 1_000_000)

    # Precompute constants
    svc_mult = _service_multiplier(request.service_count)
    rate_annual = settings.BLENDED_RATE * settings.MULTIPLIER * Decimal("12")

    for _ in range(50):  # binary search iterations
        mid = (low + high) // 2
        monthly_vol = int(_to_dec(mid) * calls_per_sub)
        discount = _volume_discount(monthly_vol)
        ispn_cost = _to_dec(monthly_vol) * rate_annual * svc_mult * (Decimal("1") - discount)

        if ispn_cost < in_house_total:
            low = mid + 1
        else:
            high = mid

        if low >= high:
            break

    return low


def _make_recommendation(
    in_house_total: Decimal,
    ispn_total: Decimal,
    savings: Decimal,
    savings_pct: Decimal,
    breakeven: int,
) -> tuple[str, str]:
    """Return (recommendation, detail) based on savings percentage."""
    if savings_pct > Decimal("15"):
        return (
            "outsource",
            f"ISPN saves ${_round_money(savings):,}/year ({_round_money(savings_pct)}%). "
            f"Full outsourcing is strongly recommended.",
        )
    if savings_pct > Decimal("5"):
        return (
            "flex",
            f"ISPN saves ${_round_money(savings):,}/year ({_round_money(savings_pct)}%). "
            f"Consider ISPN Flex for peak periods and after-hours coverage.",
        )
    return (
        "in_house",
        f"In-house is currently more cost-effective. "
        f"Outsourcing becomes favorable above ~{breakeven:,} subscribers.",
    )


def calculate_roi(request: ROICalculationRequest) -> ROICalculationResponse:
    """Main entry point: compute full ROI comparison."""
    in_house = _calculate_in_house(request)
    ispn = _calculate_ispn(request)

    in_house_total = _to_dec(in_house.total)
    ispn_total = _to_dec(ispn.total)
    savings = in_house_total - ispn_total

    if in_house_total > Decimal("0"):
        savings_pct = (savings / in_house_total) * Decimal("100")
    else:
        savings_pct = Decimal("0")

    breakeven = _calculate_breakeven(request, in_house_total)

    recommendation, detail = _make_recommendation(
        in_house_total, ispn_total, savings, savings_pct, breakeven
    )

    return ROICalculationResponse(
        in_house=in_house,
        ispn=ispn,
        annual_savings=float(_round_money(savings)),
        savings_percentage=float(_round_money(savings_pct)),
        breakeven_subscribers=breakeven,
        recommendation=recommendation,
        recommendation_detail=detail,
    )
