import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { ROICalculationResponse, CostBreakdown } from '../types/api';
import { formatUSD, formatPercent } from '../utils/format';

interface ComparisonViewProps {
  result: ROICalculationResponse;
  onBack: () => void;
  onNext: () => void;
}

const COST_LABELS: Record<keyof Omit<CostBreakdown, 'total'>, string> = {
  labor: 'Labor',
  training_ramp: 'Training & Ramp-Up',
  after_hours: 'After-Hours Coverage',
  technology: 'Technology',
  management_overhead: 'Management Overhead',
  qa_monitoring: 'QA & Monitoring',
};

export function ComparisonView({ result, onBack, onNext }: ComparisonViewProps) {
  const lineItems = Object.keys(COST_LABELS) as Array<keyof Omit<CostBreakdown, 'total'>>;

  const chartData = [
    { name: 'In-House', cost: result.in_house.total },
    { name: 'ISPN', cost: result.ispn.total },
  ];

  return (
    <div className="comparison-view">
      <div className="savings-highlight">
        <div className="savings-card">
          <span className="savings-label">Annual Savings</span>
          <span className="savings-value">{formatUSD(result.annual_savings)}</span>
        </div>
        <div className="savings-card">
          <span className="savings-label">Savings</span>
          <span className="savings-value">{formatPercent(result.savings_percentage)}</span>
        </div>
        <div className="savings-card">
          <span className="savings-label">Breakeven Subscribers</span>
          <span className="savings-value">
            {result.breakeven_subscribers.toLocaleString()}
          </span>
        </div>
      </div>

      <div className="chart-container">
        <h3>Total Cost Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 40, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(v: number) => formatUSD(v)} />
            <Tooltip formatter={(v: number) => formatUSD(v)} />
            <Legend />
            <Bar dataKey="cost" name="Annual Cost" fill="#2b6cb0" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <table className="comparison-table">
        <thead>
          <tr>
            <th>Cost Category</th>
            <th>In-House</th>
            <th>ISPN</th>
            <th>Difference</th>
          </tr>
        </thead>
        <tbody>
          {lineItems.map((key) => {
            const diff = result.in_house[key] - result.ispn[key];
            return (
              <tr key={key}>
                <td>{COST_LABELS[key]}</td>
                <td className="num">{formatUSD(result.in_house[key])}</td>
                <td className="num">{formatUSD(result.ispn[key])}</td>
                <td className={`num ${diff > 0 ? 'positive' : diff < 0 ? 'negative' : ''}`}>
                  {diff > 0 ? '+' : ''}{formatUSD(diff)}
                </td>
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr className="total-row">
            <td><strong>Total</strong></td>
            <td className="num"><strong>{formatUSD(result.in_house.total)}</strong></td>
            <td className="num"><strong>{formatUSD(result.ispn.total)}</strong></td>
            <td className={`num ${result.annual_savings > 0 ? 'positive' : result.annual_savings < 0 ? 'negative' : ''}`}>
              <strong>{result.annual_savings > 0 ? '+' : ''}{formatUSD(result.annual_savings)}</strong>
            </td>
          </tr>
        </tfoot>
      </table>

      <div className="button-row">
        <button type="button" className="btn-secondary" onClick={onBack}>
          &larr; Back to Input
        </button>
        <button type="button" className="btn-primary" onClick={onNext}>
          View Recommendation &rarr;
        </button>
      </div>
    </div>
  );
}
