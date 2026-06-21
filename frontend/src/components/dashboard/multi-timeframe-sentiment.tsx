import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Clock } from "lucide-react";
import { fetchApi } from "@/lib/api";
import { useTheme } from "@/contexts/ThemeContext";

interface TimeframeData {
  timeframe: string;
  bullish: number;
  bearish: number;
  neutral: number;
}

export function MultiTimeframeSentiment() {
  const { theme } = useTheme();
  const light = theme === "light";
  const [data, setData] = useState<TimeframeData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const timeframes = [1, 4, 12, 24, 48];
        const results: TimeframeData[] = [];

        for (const h of timeframes) {
          const dist = await fetchApi<{ distribution: Record<string, number> }>(
            `/api/sentiment/distribution?hours=${h}`
          );
          const d = dist.distribution || {};
          results.push({
            timeframe: `${h}h`,
            bullish: d.bullish || 0,
            bearish: d.bearish || 0,
            neutral: d.neutral || 0,
          });
        }

        if (!cancelled) setData(results);
      } catch {
        if (!cancelled) setData([]);
      }
      if (!cancelled) setLoading(false);
    };
    load();
    return () => { cancelled = true; };
  }, []);

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
      <div className="flex items-center gap-2 mb-4">
        <Clock className={`h-5 w-5 ${light ? "text-cyan-600" : "text-cyan-400"}`} />
        <h3 className={`text-lg font-bold ${textPrimary}`}>Multi-Timeframe Sentiment</h3>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-5 h-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data.length === 0 ? (
        <div className={`text-center py-20 ${textMuted} text-sm`}>No sentiment data available</div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="timeframe" tick={{ fontSize: 10, fill: textColor }} />
            <YAxis tick={{ fontSize: 10, fill: textColor }} allowDecimals={false} />
            <Tooltip
              contentStyle={{
                background: tooltipBg,
                border: `1px solid ${tooltipBorder}`,
                borderRadius: "8px",
                fontSize: "12px",
                color: tooltipColor,
              }}
            />
            <Legend wrapperStyle={{ fontSize: "11px", color: legendColor }} />
            <Bar dataKey="bullish" fill="#22c55e" radius={[4, 4, 0, 0]} name="Bullish" />
            <Bar dataKey="bearish" fill="#ef4444" radius={[4, 4, 0, 0]} name="Bearish" />
            <Bar dataKey="neutral" fill="#94a3b8" radius={[4, 4, 0, 0]} name="Neutral" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
