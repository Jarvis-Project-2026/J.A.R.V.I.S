import { useEffect, useState } from "react";

export default function StartupScreen({ onComplete }) {
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);

  // Gerador de texto aleatório para "encher linguiça" técnica
  const generateRandomHex = () => `0x${Math.floor(Math.random() * 16777215).toString(16).toUpperCase()}`;

  useEffect(() => {
    // Loop de progresso
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(onComplete, 800); 
          return 100;
        }
        // Avança de forma não-linear (às vezes rápido, às vezes trava) para parecer real
        const jump = Math.random() > 0.8 ? 15 : 2;
        return Math.min(prev + jump, 100);
      });

      // Adiciona logs técnicos freneticamente
      setLogs(prev => [`[SYS] CHECK ${generateRandomHex()}... OK`, ...prev.slice(0, 5)]);
    }, 100);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <div className="fixed inset-0 bg-black z-[100] flex flex-col items-center justify-center text-cyan-500 font-mono overflow-hidden scanline tech-grid">
      
      {/* --- LAYER DE BACKGROUND: Scanline descendo --- */}
      <div className="scan-moving"></div>

      {/* --- CANTOS TÉCNICOS (HUD CORNERS) --- */}
      <div className="absolute top-0 left-0 p-8 border-l-2 border-t-2 border-cyan-500/50 w-32 h-32 m-4 opacity-50"></div>
      <div className="absolute top-0 right-0 p-8 border-r-2 border-t-2 border-cyan-500/50 w-32 h-32 m-4 opacity-50 text-right text-xs">
        SYS.CHK.V.4.0.2<br/>SECURE CONN
      </div>
      <div className="absolute bottom-0 left-0 p-8 border-l-2 border-b-2 border-cyan-500/50 w-32 h-32 m-4 opacity-50 text-xs flex items-end">
        MEM: 64TB<br/>CPU: 128 CORES
      </div>
      <div className="absolute bottom-0 right-0 p-8 border-r-2 border-b-2 border-cyan-500/50 w-32 h-32 m-4 opacity-50"></div>


      {/* --- CONTEÚDO CENTRAL --- */}
      <div className="relative z-10 flex flex-col items-center">
        
        {/* Logo com efeito Glitch leve */}
        <div className="mb-12 text-center group">
          <h1 className="text-7xl font-bold tracking-[0.2em] text-white drop-shadow-[0_0_15px_rgba(0,255,255,0.8)] opacity-90 group-hover:animate-glitch transition-all cursor-default">
            J.A.R.V.I.S.
          </h1>
          <h2 className="text-xl tracking-[0.8em] text-cyan-400 opacity-60 mt-2 border-b border-cyan-500/30 pb-2 inline-block">
            System V1.0
          </h2>
        </div>

        {/* Loader Circular Sofisticado + Barra Linear */}
        <div className="w-96 relative">
            
            {/* Texto de Status */}
            <div className="flex justify-between text-xs uppercase tracking-widest mb-2 opacity-80 text-cyan-300">
                <span>Loading Core Modules</span>
                <span>{Math.floor(progress)}%</span>
            </div>

            {/* A Barra de Progresso */}
            <div className="h-1 w-full bg-cyan-900/30 relative overflow-hidden">
                <div 
                    className="h-full bg-cyan-400 shadow-[0_0_20px_#22d3ee]"
                    style={{ width: `${progress}%` }}
                ></div>
            </div>

            {/* Decoração abaixo da barra */}
            <div className="mt-1 flex justify-between opacity-40">
                <div className="h-1 w-1 bg-cyan-500"></div>
                <div className="h-1 w-full mx-1 bg-cyan-500/20"></div>
                <div className="h-1 w-1 bg-cyan-500"></div>
            </div>

        </div>

        {/* --- TERMINAL DE DADOS (Efeito Matrix/Hacker) --- */}
        <div className="mt-8 font-mono text-[10px] text-cyan-700 w-96 h-24 overflow-hidden border-l-2 border-cyan-900/50 pl-2 flex flex-col justify-end opacity-70">
            {logs.map((log, i) => (
                <div key={i} className="whitespace-nowrap">{log}</div>
            ))}
        </div>

      </div>

    </div>
  );
}