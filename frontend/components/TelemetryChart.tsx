"use client";

import { useMemo } from "react";

type TelemetryChartProps = {
  lapTimes: number[];
};

export default function TelemetryChart({ lapTimes }: TelemetryChartProps) {
  const points = useMemo(() => {
    if (lapTimes.length === 0) {
      return "";
    }
    const max = Math.max(...lapTimes);
    const min = Math.min(...lapTimes);
    const range = max - min || 1;
    return lapTimes
      .map((time, index) => {
        const x = (index / Math.max(lapTimes.length - 1, 1)) * 100;
        const y = 100 - ((time - min) / range) * 100;
        return `${x},${y}`;
      })
      .join(" ");
  }, [lapTimes]);

  return (
    <figure style={{ marginTop: "1.5rem" }}>
      <figcaption style={{ marginBottom: "0.5rem" }}>Tiempo de vuelta (s)</figcaption>
      <svg viewBox="0 0 100 100" role="img" aria-label="Tiempos de vuelta">
        <polyline
          fill="none"
          stroke="#ff4655"
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
          points={points}
        />
      </svg>
    </figure>
  );
}
