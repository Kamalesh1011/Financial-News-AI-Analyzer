import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { ImpactAnalysis } from "@/lib/api";

interface ImpactViewProps {
  impacts: ImpactAnalysis[];
}

function RiskBadge({ level }: { level: string }) {
  const styles = {
    high: "bg-red-500/10 text-red-400 border-red-500/20",
    medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    low: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  };

  const icons = {
    high: "🔴",
    medium: "🟡",
    low: "🟢",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border",
        styles[level as keyof typeof styles] || styles.low
      )}
    >
      {icons[level as keyof typeof icons] || "🟢"} {level.toUpperCase()}
    </span>
  );
}

function AssetChip({ symbol, direction }: { symbol: string; direction: string }) {
  const styles = {
    bullish: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    bearish: "bg-red-500/10 text-red-400 border-red-500/20",
    neutral: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  };

  const icons = {
    bullish: "📈",
    bearish: "📉",
    neutral: "➡️",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium border",
        styles[direction as keyof typeof styles] || styles.neutral
      )}
    >
      {icons[direction as keyof typeof icons] || "➡️"} {symbol}
    </span>
  );
}

export function ImpactView({ impacts }: ImpactViewProps) {
  if (!impacts.length) {
    return (
      <div className="text-center py-16">
        <div className="text-4xl mb-4">🎯</div>
        <h3 className="text-lg font-semibold text-white mb-2">No impact data yet</h3>
        <p className="text-slate-400">The Impact Mapper agent will correlate news with assets.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">🎯 Impact Analysis</h2>
        <span className="text-xs text-slate-500">Asset correlation mapping</span>
      </div>

      <div className="space-y-4">
        {impacts.slice(0, 10).map((impact, i) => {
          const scoreColor =
            impact.impact_score >= 7
              ? "text-red-400 bg-red-500/10"
              : impact.impact_score >= 4
              ? "text-amber-400 bg-amber-500/10"
              : "text-emerald-400 bg-emerald-500/10";

          return (
            <motion.div
              key={impact.id || i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className={cn(
                "rounded-xl p-5 glass-card transition-all duration-300",
                impact.risk_level === "high" && "border-l-2 border-l-red-500 hover:border-red-400/50 hover:shadow-[0_0_20px_rgba(239,68,68,0.15)]",
                impact.risk_level === "medium" && "border-l-2 border-l-amber-500 hover:border-amber-400/50 hover:shadow-[0_0_20px_rgba(245,158,11,0.15)]",
                impact.risk_level === "low" && "border-l-2 border-l-emerald-500 hover:border-emerald-400/50 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)]"
              )}
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="font-semibold text-white text-sm leading-snug">
                  {impact.news_title?.slice(0, 80)}...
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <div
                    className={cn(
                      "px-2 py-1 rounded-lg font-bold text-lg",
                      scoreColor
                    )}
                  >
                    {impact.impact_score}/10
                  </div>
                  <RiskBadge level={impact.risk_level} />
                </div>
              </div>

              {impact.reasoning && (
                <p className="text-xs text-slate-400 mb-3 line-clamp-2">
                  {impact.reasoning.slice(0, 200)}
                </p>
              )}

              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs text-slate-500">Affected:</span>
                {impact.affected_assets?.slice(0, 5).map((asset) => (
                  <AssetChip
                    key={asset.symbol}
                    symbol={asset.symbol}
                    direction={asset.direction}
                  />
                ))}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
