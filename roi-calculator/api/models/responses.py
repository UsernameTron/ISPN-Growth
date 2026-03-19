"""Pydantic response models for ROI Calculator."""

from datetime import datetime, timezone

from decimal import Decimal

from pydantic import BaseModel, Field


class CostBreakdown(BaseModel):
    """Itemized cost breakdown."""

    labor: Decimal
    training_ramp: Decimal
    after_hours: Decimal
    technology: Decimal
    management_overhead: Decimal
    qa_monitoring: Decimal
    total: Decimal


class ROICalculationResponse(BaseModel):
    """Full ROI comparison result."""

    success: bool = True
    in_house: CostBreakdown
    ispn: CostBreakdown
    annual_savings: Decimal
    savings_percentage: Decimal
    breakeven_subscribers: int
    recommendation: str  # "outsource" | "in_house" | "flex"
    recommendation_detail: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
