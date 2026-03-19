import { useState } from 'react';
import type { ROICalculationRequest } from '../types/api';

interface InputFormProps {
  initialData: ROICalculationRequest;
  onSubmit: (data: ROICalculationRequest) => void;
  isLoading: boolean;
}

export function InputForm({ initialData, onSubmit, isLoading }: InputFormProps) {
  const [data, setData] = useState<ROICalculationRequest>(initialData);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const setField = <K extends keyof ROICalculationRequest>(
    key: K,
    value: ROICalculationRequest[K]
  ) => {
    setData((prev) => ({ ...prev, [key]: value }));
  };

  const validate = (): string[] => {
    const errors: string[] = [];
    if (data.subscriber_count <= 0) errors.push('Subscriber count must be greater than 0');
    if (data.monthly_call_volume <= 0) errors.push('Monthly call volume must be greater than 0');
    if (data.support_staff_headcount <= 0) errors.push('Support staff headcount must be greater than 0');
    if (data.avg_hourly_wage <= 0) errors.push('Average hourly wage must be greater than 0');
    return errors;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const errors = validate();
    setValidationErrors(errors);
    if (errors.length === 0) {
      onSubmit(data);
    }
  };

  return (
    <form className="input-form" onSubmit={handleSubmit}>
      {validationErrors.length > 0 && (
        <div className="validation-errors">
          <strong>Please fix the following:</strong>
          <ul>
            {validationErrors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      <fieldset className="form-section">
        <legend>Company Details</legend>

        <div className="form-group">
          <label htmlFor="subscriber_count">Total Subscribers</label>
          <input
            id="subscriber_count"
            type="number"
            min="1"
            value={data.subscriber_count || ''}
            onChange={(e) => setField('subscriber_count', Number(e.target.value))}
            placeholder="e.g. 25000"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="monthly_call_volume">Monthly Call Volume</label>
          <input
            id="monthly_call_volume"
            type="number"
            min="1"
            value={data.monthly_call_volume || ''}
            onChange={(e) => setField('monthly_call_volume', Number(e.target.value))}
            placeholder="e.g. 5000"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="support_staff_headcount">Support Staff Headcount</label>
          <input
            id="support_staff_headcount"
            type="number"
            min="1"
            value={data.support_staff_headcount || ''}
            onChange={(e) => setField('support_staff_headcount', Number(e.target.value))}
            placeholder="e.g. 15"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="avg_hourly_wage">Average Hourly Wage (USD)</label>
          <input
            id="avg_hourly_wage"
            type="number"
            min="1"
            step="0.01"
            value={data.avg_hourly_wage || ''}
            onChange={(e) => setField('avg_hourly_wage', Number(e.target.value))}
            placeholder="e.g. 18.50"
            required
          />
        </div>
      </fieldset>

      <fieldset className="form-section">
        <legend>Services Supported</legend>

        <div className="checkbox-grid">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={data.services_internet}
              onChange={(e) => setField('services_internet', e.target.checked)}
            />
            Internet
          </label>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={data.services_voice}
              onChange={(e) => setField('services_voice', e.target.checked)}
            />
            Voice / Phone
          </label>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={data.services_video}
              onChange={(e) => setField('services_video', e.target.checked)}
            />
            Video / Streaming
          </label>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={data.services_managed_wifi}
              onChange={(e) => setField('services_managed_wifi', e.target.checked)}
            />
            Managed WiFi
          </label>
        </div>
      </fieldset>

      <fieldset className="form-section">
        <legend>Additional Options</legend>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={data.after_hours_coverage}
            onChange={(e) => setField('after_hours_coverage', e.target.checked)}
          />
          After-Hours Coverage (nights &amp; weekends)
        </label>

        <div className="form-group" style={{ marginTop: '1rem' }}>
          <label htmlFor="turnover_rate">
            Turnover Rate Override (optional, 0&ndash;100%)
          </label>
          <div className="slider-row">
            <input
              id="turnover_rate"
              type="range"
              min="0"
              max="100"
              step="1"
              value={data.turnover_rate !== null ? data.turnover_rate * 100 : 35}
              onChange={(e) => setField('turnover_rate', Number(e.target.value) / 100)}
            />
            <span className="slider-value">
              {data.turnover_rate !== null
                ? `${(data.turnover_rate * 100).toFixed(0)}%`
                : '35% (default)'}
            </span>
            {data.turnover_rate !== null && (
              <button
                type="button"
                className="btn-link"
                onClick={() => setField('turnover_rate', null)}
              >
                Reset
              </button>
            )}
          </div>
        </div>
      </fieldset>

      <button type="submit" className="btn-primary" disabled={isLoading}>
        {isLoading ? (
          <span className="loading-spinner">Calculating&hellip;</span>
        ) : (
          'Calculate ROI'
        )}
      </button>
    </form>
  );
}
