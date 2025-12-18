// src/components/LiveTelemetry.jsx
import { useEffect, useState } from "react";

// Sub-componente para um número que muda aleatoriamente
const RandomNumber = ({ min, max, intervalMs, label, unit }) => {
  const [val, setVal] = useState(min);

  useEffect(() => {
    const interval = setInterval(() => {
      setVal(Math.floor(Math.random() * (max - min + 1) + min));
    }, intervalMs);
    return () => clearInterval(interval);
  }, [min, max, intervalMs]);

  return (
    <div className="flex justify-between w-32 text-[10px] text-cyan-500/70 font-mono">
      <span>{label}</span>
      <span className="text-cyan-300">{val}{unit}</span>
    </div>
  );
};

export default function LiveTelemetry() {
  return (
    <div className="absolute inset-0 pointer-events-none z-40 overflow-hidden">
      
      {/* Módulo Esquerdo Inferior: STATUS DE HARDWARE */}
      <div className="absolute bottom-10 left-10 flex flex-col gap-1 border-l border-cyan-500/30 pl-4 animate-[fadeIn_2s_ease-in]">
        <h3 className="text-[10px] tracking-[0.2em] text-cyan-400 mb-2 uppercase">Core Diagnostics</h3>
        <RandomNumber min={40} max={65} intervalMs={2000} label="CPU TEMP" unit="°C" />
        <RandomNumber min={1200} max={4000} intervalMs={150} label="FAN RPM" unit="" />
        <RandomNumber min={12} max={16} intervalMs={5000} label="VOLTAGE" unit="V" />
        
        {/* Barra de gráfico falsa */}
        <div className="flex gap-1 mt-2">
            {[1,2,3,4,5].map(i => (
                <div key={i} className={`h-8 w-2 bg-cyan-500/${i*10 + 20} animate-pulse`}></div>
            ))}
        </div>
      </div>

      {/* Módulo Direito Inferior: STATUS DE REDE */}
      <div className="absolute bottom-10 right-10 flex flex-col gap-1 items-end border-r border-cyan-500/30 pr-4 text-right animate-[fadeIn_2s_ease-in]">
        <h3 className="text-[10px] tracking-[0.2em] text-cyan-400 mb-2 uppercase">Network Uplink</h3>
        <RandomNumber min={12} max={45} intervalMs={800} label="LATENCY" unit="ms" />
        <RandomNumber min={800} max={999} intervalMs={1200} label="PACKETS" unit="/s" />
        <div className="text-[10px] text-cyan-600 mt-1">ENCRYPTION: AES-256</div>
        
        {/* Visualizador de Onda falso (SVG animado) */}
        <svg className="w-32 h-8 mt-2 opacity-50" viewBox="0 0 100 20">
            <path d="M0 10 Q 10 0, 20 10 T 40 10 T 60 10 T 80 10 T 100 10" fill="none" stroke="cyan" strokeWidth="1">
                <animate attributeName="d" 
                    dur="2s" 
                    repeatCount="indefinite"
                    values="M0 10 Q 10 0, 20 10 T 40 10 T 60 10 T 80 10 T 100 10;
                            M0 10 Q 10 20, 20 10 T 40 10 T 60 10 T 80 10 T 100 10;
                            M0 10 Q 10 0, 20 10 T 40 10 T 60 10 T 80 10 T 100 10" 
                />
            </path>
        </svg>
      </div>

    </div>
  );
}