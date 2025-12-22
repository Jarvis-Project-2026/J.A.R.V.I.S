import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import * as THREE from "three"; 

// --- CAMADA DE PARTÍCULAS ---
function ParticlesLayer({ 
  count, 
  radius, 
  size, 
  targetColor, 
  baseSpeed, 
  speedMultiplier, 
  opacity, 
  isSpeaking, 
  isCritical 
}) {
  const pointsRef = useRef();
  const materialRef = useRef(); 

  // Gera posições iniciais
  const { positions, initialPositions } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const initialPositions = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      
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
      
      // 1. ROTAÇÃO
      const criticalSpeedBoost = isCritical ? 2.0 : 1.0;
      pointsRef.current.rotation.y += delta * baseSpeed * speedMultiplier * criticalSpeedBoost;

      const currentPositions = pointsRef.current.geometry.attributes.position.array;
      
      // 2. SIMULAÇÃO DE VOZ (O Pulo do Gato - VERSÃO SUAVE)
      let simulatedIntensity = 0;
      
      if (isSpeaking) {
        // CORREÇÃO: Reduzimos a velocidade (time * X) e suavizamos a onda
        // Antes estava time * 15 (muito rápido). Agora usamos ondas lentas sobrepostas.
        const slowWave = Math.sin(time * 2); // Respiração base
        const fastWave = Math.cos(time * 6); // Modulação da fala
        
        // Normalizamos para ficar entre 0.0 e 0.8
        simulatedIntensity = (Math.abs(slowWave * 0.6 + fastWave * 0.4)) + 0.1;
      }
      
      // Se estiver crítico, mantemos a tensão
      if (isCritical) {
         simulatedIntensity += 0.2; 
      }

      const hasActivity = isSpeaking || isCritical;

      // 3. FÍSICA DAS PARTÍCULAS
      for (let i = 0; i < count; i++) {
        const i3 = i * 3;
        
        const ix = initialPositions[i3];
        const iy = initialPositions[i3 + 1];
        const iz = initialPositions[i3 + 2];

        let targetX = ix;
        let targetY = iy;
        let targetZ = iz;

        if (hasActivity) {
          const vibration = isCritical ? Math.sin(time * 15 + i) * 0.05 : 0;
          
          // Isso evita que a esfera "exploda" visualmente
          const voiceWave = isSpeaking 
            ? Math.sin(iy * 2.0 + time * 3.0) * (0.25 * simulatedIntensity) 
            : 0;

          const pulse = 1 + voiceWave + vibration;
          
          targetX = ix * pulse;
          targetY = iy * pulse;
          targetZ = iz * pulse;
        }

        // LERP (Suavização do movimento)
        const smoothingFactor = 0.03;

        currentPositions[i3] += (targetX - currentPositions[i3]) * smoothingFactor;
        currentPositions[i3 + 1] += (targetY - currentPositions[i3 + 1]) * smoothingFactor;
        currentPositions[i3 + 2] += (targetZ - currentPositions[i3 + 2]) * smoothingFactor;
      }

      pointsRef.current.geometry.attributes.position.needsUpdate = true;
    }

    // 4. COR
    if (materialRef.current) {
      const targetColorObj = new THREE.Color(targetColor);
      materialRef.current.color.lerp(targetColorObj, 0.02);
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
        ref={materialRef}
        size={size}
        color={targetColor}
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
export default function ParticleSphere({ state = "idle", isCritical = false }) {
  const isSpeaking = state === 'speaking';
  
  // Não precisamos mais do hook de áudio real, a simulação interna cuida disso.

  const config = {
    idle: { speed: 0.2, coreColor: "#00d0ff", bloom: 1.0 },
    listening: { speed: 0.1, coreColor: "#ffffff", bloom: 0.5 },
    speaking: { speed: 1.5, coreColor: "#00eaff", bloom: 2.5 }, // Velocidade alta quando fala
  };
  
  let activeConfig = config[state] || config.idle;

  // Lógica de Override Crítico
  let coreTargetColor = activeConfig.coreColor;
  let auraTargetColor = "#0066ff"; 
  let targetBloom = activeConfig.bloom;

  if (isCritical) {
    coreTargetColor = "#ff0000"; 
    auraTargetColor = "#ff3300"; 
    targetBloom = 3.5; 
  }

  return (
    <div className="w-full h-full relative z-20">
      <Canvas camera={{ position: [0, 0, 6], fov: 45 }}>
        
        {/* Núcleo */}
        <ParticlesLayer 
          count={4000} 
          radius={1.6} 
          size={0.02} 
          targetColor={coreTargetColor} 
          baseSpeed={0.2} 
          speedMultiplier={activeConfig.speed} 
          opacity={0.9} 
          isSpeaking={isSpeaking}
          isCritical={isCritical}
        />
        
        {/* Aura */}
        <ParticlesLayer 
          count={1500} 
          radius={3.0} 
          size={0.03} 
          targetColor={auraTargetColor}
          baseSpeed={0.1} 
          speedMultiplier={activeConfig.speed} 
          opacity={0.4} 
          isSpeaking={isSpeaking}
          isCritical={isCritical}
        />
        
        <EffectComposer disableNormalPass>
          <Bloom 
            intensity={targetBloom} 
            luminanceThreshold={0.2} 
          />
        </EffectComposer>
      </Canvas>
    </div>
  );
}