import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { TrendingUp } from "lucide-react";
import { fetchApi } from "@/lib/api";
import { useTheme } from "@/contexts/ThemeContext";

interface TrendPoint {
  timestamp: string;
  bullish_count: number;
  bearish_count: number;
  neutral_count: number;
  avg_confidence: number;
}

export function SentimentTrend() {
  const { theme } = useTheme();
  const light = theme === "light";
  const [data, setData] = useState<TrendPoint[]>([]);
  const [hours, setHours] = useState(24);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const result = await fetchApi<{ trend: TrendPoint[] }>(
          `/api/sentiment/trend?hours=${hours}&interval=60`
        );
        setData(result.trend || []);
      } catch {
        setData([]);
      }
      setLoading(false);
    };
    load();
  }, [hours]);

  const formatted = data.map((d) => ({
    ...d,
    time: new Date(d.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
  }));

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
          <TrendingUp className={`h-5 w-5 ${light ? "text-cyan-600" : "text-cyan-400"}`} />
          <h3 className={`text-lg font-bold ${textPrimary}`}>Sentiment Trend</h3>
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
      ) : formatted.length === 0 ? (
        <div className={`flex items-center justify-center py-20 ${textMuted} text-sm`}>
          No sentiment trend data available
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={formatted}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="time" tick={{ fontSize: 10, fill: textColor }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 10, fill: textColor }} tickLine={false} axisLine={false} allowDecimals={false} />
            <Tooltip contentStyle={{ background: tooltipBg, border: `1px solid ${tooltipBorder}`, borderRadius: "8px", fontSize: "12px", color: tooltipColor }} />
            <Legend wrapperStyle={{ fontSize: "11px", color: legendColor }} />
            <Line type="monotone" dataKey="bullish_count" stroke="#22c55e" strokeWidth={2} dot={false} name="Bullish" />
            <Line type="monotone" dataKey="bearish_count" stroke="#ef4444" strokeWidth={2} dot={false} name="Bearish" />
            <Line type="monotone" dataKey="neutral_count" stroke="#94a3b8" strokeWidth={2} dot={false} name="Neutral" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
