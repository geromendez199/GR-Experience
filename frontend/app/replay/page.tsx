"use client";

import { Canvas } from "@react-three/fiber";
import dynamic from "next/dynamic";
import { Suspense, useMemo } from "react";

const OrbitControls = dynamic(() => import("@react-three/drei").then((mod) => mod.OrbitControls), {
  ssr: false
});

function Track() {
  const points = useMemo(() => {
    return [
      [-20, 0, -40],
      [30, 0, -20],
      [40, 0, 20],
      [0, 0, 40],
      [-40, 0, 10]
    ];
  }, []);

  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[120, 120]} />
        <meshStandardMaterial color="#111820" />
      </mesh>
      {points.map(([x, y, z], index) => (
        <mesh key={index} position={[x, y + 0.1, z]}>
          <boxGeometry args={[4, 0.2, 8]} />
          <meshStandardMaterial color={index % 2 === 0 ? "#ff4655" : "#ffffff"} />
        </mesh>
      ))}
    </group>
  );
}

function Car() {
  return (
    <mesh position={[0, 1, 0]}>
      <boxGeometry args={[2, 1, 4]} />
      <meshStandardMaterial color="#ff4655" />
    </mesh>
  );
}

export default function ReplayPage() {
  return (
    <main>
      <h1>Replay 3D</h1>
      <p>Visualización conceptual del trazado y vehículo utilizando Three.js.</p>
      <div style={{ height: "500px", borderRadius: "1rem", overflow: "hidden", marginTop: "1.5rem" }}>
        <Canvas camera={{ position: [15, 25, 35], fov: 45 }}>
          <ambientLight intensity={0.4} />
          <directionalLight position={[10, 20, 15]} intensity={0.8} />
          <Suspense fallback={null}>
            <Track />
            <Car />
            <OrbitControls enablePan enableZoom enableRotate />
          </Suspense>
        </Canvas>
      </div>
    </main>
  );
}
