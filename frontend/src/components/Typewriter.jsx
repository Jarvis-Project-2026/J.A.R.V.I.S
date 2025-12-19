import { useState, useEffect } from "react";

export default function Typewriter({ text, speed = 30 }) {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    setDisplayedText(""); 
    let currentIndex = 0;
    const intervalId = setInterval(() => {
      if (currentIndex < text.length) {
        setDisplayedText(text.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        clearInterval(intervalId); // Para de processar ao fim
      }
    }, speed);

    // Limpeza de memória (Mata o processo se o componente sumir)
    return () => clearInterval(intervalId);
  }, [text, speed]);

  return (
    <span className="border-r-2 border-cyan-500 animate-pulse pr-1">
      {displayedText}
    </span>
  );
}