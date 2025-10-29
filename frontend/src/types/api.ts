export interface TelemetryFrame {
  t_ms: number;
  car_id: string;
  lap: number;
  sector: number;
  speed_kph: number;
  throttle: number;
  brake: number;
  gear: number;
  lap_time_s?: number;
  track_temp_c?: number;
  air_temp_c?: number;
  flag_state?: string;
}

export interface LapResponse {
  session_id: string;
  track: string;
  data: TelemetryFrame[];
  total: number;
  offset: number;
  limit: number;
}

export interface SessionSummary {
  fastest_lap: Record<string, number>;
  valid_laps: number;
  stints: Array<{
    car_id: string;
    tire_set: string;
    start_lap: number;
    end_lap: number;
    avg_pace_s: number;
  }>;
}

export interface SessionIngestResponse {
  session_id: string;
  track: string;
  metrics: SessionSummary;
}

export interface StrategyResponse {
  pit_window: [number, number];
  expected_gain_s: number;
  confidence: number;
  stint_summary: Array<{
    pit_window: [number, number];
    expected_gain_s: number;
    confidence: number;
    notes: string[];
  }>;
  notes: string[];
}

export interface TrainingComparisonRequest {
  session_id: string;
  ideal_car_id: string;
  reference_car_id: string;
  lap: number;
  metric: string;
}

export interface TrainingComparisonResponse {
  distance: number;
  path: Array<[number, number]>;
  recommendations: string[];
}
