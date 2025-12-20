import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import * as THREE from "three";
// Importação correta usando o alias
import { useAudioAnalyzer } from "@/hook/useAudioAnalyzer";

// --- CAMADA DE PARTÍCULAS COM FÍSICA DE RETORNO ---
function ParticlesLayer({ count, radius, size, color, baseSpeed, speedMultiplier, opacity, isSpeaking, audioIntensity }) {
  const pointsRef = useRef();

  // Gera posições iniciais (Esfera Perfeita)
  const { positions, initialPositions } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const initialPositions = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      
      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);

      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;

      initialPositions[i * 3] = x;
      initialPositions[i * 3 + 1] = y;
      initialPositions[i * 3 + 2] = z;
    }
    return { positions, initialPositions };
  }, [count, radius]);

  useFrame((state, delta) => {
    if (pointsRef.current) {
      const time = state.clock.elapsedTime;
      
      // Rotação constante da esfera
      pointsRef.current.rotation.y += delta * baseSpeed * speedMultiplier;

      const currentPositions = pointsRef.current.geometry.attributes.position.array;
      
      // Verificamos se há som significativo para distorcer
      const hasSound = isSpeaking && audioIntensity > 0.01;

      for (let i = 0; i < count; i++) {
        const i3 = i * 3;
        
        // Posição Original (Alvo quando está quieto)
        const ix = initialPositions[i3];
        const iy = initialPositions[i3 + 1];
        const iz = initialPositions[i3 + 2];

        let targetX = ix;
        let targetY = iy;
        let targetZ = iz;

        // Se tiver som, calculamos a Posição Distorcida (Alvo quando fala)
        if (hasSound) {
          // Cria ondas baseadas na posição Y e no tempo
          const wave = Math.sin(iy * 3.0 + time * 5.0) * (0.3 * audioIntensity);
          const pulse = 1 + wave;
          
          targetX = ix * pulse;
          targetY = iy * pulse;
          targetZ = iz * pulse;
        }

        // FÍSICA DE MOLA (LERP):
        // Move a posição atual em direção ao alvo suavemente (fator 0.1)
        // Isso faz a esfera "desamassar" suavemente quando o som para.
        currentPositions[i3] += (targetX - currentPositions[i3]) * 0.1;
        currentPositions[i3 + 1] += (targetY - currentPositions[i3 + 1]) * 0.1;
        currentPositions[i3 + 2] += (targetZ - currentPositions[i3 + 2]) * 0.1;
      }

      // Avisa ao Three.js que as posições mudaram
      pointsRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={size}
        color={color}
        transparent
        opacity={opacity}
        blending={THREE.AdditiveBlending}
        sizeAttenuation={true}
        depthWrite={false}
      />
    </points>
  );
}

// --- COMPONENTE PRINCIPAL ---
export default function ParticleSphere({ state = "idle" }) {
  const isSpeaking = state === 'speaking';
  
  // Captura o volume real (ou 0 se silêncio)
  const audioIntensity = useAudioAnalyzer(isSpeaking);

  const config = {
    idle: { speed: 0.2, coreColor: "#00d0ff", bloom: 1.0 },
    listening: { speed: 0.1, coreColor: "#ffffff", bloom: 0.5 },
    speaking: { speed: 1.5, coreColor: "#00eaff", bloom: 2.5 },
  };
  
  const activeConfig = config[state] || config.idle;

  return (
    <div className="w-full h-full relative z-20">
      <Canvas camera={{ position: [0, 0, 6], fov: 45 }}>
        
        {/* Núcleo denso */}
        <ParticlesLayer 
          count={4000} 
          radius={1.6} 
          size={0.02} 
          color={activeConfig.coreColor} 
          baseSpeed={0.2} 
          speedMultiplier={activeConfig.speed} 
          opacity={0.9} 
          isSpeaking={isSpeaking}
          audioIntensity={audioIntensity} 
        />
        
        {/* Aura externa */}
        <ParticlesLayer 
          count={1500} 
          radius={3.0} 
          size={0.03} 
          color="#0066ff" 
          baseSpeed={0.1} 
          speedMultiplier={activeConfig.speed} 
          opacity={0.4} 
          isSpeaking={isSpeaking}
          audioIntensity={audioIntensity * 0.5} 
        />
        
        <EffectComposer disableNormalPass>
          <Bloom 
            intensity={activeConfig.bloom} 
            luminanceThreshold={0.2} 
          />
        </EffectComposer>
      </Canvas>
    </div>
  );
}