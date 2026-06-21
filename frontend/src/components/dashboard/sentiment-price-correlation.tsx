import { useEffect, useState } from "react";
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Activity } from "lucide-react";
import { fetchApi } from "@/lib/api";
import { useTheme } from "@/contexts/ThemeContext";

interface TrendPoint {
  timestamp: string;
  bullish_count: number;
  bearish_count: number;
  neutral_count: number;
  avg_confidence: number;
}

interface PricePoint {
  timestamp: string;
  price: number;
}

export function SentimentPriceCorrelation() {
  const { theme } = useTheme();
  const light = theme === "light";
  const [sentimentData, setSentimentData] = useState<TrendPoint[]>([]);
  const [priceData, setPriceData] = useState<PricePoint[]>([]);
  const [symbol, setSymbol] = useState("AAPL");
  const [hours, setHours] = useState(24);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [sentResult, priceResult] = await Promise.all([
          fetchApi<{ trend: TrendPoint[] }>(`/api/sentiment/trend?hours=${hours}&interval=60`),
          fetchApi<{ data: Array<Record<string, unknown>> }>(`/api/market/${symbol}?hours=${hours}`),
        ]);
        setSentimentData(sentResult.trend || []);
        setPriceData(
          (priceResult.data || []).map((d: Record<string, unknown>) => ({
            timestamp: d.timestamp as string,
            price: Number(d.price) || 0,
          }))
        );
      } catch {
        setSentimentData([]);
        setPriceData([]);
      }
      setLoading(false);
    };
    load();
  }, [symbol, hours]);

  const priceByHour: Record<string, number> = {};
  priceData.forEach((p) => {
    const h = new Date(p.timestamp).getHours().toString().padStart(2, "0") + ":00";
    priceByHour[h] = p.price;
  });

  const merged = sentimentData.map((s) => {
    const h = new Date(s.timestamp).getHours().toString().padStart(2, "0") + ":00";
    return {
      time: h,
      sentiment_score: s.bullish_count - s.bearish_count,
      price: priceByHour[h] || null,
    };
  });

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
          <Activity className={`h-5 w-5 ${light ? "text-cyan-600" : "text-cyan-400"}`} />
          <h3 className={`text-lg font-bold ${textPrimary}`}>Sentiment-Price Correlation</h3>
        </div>
        <div className="flex gap-2">
          <input
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            className={`w-24 px-3 py-1.5 rounded-lg text-sm font-mono focus:outline-none ${light ? "bg-white border border-slate-200 text-slate-800 focus:border-cyan-400" : "bg-white/[0.05] border border-white/[0.1] text-white focus:border-cyan-500/50"}`}
          />
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
      ) : merged.length === 0 ? (
        <div className={`text-center py-20 ${textMuted} text-sm`}>No data available</div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={merged}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="time" tick={{ fontSize: 10, fill: textColor }} tickLine={false} axisLine={false} />
            <YAxis yAxisId="sentiment" tick={{ fontSize: 10, fill: textColor }} tickLine={false} axisLine={false} label={{ value: "Sentiment", angle: -90, position: "insideLeft", style: { fontSize: 10, fill: textColor } }} />
            <YAxis yAxisId="price" orientation="right" tick={{ fontSize: 10, fill: textColor }} tickLine={false} axisLine={false} tickFormatter={(v: number) => `$${v}`} label={{ value: "Price", angle: 90, position: "insideRight", style: { fontSize: 10, fill: textColor } }} />
            <Tooltip contentStyle={{ background: tooltipBg, border: `1px solid ${tooltipBorder}`, borderRadius: "8px", fontSize: "12px", color: tooltipColor }} />
            <Legend wrapperStyle={{ fontSize: "11px", color: legendColor }} />
            <Bar yAxisId="sentiment" dataKey="sentiment_score" fill="rgba(0, 240, 255, 0.3)" radius={[2, 2, 0, 0]} name="Sentiment Score" />
            <Line yAxisId="price" type="monotone" dataKey="price" stroke="#a855f7" strokeWidth={2} dot={false} name="Price" connectNulls />
          </ComposedChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
