"""Pydantic response models for ROI Calculator."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class CostBreakdown(BaseModel):
    """Itemized cost breakdown."""

    labor: float
    training_ramp: float
    after_hours: float
    technology: float
    management_overhead: float
    qa_monitoring: float
    total: float


class ROICalculationResponse(BaseModel):
    """Full ROI comparison result."""

    success: bool = True
    in_house: CostBreakdown
    ispn: CostBreakdown
    annual_savings: float
    savings_percentage: float
    breakeven_subscribers: int
    recommendation: str  # "outsource" | "in_house" | "flex"
    recommendation_detail: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
