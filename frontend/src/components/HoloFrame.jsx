export default function HoloFrame() {
  return (
    <div className="fixed inset-0 pointer-events-none z-10 p-4">
      
      {/* --- BORDA SUPERIOR --- */}
      {/* Linha longa com gap no meio para o texto */}
      <div className="absolute top-4 left-4 right-4 h-px bg-gradient-to-r from-transparent via-cyan-900 to-transparent opacity-50"></div>
      
      {/* Marcadores Centrais Superiores */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-8 border-b border-cyan-500/30 flex justify-between items-end px-2 pb-1">
        <div className="w-1 h-1 bg-cyan-500"></div>
        <div className="text-[8px] tracking-[0.5em] text-cyan-700">OPTICAL SENSORS ONLINE</div>
        <div className="w-1 h-1 bg-cyan-500"></div>
      </div>

      {/* --- LATERAIS (Conectores Verticais) --- */}
      <div className="absolute top-1/4 bottom-1/4 left-8 w-px bg-gradient-to-b from-transparent via-cyan-800 to-transparent opacity-30"></div>
      <div className="absolute top-1/4 bottom-1/4 right-8 w-px bg-gradient-to-b from-transparent via-cyan-800 to-transparent opacity-30"></div>

      {/* Réguas de Altitude/Nível (Detalhe Tático) */}
      <div className="absolute right-10 top-1/2 -translate-y-1/2 flex flex-col gap-1 opacity-40">
        {[...Array(10)].map((_, i) => (
            <div key={i} className={`h-px bg-cyan-500 ${i === 4 ? 'w-6 bg-cyan-300' : 'w-3'}`}></div>
        ))}
      </div>

      {/* --- BORDA INFERIOR (Base) --- */}
      <div className="absolute bottom-4 left-10 right-10 h-px bg-cyan-900/40 flex items-center justify-center">
         {/* Detalhe no meio da linha */}
         <div className="w-32 h-1 bg-cyan-500/20"></div>
      </div>

      {/* Cantoneiras Decorativas (SVG) */}
      <svg className="absolute inset-0 w-full h-full opacity-30">
        {/* Canto Superior Esquerdo */}
        <path d="M 20 100 L 20 20 L 100 20" fill="none" stroke="cyan" strokeWidth="1" />
        {/* Canto Superior Direito */}
        <path d="M calc(100% - 20px) 100 L calc(100% - 20px) 20 L calc(100% - 100px) 20" fill="none" stroke="cyan" strokeWidth="1" />
        {/* Canto Inferior Esquerdo */}
        <path d="M 20 calc(100% - 100px) L 20 calc(100% - 20px) L 100 calc(100% - 20px)" fill="none" stroke="cyan" strokeWidth="1" />
        {/* Canto Inferior Direito */}
        <path d="M calc(100% - 20px) calc(100% - 100px) L calc(100% - 20px) calc(100% - 20px) L calc(100% - 100px) calc(100% - 20px)" fill="none" stroke="cyan" strokeWidth="1" />
      </svg>

    </div>
  );
}