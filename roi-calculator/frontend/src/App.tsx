import { useState } from 'react';
import type { ROICalculationRequest, ROICalculationResponse } from './types/api';
import { calculateROI } from './api/client';
import { InputForm } from './components/InputForm';
import { ComparisonView } from './components/ComparisonView';
import { RecommendationView } from './components/RecommendationView';

type Step = 'input' | 'comparison' | 'recommendation';

const DEFAULT_FORM_DATA: ROICalculationRequest = {
  subscriber_count: 0,
  monthly_call_volume: 0,
  support_staff_headcount: 0,
  avg_hourly_wage: 0,
  services_internet: true,
  services_voice: false,
  services_video: false,
  services_managed_wifi: false,
  after_hours_coverage: true,
  turnover_rate: null,
};

function App() {
  const [currentStep, setCurrentStep] = useState<Step>('input');
  const [formData, setFormData] = useState<ROICalculationRequest>(DEFAULT_FORM_DATA);
  const [result, setResult] = useState<ROICalculationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: ROICalculationRequest) => {
    setFormData(data);
    setIsLoading(true);
    setError(null);

    try {
      const response = await calculateROI(data);
      setResult(response);
      setCurrentStep('comparison');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setCurrentStep('input');
    setFormData(DEFAULT_FORM_DATA);
    setResult(null);
    setError(null);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>ISPN ROI Calculator</h1>
        <p className="app-subtitle">
          Compare in-house support costs with ISPN managed services
        </p>
      </header>

      <main className="app-main">
        <div className="step-indicator">
          <span className={currentStep === 'input' ? 'step active' : 'step'}>
            1. Input
          </span>
          <span className="step-divider">&rarr;</span>
          <span className={currentStep === 'comparison' ? 'step active' : 'step'}>
            2. Compare
          </span>
          <span className="step-divider">&rarr;</span>
          <span className={currentStep === 'recommendation' ? 'step active' : 'step'}>
            3. Recommend
          </span>
        </div>

        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
            <button
              className="error-dismiss"
              onClick={() => setError(null)}
              type="button"
            >
              Dismiss
            </button>
          </div>
        )}

        {currentStep === 'input' && (
          <InputForm
            initialData={formData}
            onSubmit={handleSubmit}
            isLoading={isLoading}
          />
        )}

        {currentStep === 'comparison' && result && (
          <ComparisonView
            result={result}
            onBack={() => setCurrentStep('input')}
            onNext={() => setCurrentStep('recommendation')}
          />
        )}

        {currentStep === 'recommendation' && result && (
          <RecommendationView
            result={result}
            onStartOver={handleReset}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; ISPN Growth &middot; ROI Calculator</p>
      </footer>
    </div>
  );
}

export default App;
