import { useEffect, useState } from "react";

export default function LiveTelemetry() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const updateStats = async () => {
      // Verifica se a ponte do pywebview está pronta
      if (window.pywebview && window.pywebview.api) {
        try {
          const stats = await window.pywebview.api.get_telemetry();
          setData(stats);
        } catch (err) {
          console.error("Erro ao buscar telemetria:", err);
        }
      }
    };

    // Atualiza a cada 1000ms (1 segundo)
    const interval = setInterval(updateStats, 1000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return null; // Aguarda o primeiro carregamento

  return (
    <div className="absolute inset-0 pointer-events-none z-40 overflow-hidden">
      
      {/* Módulo Esquerdo: CPU & RAM REAIS */}
      <div className="absolute bottom-10 left-10 flex flex-col gap-1 border-l border-cyan-500/30 pl-4">
        <h3 className="text-[10px] tracking-[0.2em] text-cyan-400 mb-2 uppercase">Core Diagnostics</h3>
        
        <div className="flex justify-between w-40 text-[10px] text-cyan-500/70 font-mono">
          <span>CPU USAGE</span>
          <span className="text-cyan-300">{data.cpu.usage}%</span>
        </div>
        
        <div className="flex justify-between w-40 text-[10px] text-cyan-500/70 font-mono">
          <span>RAM USED</span>
          <span className="text-cyan-300">{data.ram.used_gb} GB</span>
        </div>

        <div className="flex justify-between w-40 text-[10px] text-cyan-500/70 font-mono">
          <span>UPTIME</span>
          <span className="text-cyan-300">{data.sys.uptime}</span>
        </div>
      </div>

      {/* Módulo Direito: REDE REAL */}
      <div className="absolute bottom-10 right-10 flex flex-col gap-1 items-end border-r border-cyan-500/30 pr-4 text-right">
        <h3 className="text-[10px] tracking-[0.2em] text-cyan-400 mb-2 uppercase">Network Uplink</h3>
        
        <div className="flex justify-between gap-4 text-[10px] text-cyan-500/70 font-mono">
          <span>DOWN:</span>
          <span className="text-cyan-300">{data.net.download_speed}</span>
        </div>

        <div className="flex justify-between gap-4 text-[10px] text-cyan-500/70 font-mono">
          <span>UP:</span>
          <span className="text-cyan-300">{data.net.upload_speed}</span>
        </div>
        
        <div className="text-[10px] text-cyan-600 mt-1">BATTERY: {data.battery.percent}%</div>
      </div>
    </div>
  );
}