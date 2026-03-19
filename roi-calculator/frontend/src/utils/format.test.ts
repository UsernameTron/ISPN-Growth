import { describe, it, expect } from 'vitest';
import { formatUSD, formatPercent } from './format';

describe('formatUSD', () => {
  it('formats a positive number', () => {
    expect(formatUSD(12345)).toBe('$12,345');
  });

  it('formats a negative number', () => {
    expect(formatUSD(-5000)).toBe('-$5,000');
  });

  it('formats zero', () => {
    expect(formatUSD(0)).toBe('$0');
  });
});

describe('formatPercent', () => {
  it('formats a positive percentage', () => {
    expect(formatPercent(25.678)).toBe('25.7%');
  });

  it('formats a negative percentage', () => {
    expect(formatPercent(-3.14)).toBe('-3.1%');
  });

  it('formats zero', () => {
    expect(formatPercent(0)).toBe('0.0%');
  });
});
