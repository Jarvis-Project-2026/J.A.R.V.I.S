import { useState, useEffect } from "react";
import ArcReactor from "./components/ArcReactor";
import StartupScreen from "./components/StartupScreen";
import Typewriter from "./components/Typewriter";
import LiveTelemetry from "./components/LiveTelemetry";
import HoloFrame from "./components/HoloFrame";

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [jarvisState, setJarvisState] = useState("idle");
  const [message, setMessage] = useState("Sistemas Online.");

  // --- A PONTE: O React escutando o Python ---
  useEffect(() => {
    window.receiveStatus = (status, text) => {
      console.log(`[PYTHON SAYS]: ${status} - ${text}`);
      
      let rawState = status.toLowerCase();
      let visualState = rawState;

      // --- MAPEAMENTO DA NOVA LÓGICA ---

      // 1. LISTENING (Escutando) -> 'idle' (Azul Girando)
      // Você quer que ele continue azul enquanto escuta.
      if (rawState === "listening") {
        visualState = "idle";
      }

      // 2. PROCESSING (Pensando) -> 'listening' (Branco/Parado)
      // Você quer que ele fique branco (o visual 'listening' do componente) quando estiver pensando.
      if (rawState === "processing") {
        visualState = "listening"; 
      }

      // 3. SPEAKING (Falando) -> 'speaking' (Deformando/Vivo)
      // Mantém o padrão.

      // Tratamento de Erro
      if (rawState === "error") visualState = "idle";

      setJarvisState(visualState);
      setMessage(text);
    };

    return () => {
      delete window.receiveStatus;
    };
  }, []);

  const handleBootComplete = () => {
    setIsLoading(false);
  };

  const handleIdle = () => {
    setJarvisState("idle");
    setMessage("Encerrando protocolos...");
    if (window.pywebview) window.pywebview.api.shutdown(); 
  };

  return (
    <main className="w-screen h-screen bg-transparent backdrop-blur-md overflow-hidden flex flex-col items-center justify-center relative text-cyan-500 font-mono selection:bg-cyan-500/30 cursor-default">
      {isLoading ? (
        <StartupScreen onComplete={handleBootComplete} />
      ) : (
        <>
          {/* Cabeçalho Holográfico */}
          <div className="absolute top-10 left-10 z-50 animate-[fadeIn_1s_ease-in]">
            <HoloFrame />
            <h1 className="text-xl font-bold tracking-[0.2em] drop-shadow-[0_0_5px_rgba(6,182,212,0.8)]">
              J.A.R.V.I.S.{" "}
              <span className="text-xs opacity-50 ml-2">SYSTEM V1.0</span>
            </h1>
            <div className="flex items-center gap-2 mt-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  jarvisState === "idle" ? "bg-cyan-500" : 
                  jarvisState === "speaking" ? "bg-red-500" : "bg-white"
                } animate-pulse`}
              ></div>
              <span className="text-xs opacity-70 uppercase tracking-widest">
                {/* Mostra o estado lógico real para você saber o que está acontecendo */}
                {jarvisState === "listening" ? "PROCESSING" : jarvisState === "idle" ? "STANDBY" : jarvisState} MODE
              </span>
            </div>
          </div>

          {/* Núcleo do Reator */}
          <ArcReactor state={jarvisState} />
          
          <LiveTelemetry />

          {/* Log do Sistema */}
          <div className="absolute bottom-32 text-center w-full max-w-2xl px-4 z-50 h-24 flex items-center justify-center">
            <p className="text-lg md:text-2xl text-cyan-100 font-light tracking-wide drop-shadow-[0_0_10px_rgba(6,182,212,0.5)] bg-black/40 p-4 border-l-2 border-cyan-500 backdrop-blur-sm">
              <span className="text-xs uppercase text-cyan-600 block mb-2 tracking-[0.3em] text-left">
                System.Log.Output
              </span>
              <Typewriter text={message} speed={30} />
            </p>
          </div>

          {/* Botão Encerrar */}
          <div className="absolute bottom-10 flex gap-4 z-50 opacity-50 hover:opacity-100 transition-opacity">
            <button
              onClick={handleIdle}
              className="px-4 py-2 border border-cyan-800 hover:bg-cyan-900/50 rounded text-xs uppercase tracking-widest hover:bg-cyan-500 hover:text-black cursor-none"
            >
              ENCERRAR PROTOCOLO
            </button>
          </div>
        </>
      )}
    </main>
  );
}