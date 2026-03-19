import type { ROICalculationRequest, ROICalculationResponse } from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

export async function calculateROI(
  request: ROICalculationRequest
): Promise<ROICalculationResponse> {
  const response = await fetch(`${API_BASE}/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function getDefaults(): Promise<Partial<ROICalculationRequest>> {
  const response = await fetch(`${API_BASE}/defaults`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}
