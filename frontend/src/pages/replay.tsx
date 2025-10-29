import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import Replay3D from '@/components/Replay3D';
import { fetchLapData } from '@/lib/api';
import { LapResponse } from '@/types/api';

const ReplayPage = () => {
  const [sessionId, setSessionId] = useState('test_session');
  const [carId, setCarId] = useState<string | undefined>(undefined);

  const lapsQuery = useQuery<LapResponse, Error>({
    queryKey: ['laps', sessionId, carId, 'replay'],
    queryFn: () => fetchLapData(sessionId, carId, 1000),
    enabled: Boolean(sessionId)
  });

  const cars = useMemo(() => {
    if (!lapsQuery.data) {
      return [];
    }
    return Array.from(new Set(lapsQuery.data.data.map((frame) => frame.car_id)));
  }, [lapsQuery.data]);

  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <section style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <label>
          Session ID
          <input
            value={sessionId}
            onChange={(event) => setSessionId(event.target.value)}
            style={{
              marginLeft: '0.75rem',
              padding: '0.4rem 0.6rem',
              borderRadius: '0.5rem',
              border: '1px solid rgba(255,255,255,0.1)',
              background: 'rgba(0,0,0,0.4)',
              color: '#fff'
            }}
          />
        </label>
        <label>
          Car
          <select
            value={carId ?? ''}
            onChange={(event) => setCarId(event.target.value || undefined)}
            style={{
              marginLeft: '0.75rem',
              padding: '0.4rem 0.6rem',
              borderRadius: '0.5rem',
              border: '1px solid rgba(255,255,255,0.1)',
              background: 'rgba(0,0,0,0.4)',
              color: '#fff'
            }}
          >
            <option value="">All cars</option>
            {cars.map((car) => (
              <option key={car} value={car}>
                {car}
              </option>
            ))}
          </select>
        </label>
        <span style={{ color: 'var(--muted)' }}>
          {lapsQuery.isFetching ? 'Loading replay data…' : lapsQuery.data ? `${lapsQuery.data.total} frames` : ''}
        </span>
      </section>
      {lapsQuery.data && <Replay3D laps={lapsQuery.data.data} />}
    </div>
  );
};

export default ReplayPage;
