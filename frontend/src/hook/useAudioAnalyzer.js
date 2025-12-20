import { useState, useEffect } from 'react';

export function useAudioAnalyzer(isSpeaking) {
  const [intensity, setIntensity] = useState(0);

  useEffect(() => {
    // Se não estiver falando, zera imediatamente
    if (!isSpeaking) {
      setIntensity(0);
      return;
    }

    let audioCtx, analyzer, dataArray, animationId;

    const startAnalysis = async () => {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AudioContext();
        analyzer = audioCtx.createAnalyser();
        analyzer.fftSize = 64; // Tamanho ideal para performance visual

        // Tenta conectar ao destino de áudio para pegar o som do sistema
        analyzer.connect(audioCtx.destination);

        const bufferLength = analyzer.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        const update = () => {
          if (!isSpeaking) return;
          
          analyzer.getByteFrequencyData(dataArray);
          
          // Calcula a média do volume
          const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
          
          // Lógica Real: Se tiver som, normaliza. Se for silêncio, retorna 0.
          // Removemos o Math.sin() que criava o movimento falso.
          const value = average > 0 ? average / 50 : 0;

          setIntensity(value);
          animationId = requestAnimationFrame(update);
        };
        
        update();
      } catch (err) {
        // Se der erro no áudio, mantemos estático (0) em vez de simular erro
        setIntensity(0); 
      }
    };

    startAnalysis();

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
      if (audioCtx && audioCtx.state !== 'closed') audioCtx.close();
    };
  }, [isSpeaking]);

  return intensity;
}