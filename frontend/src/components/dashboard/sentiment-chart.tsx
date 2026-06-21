import { motion } from "framer-motion";
import type { SentimentDistribution } from "@/lib/api";

interface SentimentChartProps {
  data: SentimentDistribution[];
}

export function SentimentChart({ data }: SentimentChartProps) {
  if (!data.length) {
    return (
      <div className="text-center py-16">
        <div className="text-4xl mb-4">📊</div>
        <h3 className="text-lg font-semibold text-white mb-2">No sentiment data yet</h3>
        <p className="text-slate-400">The Sentiment Analyzer agent will process news articles.</p>
      </div>
    );
  }

  const total = data.reduce((sum, d) => sum + d.count, 0);
  const bullish = data.find((d) => d.sentiment === "bullish")?.count || 0;
  const bearish = data.find((d) => d.sentiment === "bearish")?.count || 0;
  const neutral = data.find((d) => d.sentiment === "neutral")?.count || 0;

  const bullishPct = total > 0 ? (bullish / total) * 100 : 0;
  const bearishPct = total > 0 ? (bearish / total) * 100 : 0;
  const neutralPct = total > 0 ? (neutral / total) * 100 : 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">📊 Sentiment Distribution</h2>
        <span className="text-xs text-slate-500">Last 24h analysis</span>
      </div>

      {/* Donut Chart */}
      <div className="relative flex items-center justify-center mb-8">
        <svg viewBox="0 0 200 200" className="w-48 h-48">
          {/* Background circle */}
          <circle cx="100" cy="100" r="80" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="20" />
          
          {/* Bullish segment */}
          {bullishPct > 0 && (
            <motion.circle
              cx="100"
              cy="100"
              r="80"
              fill="none"
              stroke="#10b981"
              strokeWidth="20"
              strokeDasharray={`${(bullishPct / 100) * 502.65} 502.65`}
              strokeDashoffset="0"
              transform="rotate(-90 100 100)"
              initial={{ strokeDasharray: "0 502.65" }}
              animate={{ strokeDasharray: `${(bullishPct / 100) * 502.65} 502.65` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          )}
          
          {/* Bearish segment */}
          {bearishPct > 0 && (
            <motion.circle
              cx="100"
              cy="100"
              r="80"
              fill="none"
              stroke="#ef4444"
              strokeWidth="20"
              strokeDasharray={`${(bearishPct / 100) * 502.65} 502.65`}
              strokeDashoffset={`${-(bullishPct / 100) * 502.65}`}
              transform="rotate(-90 100 100)"
              initial={{ strokeDasharray: "0 502.65" }}
              animate={{ strokeDasharray: `${(bearishPct / 100) * 502.65} 502.65` }}
              transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
            />
          )}
          
          {/* Neutral segment */}
          {neutralPct > 0 && (
            <motion.circle
              cx="100"
              cy="100"
              r="80"
              fill="none"
              stroke="#f59e0b"
              strokeWidth="20"
              strokeDasharray={`${(neutralPct / 100) * 502.65} 502.65`}
              strokeDashoffset={`${-((bullishPct + bearishPct) / 100) * 502.65}`}
              transform="rotate(-90 100 100)"
              initial={{ strokeDasharray: "0 502.65" }}
              animate={{ strokeDasharray: `${(neutralPct / 100) * 502.65} 502.65` }}
              transition={{ duration: 1, ease: "easeOut", delay: 0.6 }}
            />
          )}
        </svg>
        
        {/* Center text */}
        <div className="absolute inset-0 flex items-center justify-center flex-col">
          <div className="text-3xl font-bold text-white">{total}</div>
          <div className="text-xs text-slate-400">Total</div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex justify-center gap-6">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500" />
          <span className="text-sm text-slate-300">Bullish ({bullishPct.toFixed(0)}%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span className="text-sm text-slate-300">Bearish ({bearishPct.toFixed(0)}%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-amber-500" />
          <span className="text-sm text-slate-300">Neutral ({neutralPct.toFixed(0)}%)</span>
        </div>
      </div>
    </div>
  );
}
