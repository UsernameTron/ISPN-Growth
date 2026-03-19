export interface ROICalculationRequest {
  subscriber_count: number;
  monthly_call_volume: number;
  support_staff_headcount: number;
  avg_hourly_wage: number;
  services_internet: boolean;
  services_voice: boolean;
  services_video: boolean;
  services_managed_wifi: boolean;
  after_hours_coverage: boolean;
  turnover_rate: number | null;
}

export interface CostBreakdown {
  labor: number;
  training_ramp: number;
  after_hours: number;
  technology: number;
  management_overhead: number;
  qa_monitoring: number;
  total: number;
}

export interface ROICalculationResponse {
  success: boolean;
  in_house: CostBreakdown;
  ispn: CostBreakdown;
  annual_savings: number;
  savings_percentage: number;
  breakeven_subscribers: number;
  recommendation: 'outsource' | 'in_house' | 'flex';
  recommendation_detail: string;
  timestamp: string;
}
