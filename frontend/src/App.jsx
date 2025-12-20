import { useState, useEffect } from "react";
import ArcReactor from "./components/ArcReactor";
import StartupScreen from "./components/StartupScreen";
import LiveTelemetry from "./components/LiveTelemetry";

export default function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [jarvisState, setJarvisState] = useState("idle");
  const [, setMessage] = useState("");

  useEffect(() => {
    // EXPÕE A FUNÇÃO PARA O PYTHON ENCONTRAR
    window.receiveStatus = (status, msg) => {
      console.log("Status recebido do Python:", status, msg);
      setJarvisState(status.toLowerCase());
      setMessage(msg);
    };

    if (window.pywebview) {
        console.log("Bridge detectada. Sistemas prontos.");
    }

    // Limpeza ao desmontar o componente
    return () => {
      delete window.receiveStatus;
    };
  }, []);

  // --- A PONTE: O React escutando o Python ---
  useEffect(() => {
    window.receiveStatus = (status, text) => {
      console.log(`[PYTHON SAYS]: ${status} - ${text}`);
      
      let rawState = status.toLowerCase();
      let visualState = rawState;

      // --- MAPEAMENTO DA NOVA LÓGICA ---

      // LISTENING (Escutando) -> 'idle' (Azul Girando)
      // Você quer que ele continue azul enquanto escuta.
      if (rawState === "listening") {
        visualState = "idle";
      }

      // PROCESSING (Pensando) -> 'listening' (Branco/Parado)
      // Você quer que ele fique branco (o visual 'listening' do componente) quando estiver pensando.
      if (rawState === "processing") {
        visualState = "listening"; 
      }

      // SPEAKING (Falando) -> 'speaking' (Deformando/Vivo)
      // Mantém o padrão.
      // Tratamento de Erro
      if (rawState === "error") visualState = "idle";

      setJarvisState(visualState);
    };

    return () => {
      delete window.receiveStatus;
    };
  }, []);

  const handleBootComplete = () => {
    setIsLoading(false);
  };

  return (
    <main className="w-screen h-screen bg-transparent backdrop-blur-md overflow-hidden flex flex-col items-center justify-center relative text-cyan-500 font-mono cursor-default">
      {isLoading ? (
        <StartupScreen onComplete={handleBootComplete} />
      ) : (
        <>
          {/* Cabeçalho Holográfico */}
          <div className="absolute top-10 left-10 z-50 animate-[fadeIn_1s_ease-in]">
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

          {/* Telemetria ao Vivo do Computador */}
          <LiveTelemetry />
        </>
      )}
    </main>
  );
}