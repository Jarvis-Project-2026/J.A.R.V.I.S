// src/components/CustomCursor.jsx
import { useEffect, useState } from "react";

export default function CustomCursor() {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    const updatePosition = (e) => {
      // Atualiza a posição X e Y baseada no mouse real
      setPosition({ x: e.clientX, y: e.clientY });
    };

    const handleMouseOver = (e) => {
      // Se passar por cima de um botão ou texto interativo, muda o estado
      if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A') {
        setIsHovering(true);
      } else {
        setIsHovering(false);
      }
    };

    window.addEventListener("mousemove", updatePosition);
    window.addEventListener("mouseover", handleMouseOver);

    return () => {
      window.removeEventListener("mousemove", updatePosition);
      window.removeEventListener("mouseover", handleMouseOver);
    };
  }, []);

  return (
    <>
      {/* Esconde o cursor padrão globalmente (será aplicado via style inline no body se preferir, ou aqui) */}
      <style>{`body { cursor: none; }`}</style>
      
      {/* O Cursor Personalizado */}
      <div
        className="fixed top-0 left-0 pointer-events-none z-[9999] mix-blend-difference transition-transform duration-100 ease-out flex items-center justify-center"
        style={{
          transform: `translate3d(${position.x}px, ${position.y}px, 0) translate(-50%, -50%)`,
        }}
      >
        {/* Círculo Externo (A Mira) */}
        <div 
            className={`border border-cyan-400 rounded-full transition-all duration-300 ease-out
            ${isHovering ? 'w-12 h-12 opacity-100 border-2' : 'w-8 h-8 opacity-50'}
            `}
        ></div>

        {/* Ponto Central (O Alvo) */}
        <div className="absolute w-1 h-1 bg-cyan-200 rounded-full"></div>

        {/* Linhas de Mira (Crosshair) - Só aparecem quando não está em hover */}
        {!isHovering && (
            <>
                <div className="absolute w-12 h-[1px] bg-cyan-500/30"></div>
                <div className="absolute h-12 w-[1px] bg-cyan-500/30"></div>
            </>
        )}
      </div>
    </>
  );
}