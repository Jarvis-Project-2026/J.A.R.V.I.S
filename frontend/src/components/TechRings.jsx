// src/components/TechRings.jsx
export default function TechRings({ state }) {
  // A velocidade e cor mudam sutilmente baseados no estado
  const isSpeaking = state === 'speaking';
  const colorClass = isSpeaking ? "border-cyan-400" : "border-cyan-500/30";
  
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
      
      {/* --- ANEL 1: O MAIS EXTERNO (Lento e Fino) --- */}
      <div className="absolute w-[850px] h-[850px] opacity-20 animate-[spin_60s_linear_infinite]">
        <div className={`w-full h-full border border-dashed ${colorClass} rounded-full`}></div>
      </div>

      {/* --- ANEL 2: CONTRA-ROTATIVO (Tracejado Grosso) --- */}
      <div className="absolute w-[750px] h-[750px] opacity-30 animate-[spin_40s_linear_infinite_reverse]">
        <div className={`w-full h-full border-2 border-dotted ${colorClass} rounded-full`}></div>
        {/* Marcadores decorativos nos 4 pontos cardeais */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-8 bg-cyan-500"></div>
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-2 h-8 bg-cyan-500"></div>
        <div className="absolute left-0 top-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-2 bg-cyan-500"></div>
        <div className="absolute right-0 top-1/2 translate-x-1/2 -translate-y-1/2 w-8 h-2 bg-cyan-500"></div>
      </div>

      {/* --- ANEL 3: O "RETÍCULO" (Fixo ou muito lento) --- */}
      <div className="absolute w-[650px] h-[650px] opacity-40">
         <div className={`w-full h-full border border-cyan-500/20 rounded-full`}></div>
         {/* Triângulos de mira nos cantos (SVG simples) */}
         <svg className="absolute top-0 left-0 w-full h-full animate-pulse" viewBox="0 0 100 100">
            <path d="M 49 5 L 50 2 L 51 5" fill="cyan" />
            <path d="M 49 95 L 50 98 L 51 95" fill="cyan" />
            <path d="M 5 49 L 2 50 L 5 51" fill="cyan" />
            <path d="M 95 49 L 98 50 L 95 51" fill="cyan" />
         </svg>
      </div>

      {/* --- ANEL 4: O REATOR DE ENERGIA (Gira rápido quando fala) --- */}
      {/* Esse anel reage drasticamente ao estado SPEAK */}
      <div className={`absolute w-[580px] h-[580px] opacity-60 transition-all duration-1000 ${isSpeaking ? 'animate-[spin_2s_linear_infinite] border-cyan-300' : 'animate-[spin_20s_linear_infinite] border-cyan-600/40'}`}>
        {/* Usamos border-r e border-l transparentes para criar arcos quebrados */}
        <div className="w-full h-full border-4 border-t-cyan-500 border-b-cyan-500 border-l-transparent border-r-transparent rounded-full shadow-[0_0_15px_cyan]"></div>
      </div>

    </div>
  );
}