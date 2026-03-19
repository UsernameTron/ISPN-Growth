"""Pydantic request models for ROI Calculator."""

from pydantic import BaseModel, Field


class ROICalculationRequest(BaseModel):
    """Input for ROI calculation."""

    subscriber_count: int = Field(..., gt=0, description="Total subscriber count")
    monthly_call_volume: int = Field(..., gt=0, description="Monthly inbound call volume")
    support_staff_headcount: int = Field(..., gt=0, description="Current support staff count")
    avg_hourly_wage: float = Field(..., gt=0, description="Average hourly wage in USD")

    # Optional with smart defaults
    services_internet: bool = Field(True, description="Provides internet support")
    services_voice: bool = Field(False, description="Provides voice/phone support")
    services_video: bool = Field(False, description="Provides video/streaming support")
    services_managed_wifi: bool = Field(False, description="Provides managed WiFi support")
    after_hours_coverage: bool = Field(True, description="Requires after-hours coverage")
    turnover_rate: float | None = Field(
        None, description="Override industry turnover rate (0-1)"
    )

    @property
    def service_count(self) -> int:
        """Count of active services."""
        return sum([
            self.services_internet,
            self.services_voice,
            self.services_video,
            self.services_managed_wifi,
        ])
