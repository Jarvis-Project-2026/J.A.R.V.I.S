import ParticleSphere from "./ParticleSphere";

// 1. Adicione 'isCritical' aqui nos argumentos
export default function ArcReactor({ state, isCritical }) {
  return (
    <div className="relative flex items-center justify-center">
      {/* --- NÚCLEO 3D --- */}
      {/* Container da Esfera */}
      <div className="relative z-10 w-[720px] h-[720px] flex items-center justify-center">
          {/* Pequena borda interna para conter visualmente a esfera */}
          {/* Opcional: Se quiser que essa borda fina também fique vermelha, pode usar classe condicional aqui */}
          <div className={`absolute inset-0 rounded-full border shadow-[inset_0_0_20px_rgba(6,182,212,0.2)] pointer-events-none transition-colors duration-500 ${
            isCritical ? "border-red-500/30" : "border-cyan-500/10"
          }`}></div>
          
          {/* 2. REPASSE 'isCritical' para a Esfera aqui! */}
          <ParticleSphere state={state} isCritical={isCritical} />
      </div>
    </div>
  );
}