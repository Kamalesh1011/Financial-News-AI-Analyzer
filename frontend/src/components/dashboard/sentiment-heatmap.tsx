import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Grid3x3 } from "lucide-react";
import { fetchApi } from "@/lib/api";
import { useTheme } from "@/contexts/ThemeContext";

interface TickerSentiment {
  ticker: string;
  bullish: number;
  bearish: number;
  neutral: number;
}

function getHeatColor(bullish: number, bearish: number, neutral: number, light: boolean): string {
  const total = bullish + bearish + neutral;
  if (total === 0) return light ? "rgba(148, 163, 184, 0.12)" : "rgba(148, 163, 184, 0.1)";
  const score = (bullish - bearish) / total;
  if (light) {
    if (score > 0.5) return "rgba(34, 197, 94, 0.2)";
    if (score > 0.2) return "rgba(34, 197, 94, 0.12)";
    if (score > -0.2) return "rgba(148, 163, 184, 0.1)";
    if (score > -0.5) return "rgba(239, 68, 68, 0.12)";
    return "rgba(239, 68, 68, 0.2)";
  }
  if (score > 0.5) return "rgba(34, 197, 94, 0.6)";
  if (score > 0.2) return "rgba(34, 197, 94, 0.3)";
  if (score > -0.2) return "rgba(148, 163, 184, 0.15)";
  if (score > -0.5) return "rgba(239, 68, 68, 0.3)";
  return "rgba(239, 68, 68, 0.6)";
}

export function SentimentHeatmap() {
  const { theme } = useTheme();
  const light = theme === "light";
  const [data, setData] = useState<TickerSentiment[]>([]);
  const [hours, setHours] = useState(24);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const result = await fetchApi<{ tickers: TickerSentiment[] }>(
          `/api/sentiment/by-ticker?hours=${hours}`
        );
        if (!cancelled) setData(result.tickers || []);
      } catch {
        if (!cancelled) setData([]);
      }
      if (!cancelled) setLoading(false);
    };
    load();
    return () => { cancelled = true; };
  }, [hours]);

  const totalArticles = data.reduce((sum, d) => sum + d.bullish + d.bearish + d.neutral, 0);

  const textPrimary = light ? "text-slate-800" : "text-white";
  const textSecondary = light ? "text-slate-600" : "text-slate-300";
  const textMuted = light ? "text-slate-500" : "text-slate-400";
  const textMutedDark = light ? "text-slate-500" : "text-slate-500";

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Grid3x3 className={`h-5 w-5 ${light ? "text-cyan-600" : "text-cyan-400"}`} />
          <h3 className={`text-lg font-bold ${textPrimary}`}>Sentiment Heatmap by Ticker</h3>
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

      <div className={`text-xs ${textMuted} mb-4 font-mono`}>
        {data.length} tickers • {totalArticles} total articles
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-5 h-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data.length === 0 ? (
        <div className={`text-center py-20 ${textMuted} text-sm`}>No ticker sentiment data available</div>
      ) : (
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
          {data.map((d, i) => {
            const total = d.bullish + d.bearish + d.neutral;
            return (
              <motion.div
                key={d.ticker}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.03 }}
                className="rounded-lg p-3 text-center cursor-default transition-all hover:scale-105"
                style={{ background: getHeatColor(d.bullish, d.bearish, d.neutral, light) }}
                title={`${d.ticker}: 🟢${d.bullish} 🔴${d.bearish} ⚪${d.neutral}`}
              >
                <div className={`text-xs font-mono font-bold ${textPrimary}`}>{d.ticker}</div>
                <div className={`text-[10px] ${textSecondary} mt-1`}>{total} articles</div>
              </motion.div>
            );
          })}
        </div>
      )}

      <div className={`flex items-center justify-center gap-4 mt-4 text-[10px] ${textMutedDark} font-mono`}>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded" style={{ background: light ? "rgba(239,68,68,0.2)" : "rgba(239,68,68,0.5)" }} /> Bearish
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded" style={{ background: light ? "rgba(148,163,184,0.15)" : "rgba(148,163,184,0.15)" }} /> Neutral
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded" style={{ background: light ? "rgba(34,197,94,0.2)" : "rgba(34,197,94,0.5)" }} /> Bullish
        </span>
      </div>
    </div>
  );
}
