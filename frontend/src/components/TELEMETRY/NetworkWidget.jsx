export default function NetworkWidget({ data }) {
  if (!data) return null;

  return (
    <>
      <div className="flex justify-between text-[11px] font-medium text-white/70 select-text">
        <span>Download</span>
        <span className="font-semibold text-cyan-300 font-mono text-[10px]">
          {data.net.download_speed}
        </span>
      </div>

      <div className="flex justify-between text-[11px] font-medium text-white/70 select-text">
        <span>Upload</span>
        <span className="font-semibold text-cyan-300 font-mono text-[10px]">
          {data.net.upload_speed}
        </span>
      </div>

      <div className="flex justify-between text-[11px] font-medium text-white/60 border-t border-white/5 pt-2 mt-1">
        <span>Battery Charge</span>
        <span
          className={`font-semibold text-[11px] ${
            data.battery.percent < 20
              ? "text-red-400 animate-pulse"
              : "text-emerald-400"
          }`}
        >
          {data.battery.percent}%
        </span>
      </div>
    </>
  );
}
