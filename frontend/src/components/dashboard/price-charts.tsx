import { useEffect, useState } from "react";
import {
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Bar,
  ComposedChart,
} from "recharts";
import { TrendingUp } from "lucide-react";
import { fetchApi } from "@/lib/api";
import { useTheme } from "@/contexts/ThemeContext";

interface PricePoint {
  timestamp: string;
  price: number;
  volume?: number;
}

export function PriceCharts({ symbol }: { symbol?: string }) {
  const { theme } = useTheme();
  const light = theme === "light";
  const [data, setData] = useState<PricePoint[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState(symbol || "AAPL");
  const [hours, setHours] = useState(24);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const result = await fetchApi<{ data: Array<Record<string, unknown>> }>(
          `/api/market/${selectedSymbol}?hours=${hours}`
        );
        setData(
          (result.data || []).map((d) => ({
            timestamp: d.timestamp as string,
            price: Number(d.price) || 0,
            volume: Number(d.volume) || 0,
          }))
        );
      } catch {
        setData([]);
      }
      setLoading(false);
    };
    load();
  }, [selectedSymbol, hours]);

  const formatted = data.map((d) => ({
    ...d,
    time: new Date(d.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    date: new Date(d.timestamp).toLocaleDateString([], { month: "short", day: "numeric" }),
    volume: d.volume || 0,
  }));

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
          <TrendingUp className={`h-5 w-5 ${light ? "text-cyan-600" : "text-cyan-400"}`} />
          <h3 className={`text-lg font-bold ${textPrimary}`}>Price Chart</h3>
        </div>
        <div className="flex gap-2">
          <input
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
            className={`w-24 px-3 py-1.5 rounded-lg text-sm font-mono focus:outline-none ${light ? "bg-white border border-slate-200 text-slate-800 focus:border-cyan-400" : "bg-white/[0.05] border border-white/[0.1] text-white focus:border-cyan-500/50"}`}
            placeholder="Symbol"
          />
          {[1, 4, 24, 72].map((h) => (
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
          No price data available for {selectedSymbol}
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={formatted}>
            <defs>
              <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#00f0ff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="time" tick={{ fontSize: 10, fill: textColor }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 10, fill: textColor }} tickLine={false} axisLine={false} domain={["dataMin - 1", "dataMax + 1"]} tickFormatter={(v: number) => `$${v.toFixed(2)}`} />
            <Tooltip contentStyle={{ background: tooltipBg, border: `1px solid ${tooltipBorder}`, borderRadius: "8px", fontSize: "12px", color: tooltipColor }} formatter={(value) => [`$${Number(value).toFixed(2)}`, "Price"]} />
            <Area type="monotone" dataKey="price" stroke="#00f0ff" strokeWidth={2} fill="url(#priceGrad)" dot={false} animationDuration={1000} />
            {formatted.some((d) => (d.volume ?? 0) > 0) && (
              <Bar dataKey="volume" fill="rgba(168, 85, 247, 0.15)" yAxisId="volume" />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
