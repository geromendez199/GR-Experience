import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';

import { compareLap } from '@/lib/api';
import { TrainingComparisonRequest, TrainingComparisonResponse } from '@/types/api';

interface TrainingCompareProps {
  sessionId: string;
  cars: string[];
  lapsAvailable: number[];
}

const TrainingCompare = ({ sessionId, cars, lapsAvailable }: TrainingCompareProps) => {
  const [form, setForm] = useState<TrainingComparisonRequest>({
    session_id: sessionId,
    ideal_car_id: cars[0] ?? '',
    reference_car_id: cars[1] ?? cars[0] ?? '',
    lap: lapsAvailable[0] ?? 1,
    metric: 'speed_kph'
  });

  const { data, mutateAsync, isPending } = useMutation<
    TrainingComparisonResponse,
    Error,
    TrainingComparisonRequest
  >({
    mutationFn: compareLap
  });

  return (
    <section style={{ background: 'rgba(255,255,255,0.04)', borderRadius: '1rem', padding: '1.5rem' }}>
      <h2 style={{ marginTop: 0 }}>Dynamic Time Warping Comparison</h2>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          mutateAsync({ ...form, session_id: sessionId });
        }}
        style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}
      >
        <label>
          Ideal car
          <select
            value={form.ideal_car_id}
            onChange={(event) => setForm((prev) => ({ ...prev, ideal_car_id: event.target.value }))}
          >
            {cars.map((car) => (
              <option key={car} value={car}>
                {car}
              </option>
            ))}
          </select>
        </label>
        <label>
          Reference car
          <select
            value={form.reference_car_id}
            onChange={(event) => setForm((prev) => ({ ...prev, reference_car_id: event.target.value }))}
          >
            {cars.map((car) => (
              <option key={car} value={car}>
                {car}
              </option>
            ))}
          </select>
        </label>
        <label>
          Lap
          <select
            value={form.lap}
            onChange={(event) => setForm((prev) => ({ ...prev, lap: Number(event.target.value) }))}
          >
            {lapsAvailable.map((lap) => (
              <option key={lap} value={lap}>
                {lap}
              </option>
            ))}
          </select>
        </label>
        <label>
          Metric
          <select
            value={form.metric}
            onChange={(event) => setForm((prev) => ({ ...prev, metric: event.target.value }))}
          >
            <option value="speed_kph">Speed</option>
            <option value="throttle">Throttle</option>
            <option value="brake">Brake</option>
          </select>
        </label>
        <button
          type="submit"
          disabled={isPending}
          style={{
            alignSelf: 'end',
            background: 'var(--accent)',
            color: '#fff',
            border: 'none',
            padding: '0.6rem 1rem',
            borderRadius: '0.5rem',
            cursor: 'pointer'
          }}
        >
          {isPending ? 'Comparing…' : 'Compare'}
        </button>
      </form>
      {data && (
        <div style={{ marginTop: '1.5rem' }}>
          <h3>Recommendations</h3>
          <ul>
            {data.recommendations.map((recommendation) => (
              <li key={recommendation}>{recommendation}</li>
            ))}
          </ul>
          <p>
            Alignment distance: <strong>{data.distance.toFixed(2)}</strong>
          </p>
        </div>
      )}
    </section>
  );
};

export default TrainingCompare;
