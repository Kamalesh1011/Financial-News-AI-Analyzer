import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string | number;
  icon: string;
  delta?: string;
  deltaType?: "positive" | "negative" | "neutral";
  subtext?: string;
  borderColor?: string;
}

function KpiCard({
  label,
  value,
  icon,
  delta,
  deltaType = "neutral",
  subtext,
  borderColor = "border-blue-500",
}: KpiCardProps) {
  const deltaColors = {
    positive: "text-emerald-500",
    negative: "text-red-500",
    neutral: "text-[var(--text-muted)]",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "relative overflow-hidden rounded-2xl glass-card",
        "p-5 transition-all duration-300 hover:-translate-y-1",
        "group"
      )}
    >
      <div className={cn("absolute left-0 top-0 bottom-0 w-[3px]", borderColor)} />

      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <span className="text-xl">{icon}</span>
          <span className="text-sm font-medium text-[var(--text-secondary)] tracking-wide">
            {label}
          </span>
        </div>
        {subtext && (
          <span className="text-xs text-[var(--text-muted)]">{subtext}</span>
        )}
      </div>

      <div className="text-3xl font-bold text-[var(--text-primary)] mb-1.5 tracking-tight">
        {value}
      </div>

      {delta && (
        <div className={cn("text-sm font-medium", deltaColors[deltaType])}>
          {deltaType === "positive" && "↑ "}
          {deltaType === "negative" && "↓ "}
          {delta}
        </div>
      )}
    </motion.div>
  );
}

interface KpiRowProps {
  newsCount: number;
  bullishPct: number;
  highImpact: number;
  alertsSent: number;
}

export function KpiRow({ newsCount, bullishPct, highImpact, alertsSent }: KpiRowProps) {
  const sentimentLabel = bullishPct >= 50 ? "Bullish" : bullishPct < 40 ? "Bearish" : "Neutral";
  const sentimentIcon = bullishPct >= 50 ? "📈" : bullishPct < 40 ? "📉" : "➡️";
  const riskLabel = highImpact >= 5 ? "High" : highImpact >= 2 ? "Medium" : "Low";
  const riskIcon = highImpact >= 5 ? "🔴" : highImpact >= 2 ? "🟡" : "🟢";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <KpiCard
        label="News Today"
        value={newsCount}
        icon="📰"
        delta="+12 vs yesterday"
        deltaType="positive"
        borderColor="border-blue-500"
      />
      <KpiCard
        label="Market Sentiment"
        value={`${bullishPct.toFixed(0)}%`}
        icon="📊"
        subtext={`${sentimentIcon} ${sentimentLabel}`}
        delta="+2.3% from 24h"
        deltaType={bullishPct >= 50 ? "positive" : "negative"}
        borderColor={bullishPct >= 50 ? "border-emerald-500" : bullishPct < 40 ? "border-red-500" : "border-amber-500"}
      />
      <KpiCard
        label="High Impact Events"
        value={highImpact}
        icon="⚡"
        subtext={`${riskIcon} ${riskLabel} Risk`}
        delta="-1 from peak"
        deltaType={highImpact > 3 ? "negative" : "positive"}
        borderColor={highImpact >= 5 ? "border-red-500" : highImpact >= 2 ? "border-amber-500" : "border-emerald-500"}
      />
      <KpiCard
        label="Alerts Sent"
        value={alertsSent}
        icon="🔔"
        subtext="✅ Active"
        delta="+3 this hour"
        deltaType="neutral"
        borderColor="border-cyan-500"
      />
    </div>
  );
}
