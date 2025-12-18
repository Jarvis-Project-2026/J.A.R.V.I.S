import { useRef, useMemo, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { EffectComposer, Bloom, ChromaticAberration, Noise, Vignette } from "@react-three/postprocessing";
import { OrbitControls, Sparkles } from "@react-three/drei";

// --- Função Auxiliar ---
function generateSpherePoints(count, radius) {
  const points = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const i3 = i * 3;
    const theta = THREE.MathUtils.randFloatSpread(360);
    const phi = THREE.MathUtils.randFloatSpread(360);
    
    const x = radius * Math.sin(theta) * Math.cos(phi);
    const y = radius * Math.sin(theta) * Math.sin(phi);
    const z = radius * Math.cos(theta);
    
    points[i3] = x;
    points[i3 + 1] = y;
    points[i3 + 2] = z;
  }
  return points;
}

// --- Componente de Camada ---
function ParticlesLayer({ count, radius, size, color, baseSpeed, opacity, speedMultiplier, isSpeaking }) {
  const pointsRef = useRef();
  const mouseRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event) => {
      mouseRef.current.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouseRef.current.y = -(event.clientY / window.innerHeight) * 2 + 1;
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const initialPositions = useMemo(() => generateSpherePoints(count, radius), [count, radius]);
  const currentPositions = useMemo(() => new Float32Array(initialPositions), [initialPositions]);

  useFrame((state, delta) => {
    if (pointsRef.current) {
      const time = state.clock.elapsedTime;
      const geometry = pointsRef.current.geometry;
      
      const currentSpeed = baseSpeed * speedMultiplier;
      pointsRef.current.rotation.y -= delta * currentSpeed * 0.2;
      
      pointsRef.current.rotation.x = THREE.MathUtils.lerp(pointsRef.current.rotation.x, mouseRef.current.y * 0.2, 0.05);
      pointsRef.current.rotation.z = THREE.MathUtils.lerp(pointsRef.current.rotation.z, -mouseRef.current.x * 0.2, 0.05);

      if (isSpeaking) {
         for (let i = 0; i < count; i++) {
            const i3 = i * 3;
            const ox = initialPositions[i3];
            const oy = initialPositions[i3 + 1];
            const oz = initialPositions[i3 + 2];

            const wave1 = Math.sin(oy * 2.5 + time * 8.0) * 0.3;
            const wave2 = Math.cos(ox * 2.0 + time * 6.0) * 0.2;
            const noise = Math.sin(oz * 5.0 + time * 3.0) * 0.1;
            const distortion = 1 + (wave1 + wave2 + noise) * 0.4;

            currentPositions[i3] = ox * distortion;
            currentPositions[i3 + 1] = oy * distortion;
            currentPositions[i3 + 2] = oz * distortion;
         }
      } else {
        for (let i = 0; i < count; i++) {
          const i3 = i * 3;
          currentPositions[i3] += (initialPositions[i3] - currentPositions[i3]) * 0.05;
          currentPositions[i3+1] += (initialPositions[i3+1] - currentPositions[i3+1]) * 0.05;
          currentPositions[i3+2] += (initialPositions[i3+2] - currentPositions[i3+2]) * 0.05;
        }
      }

      geometry.attributes.position.array = currentPositions;
      geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={currentPositions.length / 3} array={currentPositions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial
        size={size}
        color={new THREE.Color(color).multiplyScalar(isSpeaking ? 3.0 : 1.5)} 
        transparent opacity={opacity} blending={THREE.AdditiveBlending}
        sizeAttenuation={true} toneMapped={false}
      />
    </points>
  );
}

// --- Componente Principal ---
export default function ParticleSphere({ state = "idle" }) {
  const isSpeaking = state === 'speaking';
  const config = {
    idle: { speed: 1.0, coreColor: "#4fd1c5", bloom: 1.5 },
    listening: { speed: 0.2, coreColor: "#ffffff", bloom: 0.8 },
    speaking: { speed: 1.5, coreColor: "#00eaff", bloom: 3.0 },
  };
  const activeConfig = config[state] || config.idle;

  return (
    <div className="w-full h-full relative z-20 transition-all duration-700 ease-in-out">
      <Canvas camera={{ position: [0, 0, 6], fov: 45 }} gl={{ alpha: true }}>
        <ambientLight intensity={0.5} />

        <ParticlesLayer count={5000} radius={1.6} size={0.025} color={activeConfig.coreColor} baseSpeed={0.2} speedMultiplier={activeConfig.speed} opacity={0.95} isSpeaking={isSpeaking} />
        <ParticlesLayer count={2000} radius={3.2} size={0.03} color="#00d0ff" baseSpeed={0.05} speedMultiplier={activeConfig.speed} opacity={0.5} isSpeaking={isSpeaking} />
        <Sparkles count={100} scale={12} size={4} speed={0.4} opacity={0.2} color="#00d0ff" />

        {/* --- O SEGREDO DO "LOOK" DE FILME --- */}
        <EffectComposer disableNormalPass>
          <Bloom luminanceThreshold={0.2} luminanceSmoothing={0.9} height={300} intensity={activeConfig.bloom} />
          <ChromaticAberration offset={[0.002, 0.002]} />
          <Noise opacity={0.02} />
          <Vignette eskil={false} offset={0.1} darkness={1.1} />
        </EffectComposer>

      </Canvas>
    </div>
  );
}