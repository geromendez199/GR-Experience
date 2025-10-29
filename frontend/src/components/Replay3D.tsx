import dynamic from 'next/dynamic';
import { Suspense, useMemo } from 'react';
import { Color, Vector3 } from 'three';

import { TelemetryFrame } from '@/types/api';

const Canvas = dynamic(
  () => import('@react-three/fiber').then((mod) => mod.Canvas),
  { ssr: false }
);
const OrbitControls = dynamic(
  () => import('@react-three/drei').then((mod) => mod.OrbitControls),
  { ssr: false }
);

interface Replay3DProps {
  laps: TelemetryFrame[];
}

const Replay3D = ({ laps }: Replay3DProps) => {
  const points = useMemo(() => {
    if (!laps.length) {
      return [];
    }
    return laps.map((frame, index) => {
      const theta = ((frame.lap * 3 + frame.sector) / (Math.max(...laps.map((item) => item.lap)) * 3)) * Math.PI * 2;
      const radius = 40 + frame.speed_kph * 0.1;
      const x = Math.cos(theta) * radius;
      const z = Math.sin(theta) * radius;
      const y = frame.throttle * 0.02;
      return new Vector3(x, y, z);
    });
  }, [laps]);

  return (
    <div style={{ height: 500, borderRadius: '1rem', overflow: 'hidden', background: 'rgba(0,0,0,0.4)' }}>
      <Suspense fallback={<p style={{ padding: '1rem' }}>Loading replay…</p>}>
        <Canvas camera={{ position: [0, 80, 120], fov: 45 }}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[50, 100, 50]} intensity={1} />
          <group>
            <TrackLine points={points} color={new Color('#ff4d4f')} />
            <GhostCar points={points} />
          </group>
          <OrbitControls enablePan enableZoom />
        </Canvas>
      </Suspense>
    </div>
  );
};

const TrackLine = ({ points, color }: { points: Vector3[]; color: Color }) => {
  if (!points.length) {
    return null;
  }
  return (
    <line>
      <bufferGeometry attach="geometry">
        <bufferAttribute
          attachObject={["attributes", "position"]}
          args={[new Float32Array(points.flatMap((point) => point.toArray())), 3]}
        />
      </bufferGeometry>
      <lineBasicMaterial attach="material" color={color} linewidth={2} />
    </line>
  );
};

const GhostCar = ({ points }: { points: Vector3[] }) => {
  if (!points.length) {
    return null;
  }
  const finalPoint = points[points.length - 1];
  return (
    <mesh position={finalPoint.toArray()}>
      <sphereGeometry args={[2.2, 32, 32]} />
      <meshStandardMaterial color="#f0f3f7" emissive="#ff4d4f" emissiveIntensity={0.4} />
    </mesh>
  );
};

export default Replay3D;
