import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';

import { simulateStrategy } from '@/lib/api';
import { StrategyResponse } from '@/types/api';

interface StrategyPanelProps {
  sessionId: string;
}

const StrategyPanel = ({ sessionId }: StrategyPanelProps) => {
  const [targetPosition, setTargetPosition] = useState<number | undefined>(undefined);
  const { data, mutateAsync, isPending } = useMutation<StrategyResponse, Error, void>(async () => {
    return simulateStrategy(sessionId, targetPosition);
  });

  return (
    <section style={{ background: 'rgba(255,255,255,0.04)', borderRadius: '1rem', padding: '1.5rem' }}>
      <header style={{ display: 'flex', justify-content: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>Strategy Simulation</h2>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <label style={{ fontSize: '0.9rem' }}>
            Target Position
            <input
              type="number"
              min={1}
              value={targetPosition ?? ''}
              onChange={(event) =>
                setTargetPosition(event.target.value ? Number(event.target.value) : undefined)
              }
              style={{
                marginLeft: '0.5rem',
                padding: '0.3rem 0.5rem',
                borderRadius: '0.4rem',
                border: '1px solid rgba(255,255,255,0.1)',
                background: 'rgba(0,0,0,0.4)',
                color: 'white'
              }}
            />
          </label>
          <button
            onClick={() => mutateAsync()}
            disabled={isPending}
            style={{
              background: 'var(--accent)',
              color: '#fff',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              cursor: 'pointer'
            }}
          >
            {isPending ? 'Simulating…' : 'Run Simulation'}
          </button>
        </div>
      </header>
      {data && (
        <div style={{ marginTop: '1.5rem' }}>
          <p style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
            Recommended pit window: <strong>{data.pit_window[0]} - {data.pit_window[1]}</strong>
          </p>
          <p>
            Expected gain: <strong>{data.expected_gain_s.toFixed(2)}s</strong> | Confidence:{' '}
            <strong>{(data.confidence * 100).toFixed(0)}%</strong>
          </p>
          <h3>Notes</h3>
          <ul>
            {data.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
          <h3>Evaluated windows</h3>
          <div
            style={{
              display: 'grid',
              gap: '0.75rem',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))'
            }}
          >
            {data.stint_summary.map((stint) => (
              <article
                key={`${stint.pit_window[0]}-${stint.pit_window[1]}`}
                style={{
                  background: 'rgba(0,0,0,0.3)',
                  borderRadius: '0.75rem',
                  padding: '0.75rem'
                }}
              >
                <h4 style={{ marginTop: 0 }}>Laps {stint.pit_window[0]}-{stint.pit_window[1]}</h4>
                <p>Gain: {stint.expected_gain_s.toFixed(2)}s</p>
                <p>Confidence: {(stint.confidence * 100).toFixed(0)}%</p>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};

export default StrategyPanel;
