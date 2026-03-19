import type { ROICalculationResponse } from '../types/api';
import { formatUSD, formatPercent } from '../utils/format';

interface RecommendationViewProps {
  result: ROICalculationResponse;
  onStartOver: () => void;
}

const BADGE_STYLES: Record<ROICalculationResponse['recommendation'], { bg: string; label: string }> = {
  outsource: { bg: '#38a169', label: 'Outsource to ISPN' },
  flex: { bg: '#d69e2e', label: 'Flex / Hybrid Model' },
  in_house: { bg: '#2b6cb0', label: 'Keep In-House' },
};

export function RecommendationView({ result, onStartOver }: RecommendationViewProps) {
  const badge = BADGE_STYLES[result.recommendation];

  return (
    <div className="recommendation-view">
      <div
        className="recommendation-badge"
        style={{ backgroundColor: badge.bg }}
      >
        {badge.label}
      </div>

      <p className="recommendation-detail">{result.recommendation_detail}</p>

      <div className="key-metrics">
        <div className="metric-card">
          <span className="metric-label">Annual Savings</span>
          <span className="metric-value">{formatUSD(result.annual_savings)}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Savings Percentage</span>
          <span className="metric-value">{formatPercent(result.savings_percentage)}</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Breakeven Subscribers</span>
          <span className="metric-value">
            {result.breakeven_subscribers.toLocaleString()}
          </span>
        </div>
      </div>

      <div className="cost-summary">
        <div className="cost-summary-row">
          <span>In-House Annual Cost</span>
          <span className="num">{formatUSD(result.in_house.total)}</span>
        </div>
        <div className="cost-summary-row">
          <span>ISPN Annual Cost</span>
          <span className="num">{formatUSD(result.ispn.total)}</span>
        </div>
      </div>

      <button type="button" className="btn-primary" onClick={onStartOver}>
        Start Over
      </button>
    </div>
  );
}
