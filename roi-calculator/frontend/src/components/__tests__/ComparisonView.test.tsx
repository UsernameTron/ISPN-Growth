import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ComparisonView } from '../ComparisonView';
import type { ROICalculationResponse, CostBreakdown } from '../../types/api';

// Mock recharts — ResponsiveContainer needs a real DOM width; just render children.
vi.mock('recharts', () => ({
  BarChart: () => null,
  Bar: () => null,
  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
  Legend: () => null,
  ResponsiveContainer: () => null,
}));

function makeCostBreakdown(overrides: Partial<CostBreakdown> = {}): CostBreakdown {
  return {
    labor: 100000,
    training_ramp: 10000,
    after_hours: 5000,
    technology: 8000,
    management_overhead: 12000,
    qa_monitoring: 6000,
    total: 141000,
    ...overrides,
  };
}

function makeResult(overrides: Partial<ROICalculationResponse> = {}): ROICalculationResponse {
  return {
    success: true,
    in_house: makeCostBreakdown(),
    ispn: makeCostBreakdown({ labor: 80000, total: 121000 }),
    annual_savings: 20000,
    savings_percentage: 14.2,
    breakeven_subscribers: 5000,
    recommendation: 'outsource',
    recommendation_detail: 'ISPN is more cost-effective.',
    timestamp: '2026-03-19T00:00:00Z',
    ...overrides,
  };
}

const noop = () => {};

describe('ComparisonView — savings display', () => {
  it('renders without crashing with valid data', () => {
    const result = makeResult();
    render(<ComparisonView result={result} onBack={noop} onNext={noop} />);
    expect(screen.getByText('Annual Savings')).toBeTruthy();
  });

  it('displays positive savings with "+" prefix and "positive" class', () => {
    const result = makeResult({ annual_savings: 20000 });
    render(<ComparisonView result={result} onBack={noop} onNext={noop} />);

    // The total row should show "+$20,000"
    const totalRow = screen.getByText('Total').closest('tr')!;
    const cells = totalRow.querySelectorAll('td');
    const diffCell = cells[cells.length - 1];

    expect(diffCell.textContent).toBe('+$20,000');
    expect(diffCell.classList.contains('positive')).toBe(true);
    expect(diffCell.classList.contains('negative')).toBe(false);
  });

  it('displays negative savings without "+" prefix and with "negative" class (no "+-" double sign)', () => {
    // ISPN costs more than in-house: savings are negative
    const result = makeResult({
      in_house: makeCostBreakdown({ total: 100000 }),
      ispn: makeCostBreakdown({ total: 115000 }),
      annual_savings: -15000,
    });
    render(<ComparisonView result={result} onBack={noop} onNext={noop} />);

    const totalRow = screen.getByText('Total').closest('tr')!;
    const cells = totalRow.querySelectorAll('td');
    const diffCell = cells[cells.length - 1];

    // Must be "-$15,000", NOT "+-$15,000"
    expect(diffCell.textContent).toBe('-$15,000');
    expect(diffCell.classList.contains('negative')).toBe(true);
    expect(diffCell.classList.contains('positive')).toBe(false);
  });

  it('displays zero savings with no prefix and no positive/negative class', () => {
    const breakdown = makeCostBreakdown();
    const result = makeResult({
      in_house: breakdown,
      ispn: { ...breakdown },
      annual_savings: 0,
    });
    render(<ComparisonView result={result} onBack={noop} onNext={noop} />);

    const totalRow = screen.getByText('Total').closest('tr')!;
    const cells = totalRow.querySelectorAll('td');
    const diffCell = cells[cells.length - 1];

    expect(diffCell.textContent).toBe('$0');
    expect(diffCell.classList.contains('positive')).toBe(false);
    expect(diffCell.classList.contains('negative')).toBe(false);
  });
});
