import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { BarChart3 } from "lucide-react";
import { fetchApi } from "@/lib/api";
import { useTheme } from "@/contexts/ThemeContext";

interface ConfidenceBucket {
  range: string;
  count: number;
}

export function ConfidenceDistribution() {
  const { theme } = useTheme();
  const light = theme === "light";
  const [data, setData] = useState<ConfidenceBucket[]>([]);
  const [hours, setHours] = useState(24);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const result = await fetchApi<{ distribution: ConfidenceBucket[] }>(
          `/api/sentiment/confidence-distribution?hours=${hours}`
        );
        if (!cancelled) setData(result.distribution || []);
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
  const textPrimary = light ? "text-slate-800" : "text-white";
  const textMuted = light ? "text-slate-500" : "text-slate-400";

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BarChart3 className={`h-5 w-5 ${light ? "text-cyan-600" : "text-cyan-400"}`} />
          <h3 className={`text-lg font-bold ${textPrimary}`}>Confidence Distribution</h3>
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
        <div className={`text-center py-20 ${textMuted} text-sm`}>No confidence data available</div>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="range" tick={{ fontSize: 9, fill: textColor }} />
            <YAxis tick={{ fontSize: 10, fill: textColor }} allowDecimals={false} />
            <Tooltip
              contentStyle={{
                background: tooltipBg,
                border: `1px solid ${tooltipBorder}`,
                borderRadius: "8px",
                fontSize: "12px",
                color: tooltipColor,
              }}
              formatter={(value) => [`${value}`, "Analyses"]}
            />
            <Bar dataKey="count" fill="#a855f7" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
