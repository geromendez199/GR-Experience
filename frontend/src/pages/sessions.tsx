import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import Charts from '@/components/Charts';
import StrategyPanel from '@/components/StrategyPanel';
import TelemetryTable from '@/components/TelemetryTable';
import { fetchLapData, fetchSessionSummary } from '@/lib/api';
import { LapResponse, SessionSummary } from '@/types/api';

const SessionsPage = () => {
  const [sessionId, setSessionId] = useState('test_session');
  const [selectedCar, setSelectedCar] = useState<string | undefined>(undefined);

  const summaryQuery = useQuery<SessionSummary, Error>({
    queryKey: ['summary', sessionId],
    queryFn: () => fetchSessionSummary(sessionId),
    enabled: Boolean(sessionId)
  });

  const lapsQuery = useQuery<LapResponse, Error>({
    queryKey: ['laps', sessionId, selectedCar],
    queryFn: () => fetchLapData(sessionId, selectedCar),
    enabled: Boolean(sessionId)
  });

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
          {lapsQuery.isFetching ? 'Loading telemetry…' : lapsQuery.data ? `${lapsQuery.data.total} frames loaded` : ''}
        </span>
      </section>

      <TelemetryTable
        laps={lapsQuery.data}
        selectedCar={selectedCar}
        onCarChange={setSelectedCar}
      />

      <Charts laps={lapsQuery.data} summary={summaryQuery.data} />

      {sessionId && <StrategyPanel sessionId={sessionId} />}
    </div>
  );
};

export default SessionsPage;
