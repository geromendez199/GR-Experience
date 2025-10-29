import axios from 'axios';

import {
  LapResponse,
  SessionIngestResponse,
  SessionSummary,
  StrategyResponse,
  TrainingComparisonRequest,
  TrainingComparisonResponse
} from '@/types/api';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'
});

export const ingestSession = async (
  sessionId: string,
  zipPath: string
): Promise<SessionIngestResponse> => {
  const { data } = await api.post<SessionIngestResponse>(
    `/api/sessions/${sessionId}/ingest`,
    { zip_path: zipPath }
  );
  return data;
};

export const fetchLapData = async (
  sessionId: string,
  carId?: string,
  limit = 500
): Promise<LapResponse> => {
  const { data } = await api.get<LapResponse>(`/api/sessions/${sessionId}/laps`, {
    params: {
      car_id: carId,
      limit
    }
  });
  return data;
};

export const fetchSessionSummary = async (
  sessionId: string
): Promise<SessionSummary> => {
  const { data } = await api.get<SessionSummary>(`/api/sessions/${sessionId}/summary`);
  return data;
};

export const simulateStrategy = async (
  sessionId: string,
  targetPosition?: number
): Promise<StrategyResponse> => {
  const { data } = await api.post<StrategyResponse>(`/api/strategy/simulate`, {
    session_id: sessionId,
    target_position: targetPosition
  });
  return data;
};

export const compareLap = async (
  payload: TrainingComparisonRequest
): Promise<TrainingComparisonResponse> => {
  const { data } = await api.post<TrainingComparisonResponse>(
    `/api/training/compare-lap`,
    payload
  );
  return data;
};

export default api;
