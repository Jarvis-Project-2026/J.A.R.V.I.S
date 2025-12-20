import ParticleSphere from "./ParticleSphere";

export default function ArcReactor({ state }) {
  return (
    <div className="relative flex items-center justify-center">
      {/* --- NÚCLEO 3D --- */}
      {/* Container da Esfera */}
      <div className="relative z-10 w-[720px] h-[720px] flex items-center justify-center">
          {/* Pequena borda interna para conter visualmente a esfera */}
          <div className="absolute inset-0 rounded-full border border-cyan-500/10 shadow-[inset_0_0_20px_rgba(6,182,212,0.2)] pointer-events-none"></div>
          <ParticleSphere state={state} />
      </div>
    </div>
  );
}