export type LapMetric = {
  lap_number: number;
  lap_time_seconds: number;
  average_speed_kmh: number;
  throttle_usage_pct: number;
  brake_usage_pct: number;
};

export type EventAnalytics = {
  event_id: string;
  fastest_lap_seconds: number;
  slowest_lap_seconds: number;
  average_lap_seconds: number;
  laps: LapMetric[];
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json"
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Solicitud fallida: ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function fetchEventAnalytics(eventId: string): Promise<EventAnalytics> {
  return fetchJson<EventAnalytics>(`${API_BASE_URL}/events/${eventId}/analytics`);
}
