import { useState, useEffect, useRef } from "react";

export default function Typewriter({ text, speed = 30 }) {
  const [displayedText, setDisplayedText] = useState("");
  const indexRef = useRef(0);

  // Reinicia a digitação sempre que o texto muda
  useEffect(() => {
    setDisplayedText("");
    indexRef.current = 0;
  }, [text]);

  useEffect(() => {
    // Se já digitou tudo, para
    if (indexRef.current >= text.length) return;

    const timeoutId = setTimeout(() => {
      // Adiciona a próxima letra
      setDisplayedText((prev) => prev + text.charAt(indexRef.current));
      indexRef.current += 1;
    }, speed);

    return () => clearTimeout(timeoutId);
  }, [displayedText, text, speed]);

  return (
    <span className="border-r-2 border-cyan-500 animate-pulse pr-1">
      {displayedText}
    </span>
  );
}