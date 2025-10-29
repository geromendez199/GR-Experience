import { useMemo } from 'react';

import { LapResponse } from '@/types/api';

interface TelemetryTableProps {
  laps: LapResponse | undefined;
  selectedCar: string | undefined;
  onCarChange: (carId: string | undefined) => void;
}

const TelemetryTable = ({ laps, selectedCar, onCarChange }: TelemetryTableProps) => {
  const cars = useMemo(() => {
    if (!laps) {
      return [];
    }
    return Array.from(new Set(laps.data.map((frame) => frame.car_id)));
  }, [laps]);

  const rows = useMemo(() => {
    if (!laps) {
      return [];
    }
    return laps.data
      .filter((frame) => frame.sector === 3)
      .filter((frame) => (selectedCar ? frame.car_id === selectedCar : true))
      .slice(0, 30);
  }, [laps, selectedCar]);

  return (
    <section style={{ background: 'rgba(255,255,255,0.04)', borderRadius: '1rem', padding: '1.5rem' }}>
      <header style={{ display: 'flex', justify-content: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>Lap overview</h2>
        <select
          value={selectedCar ?? ''}
          onChange={(event) => onCarChange(event.target.value || undefined)}
          style={{ padding: '0.4rem 0.6rem', borderRadius: '0.4rem', background: 'rgba(0,0,0,0.4)', color: '#fff' }}
        >
          <option value="">All cars</option>
          {cars.map((car) => (
            <option key={car} value={car}>
              {car}
            </option>
          ))}
        </select>
      </header>
      <div style={{ overflowX: 'auto', marginTop: '1rem' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
              <th>Car</th>
              <th>Lap</th>
              <th>Lap Time (s)</th>
              <th>Avg Speed (kph)</th>
              <th>Throttle (%)</th>
              <th>Brake (%)</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.car_id}-${row.lap}`} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <td>{row.car_id}</td>
                <td>{row.lap}</td>
                <td>{row.lap_time_s?.toFixed(2)}</td>
                <td>{row.speed_kph.toFixed(1)}</td>
                <td>{row.throttle.toFixed(1)}</td>
                <td>{row.brake.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

export default TelemetryTable;
