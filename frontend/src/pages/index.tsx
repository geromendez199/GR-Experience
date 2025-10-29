import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { fetchSessionSummary } from '@/lib/api';
import { SessionSummary } from '@/types/api';

const IndexPage = () => {
  const [sessionId, setSessionId] = useState('test_session');
  const { data, isFetching, error } = useQuery<SessionSummary, Error>({
    queryKey: ['summary', sessionId],
    queryFn: () => fetchSessionSummary(sessionId),
    enabled: Boolean(sessionId)
  });

  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <section style={{ background: 'rgba(255,255,255,0.04)', borderRadius: '1rem', padding: '1.5rem' }}>
        <h2>Welcome to GR-Experience</h2>
        <p>
          Monitor Toyota GR Cup telemetry, run strategy simulations and replay sessions in 3D. Start by selecting a
          session identifier to load normalized data from the ingestion pipeline.
        </p>
        <label style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          Session ID
          <input
            value={sessionId}
            onChange={(event) => setSessionId(event.target.value)}
            placeholder="grcup_barber_2025"
            style={{ padding: '0.5rem 0.8rem', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(0,0,0,0.4)', color: '#fff' }}
          />
        </label>
        {error && <p style={{ color: '#ff8a80' }}>Failed to load session summary: {error.message}</p>}
      </section>
      {data && !isFetching && (
        <section style={{ background: 'rgba(255,255,255,0.04)', borderRadius: '1rem', padding: '1.5rem' }}>
          <h3>Session KPIs</h3>
          <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
            <article style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '0.75rem' }}>
              <h4>Fastest Lap</h4>
              {Object.entries(data.fastest_lap).map(([car, lapTime]) => (
                <p key={car}>
                  {car}: {lapTime.toFixed(2)}s
                </p>
              ))}
            </article>
            <article style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '0.75rem' }}>
              <h4>Valid laps</h4>
              <p>{data.valid_laps}</p>
            </article>
            <article style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '0.75rem' }}>
              <h4>Detected stints</h4>
              <p>{data.stints.length}</p>
            </article>
          </div>
        </section>
      )}
    </div>
  );
};

export default IndexPage;
