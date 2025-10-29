import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import TrainingCompare from '@/components/TrainingCompare';
import { fetchLapData } from '@/lib/api';
import { LapResponse } from '@/types/api';

const TrainingPage = () => {
  const [sessionId, setSessionId] = useState('test_session');
  const lapsQuery = useQuery<LapResponse, Error>({
    queryKey: ['laps', sessionId],
    queryFn: () => fetchLapData(sessionId),
    enabled: Boolean(sessionId)
  });

  const cars = useMemo(() => {
    if (!lapsQuery.data) {
      return [];
    }
    return Array.from(new Set(lapsQuery.data.data.map((frame) => frame.car_id)));
  }, [lapsQuery.data]);

  const laps = useMemo(() => {
    if (!lapsQuery.data) {
      return [];
    }
    return Array.from(new Set(lapsQuery.data.data.map((frame) => frame.lap))).sort((a, b) => a - b);
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
        <span style={{ color: 'var(--muted)' }}>
          {lapsQuery.isFetching ? 'Loading laps…' : cars.length ? `${cars.length} cars loaded` : ''}
        </span>
      </section>
      {cars.length >= 1 && laps.length >= 1 && (
        <TrainingCompare sessionId={sessionId} cars={cars} lapsAvailable={laps} />
      )}
    </div>
  );
};

export default TrainingPage;
