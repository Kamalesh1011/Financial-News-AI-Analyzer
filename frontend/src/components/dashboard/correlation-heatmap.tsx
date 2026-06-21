import { useEffect, useState } from "react";
import { Grid3x3 } from "lucide-react";
import { fetchApi } from "@/lib/api";

interface CorrelationData {
  symbols: string[];
  matrix: number[][];
}

function getColor(value: number): string {
  if (value > 0.7) return "rgba(34, 197, 94, 0.8)";
  if (value > 0.3) return "rgba(34, 197, 94, 0.4)";
  if (value > 0) return "rgba(34, 197, 94, 0.15)";
  if (value === 0) return "rgba(148, 163, 184, 0.1)";
  if (value > -0.3) return "rgba(239, 68, 68, 0.15)";
  if (value > -0.7) return "rgba(239, 68, 68, 0.4)";
  return "rgba(239, 68, 68, 0.8)";
}

export function CorrelationHeatmap() {
  const [data, setData] = useState<CorrelationData | null>(null);
  const [symbols, setSymbols] = useState("AAPL,MSFT,GOOGL,NVDA,TSLA");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const loadData = async () => {
      setLoading(true);
      try {
        const result = await fetchApi<CorrelationData>(
          `/api/correlation?symbols=${symbols}&hours=72`
        );
        if (!cancelled) setData(result);
      } catch {
        if (!cancelled) setData(null);
      }
      if (!cancelled) setLoading(false);
    };
    loadData();
    return () => { cancelled = true; };
  }, [symbols]);

  const handleUpdate = async () => {
    setLoading(true);
    try {
      const result = await fetchApi<CorrelationData>(
        `/api/correlation?symbols=${symbols}&hours=72`
      );
      setData(result);
    } catch {
      setData(null);
    }
    setLoading(false);
  };

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Grid3x3 className="h-5 w-5 text-cyan-400" />
          <h3 className="text-lg font-bold text-white">Asset Correlation Heatmap</h3>
        </div>
        <div className="flex gap-2">
          <input
            value={symbols}
            onChange={(e) => setSymbols(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-xs font-mono focus:outline-none focus:border-cyan-500/50 w-64"
            placeholder="Symbols (comma separated)"
          />
          <button
            onClick={handleUpdate}
            className="px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 text-xs font-mono border border-cyan-500/30 hover:bg-cyan-500/30 transition-all"
          >
            Update
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-5 h-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : !data || data.matrix.length === 0 ? (
        <div className="text-center py-20 text-slate-400 text-sm">No correlation data available</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="p-2" />
                {data.symbols.map((s) => (
                  <th key={s} className="p-2 text-xs font-mono text-cyan-400 font-bold">
                    {s}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.matrix.map((row, i) => (
                <tr key={data.symbols[i]}>
                  <td className="p-2 text-xs font-mono text-cyan-400 font-bold text-right pr-4">
                    {data.symbols[i]}
                  </td>
                  {row.map((val, j) => (
                    <td key={j} className="p-1">
                      <div
                        className="w-12 h-12 rounded-lg flex items-center justify-center text-[10px] font-mono font-bold transition-all hover:scale-110 cursor-default"
                        style={{
                          background: getColor(val),
                          color: val === 0 ? "#64748b" : "#fff",
                        }}
                        title={`${data.symbols[i]} × ${data.symbols[j]}: ${val.toFixed(4)}`}
                      >
                        {val.toFixed(2)}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex items-center justify-center gap-4 mt-4 text-[10px] text-slate-500 font-mono">
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded" style={{ background: "rgba(239,68,68,0.6)" }} /> Negative
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded" style={{ background: "rgba(148,163,184,0.2)" }} /> Neutral
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded" style={{ background: "rgba(34,197,94,0.6)" }} /> Positive
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
