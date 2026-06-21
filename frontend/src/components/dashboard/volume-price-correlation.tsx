import { useEffect, useState } from "react";
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { BarChart3 } from "lucide-react";
import { fetchApi } from "@/lib/api";
import { useTheme } from "@/contexts/ThemeContext";

interface CorrelationPoint {
  date: string;
  volume: number;
  price: number;
}

export function VolumePriceCorrelation() {
  const { theme } = useTheme();
  const light = theme === "light";
  const [data, setData] = useState<CorrelationPoint[]>([]);
  const [hours, setHours] = useState(24);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const result = await fetchApi<{ data: CorrelationPoint[] }>(
          `/api/news/volume-price?hours=${hours}`
        );
        if (!cancelled) setData(result.data || []);
      } catch {
        if (!cancelled) setData([]);
      }
      if (!cancelled) setLoading(false);
    };
    load();
    return () => { cancelled = true; };
  }, [hours]);

  const textColor = light ? "#475569" : "#64748b";
  const gridColor = light ? "rgba(0,0,0,0.06)" : "rgba(255,255,255,0.05)";
  const tooltipBg = light ? "rgba(255,255,255,0.95)" : "rgba(10,10,20,0.95)";
  const tooltipBorder = light ? "rgba(0,0,0,0.1)" : "rgba(0,240,255,0.2)";
  const tooltipColor = light ? "#0f172a" : "#fff";
  const legendColor = light ? "#475569" : "#94a3b8";
  const textPrimary = light ? "text-slate-800" : "text-white";
  const textMuted = light ? "text-slate-500" : "text-slate-400";

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BarChart3 className={`h-5 w-5 ${light ? "text-cyan-600" : "text-cyan-400"}`} />
          <h3 className={`text-lg font-bold ${textPrimary}`}>Volume–Price Correlation</h3>
        </div>
        <div className="flex gap-2">
          {[6, 12, 24, 48].map((h) => (
            <button
              key={h}
              onClick={() => setHours(h)}
              className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all ${
                hours === h
                  ? light
                    ? "bg-cyan-100 text-cyan-700 border border-cyan-300"
                    : "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                  : `${textMuted} border border-transparent`
              }`}
            >
              {h}h
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-5 h-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data.length === 0 ? (
        <div className={`text-center py-20 ${textMuted} text-sm`}>No volume-price data available</div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="date" tick={{ fontSize: 9, fill: textColor }} />
            <YAxis yAxisId="left" tick={{ fontSize: 10, fill: textColor }} />
            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: textColor }} />
            <Tooltip contentStyle={{ background: tooltipBg, border: `1px solid ${tooltipBorder}`, borderRadius: "8px", fontSize: "12px", color: tooltipColor }} />
            <Legend wrapperStyle={{ fontSize: "11px", color: legendColor }} />
            <Bar yAxisId="left" dataKey="volume" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Volume" opacity={0.7} />
            <Line yAxisId="right" dataKey="price" stroke="#f59e0b" strokeWidth={2} dot={false} name="Price ($)" />
          </ComposedChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
