import { useState, useEffect } from "react";
import ArcReactor from "./components/ArcReactor";
import StartupScreen from "./components/StartupScreen";
import LiveTelemetry from "./components/LiveTelemetry";

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [jarvisState, setJarvisState] = useState("idle");
  const [isCritical, setIsCritical] = useState(false); 

  useEffect(() => {
    // OUVINTE DE ESTADO (Voz/Processamento)
    window.receiveStatus = (status, text) => {
      console.log(`[PYTHON SAYS]: ${status} - ${text}`);
      
      let rawState = status.toLowerCase();
      let visualState = rawState;

      if (rawState === "listening") visualState = "idle";
      if (rawState === "processing") visualState = "listening";
      if (rawState === "error") visualState = "idle";

      setJarvisState(visualState);
    };

    // OUVINTE DE HUD (Sensores/Alerta Vermelho)
    window.updateHudState = (isActive) => {
      console.log("🚨 ALERTA VISUAL:", isActive ? "ATIVADO" : "NORMALIZADO");
      // Agora setIsCritical é uma função válida!
      setIsCritical(isActive); 
    };

    if (window.pywebview) {
        console.log("Bridge detectada. Sistemas prontos.");
    }

    return () => {
      delete window.receiveStatus;
      delete window.updateHudState;
    };
  }, []); // Removemos as dependências desnecessárias para evitar loops

  const handleBootComplete = () => {
    setIsLoading(false);
  };

  return (
    <main className="w-screen h-screen bg-transparent backdrop-blur-md overflow-hidden flex flex-col items-center justify-center relative text-cyan-500 font-mono cursor-default">

      {/* --- CORREÇÃO 2: A Camada Visual do HUD --- */}
      {/* Certifique-se que a classe .hud-critical-mode está no seu index.css */}
      <div className={isCritical ? "hud-critical-mode" : ""} />

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
                  // Lógica visual combinada: Crítico (Vermelho) ou Estado do Jarvis
                  isCritical ? "bg-red-600 shadow-[0_0_10px_red]" :
                  jarvisState === "idle" ? "bg-cyan-500" : 
                  jarvisState === "speaking" ? "bg-cyan-300" : "bg-white"
                } animate-pulse`}
              ></div>
              <span className={`text-xs opacity-70 uppercase tracking-widest ${isCritical ? "text-red-500 font-bold" : ""}`}>
                 {isCritical ? "CRITICAL ALERT" : (jarvisState === "listening" ? "PROCESSING" : jarvisState === "idle" ? "STANDBY" : jarvisState)} MODE
              </span>
            </div>
          </div>

          {/* Passamos isCritical para o Reator caso queira mudar a cor dele também */}
          <ArcReactor state={jarvisState} isCritical={isCritical} />
          <LiveTelemetry />
        </>
      )}
    </main>
  );
}