/* eslint-disable */
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import TelemetryWidget from "./TELEMETRY/TelemetryWidget";
import CpuRamWidget from "./TELEMETRY/CpuRamWidget";
import NetworkWidget from "./TELEMETRY/NetworkWidget";
import useBridgeAPI from "../hooks/BridgeAPI";

export default function LiveTelemetry() {
  const [data, setData] = useState(null);
  const [showCpuWidget, setShowCpuWidget] = useState(true);
  const [showNetWidget, setShowNetWidget] = useState(true);
  const { callApi } = useBridgeAPI();

  // Sincroniza dados com o Python a cada 1 segundo
  useEffect(() => {
    const updateStats = async () => {
      try {
        const stats = await callApi("get_telemetry");
        if (stats) {
          setData(stats);
        }
      } catch (err) {
        console.error("Erro ao buscar telemetria:", err);
      }
    };

    const interval = setInterval(updateStats, 1000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return null;

  return (
    <div className="absolute inset-0 pointer-events-none z-40 overflow-hidden">
      {/* Quick widget restoration triggers in the footer */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-3 pointer-events-auto select-none opacity-45 hover:opacity-100 transition-opacity duration-300">
        {!showCpuWidget && (
          <motion.button
            onClick={() => setShowCpuWidget(true)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-3 py-1 rounded-full bg-black/40 border border-white/5 backdrop-blur-[10px] text-[8px] font-bold tracking-widest uppercase text-cyan-400 cursor-pointer"
          >
            + Core Diagnostic
          </motion.button>
        )}
        {!showNetWidget && (
          <motion.button
            onClick={() => setShowNetWidget(true)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-3 py-1 rounded-full bg-black/40 border border-white/5 backdrop-blur-[10px] text-[8px] font-bold tracking-widest uppercase text-cyan-400 cursor-pointer"
          >
            + Network Uplink
          </motion.button>
        )}
      </div>

      {/* 1. CORE DIAGNOSTIC WIDGET */}
      <AnimatePresence>
        {showCpuWidget && (
          <TelemetryWidget
            title="Core Diagnostics"
            onClose={() => setShowCpuWidget(false)}
            positionClasses="bottom-10 left-10"
          >
            <CpuRamWidget data={data} />
          </TelemetryWidget>
        )}
      </AnimatePresence>

      {/* 2. NETWORK UPLINK WIDGET */}
      <AnimatePresence>
        {showNetWidget && (
          <TelemetryWidget
            title="Network Uplink"
            onClose={() => setShowNetWidget(false)}
            positionClasses="bottom-10 right-10"
          >
            <NetworkWidget data={data} />
          </TelemetryWidget>
        )}
      </AnimatePresence>
    </div>
  );
}
