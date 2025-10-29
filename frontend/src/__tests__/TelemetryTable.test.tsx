import { render, screen } from '@testing-library/react';

import TelemetryTable from '@/components/TelemetryTable';
import { LapResponse } from '@/types/api';

const buildLapResponse = (): LapResponse => ({
  session_id: 'test',
  track: 'Barber',
  data: [
    {
      t_ms: 1000,
      car_id: 'GR21',
      lap: 1,
      sector: 3,
      speed_kph: 180,
      throttle: 95,
      brake: 5,
      gear: 6,
      lap_time_s: 90,
      track_temp_c: 35,
      air_temp_c: 28,
      flag_state: 'green'
    },
    {
      t_ms: 2000,
      car_id: 'GR22',
      lap: 1,
      sector: 3,
      speed_kph: 178,
      throttle: 94,
      brake: 6,
      gear: 6,
      lap_time_s: 91,
      track_temp_c: 35,
      air_temp_c: 28,
      flag_state: 'green'
    }
  ],
  total: 2,
  offset: 0,
  limit: 500
});

describe('TelemetryTable', () => {
  it('renders lap rows for each car', () => {
    render(
      <TelemetryTable laps={buildLapResponse()} selectedCar={undefined} onCarChange={() => undefined} />
    );
    expect(screen.getByText('GR21')).toBeInTheDocument();
    expect(screen.getByText('GR22')).toBeInTheDocument();
    expect(screen.getByText('90.00')).toBeInTheDocument();
  });
});
