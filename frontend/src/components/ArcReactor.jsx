import ParticleSphere from "./ParticleSphere";
import TechRings from "./TechRings";

export default function ArcReactor({ state }) {
  return (
    <div className="relative flex items-center justify-center">

      {/* --- FUNDO E ANÉIS TÉCNICOS --- */}
      {/* Brilho de Fundo (Aura) */}
      <div className={`absolute w-[600px] h-[600px] bg-cyan-900/10 rounded-full shadow-[0_0_150px_rgba(6,182,212,0.4)] blur-3xl transition-all duration-500 ${state === 'speaking' ? 'opacity-100 scale-110' : 'opacity-60 scale-100'}`}></div>

      {/* Os Novos Anéis (Substituem as bordas simples antigas) */}
      <TechRings state={state} />

      {/* --- NÚCLEO 3D --- */}
      {/* Container da Esfera */}
      <div className="relative z-10 w-[520px] h-[520px] flex items-center justify-center">
          {/* Pequena borda interna para conter visualmente a esfera */}
          <div className="absolute inset-0 rounded-full border border-cyan-500/10 shadow-[inset_0_0_20px_rgba(6,182,212,0.2)] pointer-events-none"></div>
          
          <ParticleSphere state={state} />
      </div>

    </div>
  );
}