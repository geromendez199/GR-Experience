import dynamic from 'next/dynamic';
import { useMemo } from 'react';

import { LapResponse, SessionSummary } from '@/types/api';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface ChartsProps {
  laps: LapResponse | undefined;
  summary: SessionSummary | undefined;
}

const Charts = ({ laps, summary }: ChartsProps) => {
  const lapSeries = useMemo(() => {
    if (!laps) {
      return [];
    }
    const completeLaps = laps.data.filter((frame) => frame.sector === 3 && frame.lap_time_s);
    const grouped = new Map<string, { lap: number; time: number }[]>();
    completeLaps.forEach((frame) => {
      const list = grouped.get(frame.car_id) ?? [];
      list.push({ lap: frame.lap, time: frame.lap_time_s ?? 0 });
      grouped.set(frame.car_id, list);
    });
    return Array.from(grouped.entries()).map(([car, values]) => ({
      x: values.map((item) => item.lap),
      y: values.map((item) => item.time),
      name: car,
      mode: 'lines+markers'
    }));
  }, [laps]);

  const stintAverages = useMemo(() => {
    if (!summary) {
      return [];
    }
    return summary.stints.map((stint) => ({
      x: [stint.start_lap, stint.end_lap],
      y: [stint.avg_pace_s, stint.avg_pace_s],
      name: `${stint.car_id} ${stint.tire_set}`,
      mode: 'lines',
      line: { dash: 'dot' as const }
    }));
  }, [summary]);

  const paceStats = useMemo(() => {
    if (!laps) {
      return null;
    }
    const perLap: Record<number, number[]> = {};
    laps.data.forEach((frame) => {
      if (!frame.lap_time_s || frame.sector !== 3) {
        return;
      }
      perLap[frame.lap] = perLap[frame.lap] ?? [];
      perLap[frame.lap].push(frame.lap_time_s);
    });
    const lapsSorted = Object.keys(perLap)
      .map(Number)
      .sort((a, b) => a - b);
    const mean = lapsSorted.map((lap) => {
      const values = perLap[lap];
      const avg = values.reduce((acc, value) => acc + value, 0) / values.length;
      const variance = values.reduce((acc, value) => acc + (value - avg) ** 2, 0) / values.length;
      const deviation = Math.sqrt(variance);
      return { lap, avg, min: avg - deviation, max: avg + deviation };
    });
    return mean;
  }, [laps]);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
      <Plot
        data={lapSeries}
        layout={{
          title: 'Lap time trend',
          xaxis: { title: 'Lap' },
          yaxis: { title: 'Lap Time (s)' },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: { color: '#f0f3f7' }
        }}
        useResizeHandler
        style={{ width: '100%', height: 360 }}
      />
      {paceStats && (
        <Plot
          data={[
            {
              x: paceStats.map((item) => item.lap),
              y: paceStats.map((item) => item.avg),
              mode: 'lines',
              name: 'Average pace'
            },
            {
              x: paceStats.map((item) => item.lap).concat([...paceStats.map((item) => item.lap)].reverse()),
              y: paceStats.map((item) => item.max).concat([...paceStats.map((item) => item.min)].reverse()),
              fill: 'toself',
              fillcolor: 'rgba(255, 77, 79, 0.15)',
              line: { color: 'transparent' },
              name: 'Variance band',
              type: 'scatter'
            }
          ]}
          layout={{
            title: 'Stint degradation projection',
            xaxis: { title: 'Lap' },
            yaxis: { title: 'Estimated Lap Time (s)' },
            showlegend: true,
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#f0f3f7' }
          }}
          useResizeHandler
          style={{ width: '100%', height: 360 }}
        />
      )}
      {stintAverages.length > 0 && (
        <Plot
          data={stintAverages}
          layout={{
            title: 'Stint average pace',
            xaxis: { title: 'Lap' },
            yaxis: { title: 'Average pace (s)' },
            showlegend: true,
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#f0f3f7' }
          }}
          useResizeHandler
          style={{ width: '100%', height: 320 }}
        />
      )}
    </div>
  );
};

export default Charts;
