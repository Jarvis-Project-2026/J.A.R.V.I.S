import { useState } from "react";
import ArcReactor from "./components/ArcReactor";
import StartupScreen from "./components/StartupScreen";
import Typewriter from "./components/Typewriter";
import CustomCursor from "./components/CustomCursor";
import LiveTelemetry from "./components/LiveTelemetry";
import HoloFrame from "./components/HoloFrame";

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [jarvisState, setJarvisState] = useState("idle");
  const [message, setMessage] = useState("Sistemas Online.");

  const handleBootComplete = () => {
    setIsLoading(false);
  };

  // --- FUNÇÕES DE COMUNICAÇÃO COM PYTHON ---

  // Botão LISTEN: Aciona o microfone no Python
  const handleListen = async () => {
    setJarvisState("listening");
    setMessage("Inicializando sensores de áudio...");

    // Verifica se estamos rodando dentro do software Python
    if (window.pywebview) {
      try {
        // Chama a função 'start_listening' do arquivo main.py
        const response = await window.pywebview.api.start_listening();
        
        // Quando o Python responder...
        setJarvisState("speaking"); // Muda visual para 'Falando'
        setMessage(response);       // Mostra o texto que veio do Python

        // Volta para IDLE após 4 segundos
        setTimeout(() => setJarvisState("idle"), 4000);
      } catch (error) {
        console.error("Erro na ponte Python:", error);
        setMessage("Erro: Módulo de voz desconectado.");
        setJarvisState("idle");
      }
    } else {
      // Fallback para quando você estiver testando só no navegador
      console.warn("Python não detectado (Modo Web)");
      setTimeout(() => {
        setMessage("Simulação: Áudio detectado.");
        setJarvisState("idle");
      }, 2000);
    }
  };

  // Botão SPEAK: Envia um comando de teste
  const handleSpeak = async () => {
    setJarvisState("speaking");
    setMessage("Enviando pacote de dados...");

    if (window.pywebview) {
      try {
        // Chama a função 'process_command' do main.py
        const response = await window.pywebview.api.process_command("Protocolo de Teste Alpha");
        setMessage(response);
        setTimeout(() => setJarvisState("idle"), 4000);
      } catch (error) {
        setMessage("Falha no processamento neural.");
      }
    } else {
      setTimeout(() => {
        setMessage("Simulação: Comando processado.");
        setJarvisState("idle");
      }, 2000);
    }
  };

  // Botão IDLE: Reseta ou pode servir para fechar o app
  const handleIdle = () => {
    setJarvisState("idle");
    setMessage("Sistemas em espera.");
    
    // Opcional: Se quiser que esse botão feche o app de verdade
    // if (window.pywebview) window.pywebview.api.shutdown(); 
  };

  return (
    <main className="w-screen h-screen bg-black overflow-hidden flex flex-col items-center justify-center relative text-cyan-500 font-mono selection:bg-cyan-500/30 cursor-none">
      <CustomCursor />

      {isLoading ? (
        <StartupScreen onComplete={handleBootComplete} />
      ) : (
        <>
          <div className="absolute top-10 left-10 z-50 animate-[fadeIn_1s_ease-in]">
            <HoloFrame />
            <h1 className="text-xl font-bold tracking-[0.2em] drop-shadow-[0_0_5px_rgba(6,182,212,0.8)]">
              J.A.R.V.I.S.{" "}
              <span className="text-xs opacity-50 ml-2">SYSTEM V1.0</span>
            </h1>
            <div className="flex items-center gap-2 mt-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  jarvisState === "idle" ? "bg-cyan-500" : "bg-red-500"
                } animate-pulse`}
              ></div>
              <span className="text-xs opacity-70 uppercase tracking-widest">
                {jarvisState} MODE
              </span>
            </div>
          </div>

          <ArcReactor state={jarvisState} />
          <LiveTelemetry />

          <div className="absolute bottom-32 text-center w-full max-w-2xl px-4 z-50 h-24 flex items-center justify-center">
            <p className="text-lg md:text-2xl text-cyan-100 font-light tracking-wide drop-shadow-[0_0_10px_rgba(6,182,212,0.5)] bg-black/40 p-4 border-l-2 border-cyan-500 backdrop-blur-sm">
              <span className="text-xs uppercase text-cyan-600 block mb-2 tracking-[0.3em] text-left">
                System.Log.Output
              </span>
              <Typewriter text={message} speed={30} />
            </p>
          </div>

          {/* Botões Atualizados com as novas funções */}
          <div className="absolute bottom-10 flex gap-4 z-50 opacity-50 hover:opacity-100 transition-opacity">
            <button
              onClick={handleIdle}
              className="px-4 py-2 border border-cyan-800 hover:bg-cyan-900/50 rounded text-xs uppercase tracking-widest hover:bg-cyan-500 hover:text-black cursor-none"
            >
              Idle
            </button>
            <button
              onClick={handleListen}
              className="px-4 py-2 border border-cyan-800 hover:bg-cyan-900/50 rounded text-xs uppercase tracking-widest hover:bg-cyan-500 hover:text-black cursor-none"
            >
              Listen
            </button>
            <button
              onClick={handleSpeak}
              className="px-4 py-2 border border-cyan-800 hover:bg-cyan-900/50 rounded text-xs uppercase tracking-widest hover:bg-cyan-500 hover:text-black cursor-none"
            >
              Speak
            </button>
          </div>
        </>
      )}
    </main>
  );
}