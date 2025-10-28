"use client";

import { useEffect, useMemo, useState } from "react";

import { fetchEventAnalytics, type EventAnalytics } from "@/lib/api";
import TelemetryChart from "@/components/TelemetryChart";

export default function DashboardSummary() {
  const [analytics, setAnalytics] = useState<EventAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEventAnalytics("barber-motorsports-park")
      .then(setAnalytics)
      .catch((err) => setError(err instanceof Error ? err.message : "Unknown error"));
  }, []);

  const lapTimes = useMemo(() => analytics?.laps.map((lap) => lap.lap_time_seconds) ?? [], [analytics]);

  if (error) {
    return <p role="alert">No se pudo cargar la analítica: {error}</p>;
  }

  if (!analytics) {
    return <p>Cargando analítica...</p>;
  }

  return (
    <section>
      <h2>Resumen del evento</h2>
      <ul>
        <li>Vuelta más rápida: {analytics.fastest_lap_seconds.toFixed(3)} s</li>
        <li>Vuelta más lenta: {analytics.slowest_lap_seconds.toFixed(3)} s</li>
        <li>Promedio de vueltas: {analytics.average_lap_seconds.toFixed(3)} s</li>
      </ul>
      <TelemetryChart lapTimes={lapTimes} />
    </section>
  );
}
