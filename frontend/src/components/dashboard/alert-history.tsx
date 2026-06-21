import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { Alert } from "@/lib/api";

interface AlertHistoryProps {
  alerts: Alert[];
}

export function AlertHistory({ alerts }: AlertHistoryProps) {
  if (!alerts.length) {
    return (
      <div className="text-center py-16">
        <div className="text-4xl mb-4">🔔</div>
        <h3 className="text-lg font-semibold text-white mb-2">No alerts sent yet</h3>
        <p className="text-slate-400">The Alert Engine will notify you of important events.</p>
      </div>
    );
  }

  const typeStyles: Record<string, { icon: string; color: string }> = {
    high_impact: { icon: "🚨", color: "border-l-red-500" },
    sentiment_shift: { icon: "📊", color: "border-l-amber-500" },
    price_move: { icon: "📈", color: "border-l-emerald-500" },
    info: { icon: "ℹ️", color: "border-l-blue-500" },
  };

  const channelIcons: Record<string, string> = {
    email: "📨",
    telegram: "📱",
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">🔔 Alert History</h2>
        <span className="text-xs text-slate-500">Recent notifications</span>
      </div>

      <div className="space-y-3">
        {alerts.slice(0, 10).map((alert, i) => {
          const style = typeStyles[alert.type] || typeStyles.info;
          const channelIcon = channelIcons[alert.channel] || "🔔";

          return (
            <motion.div
              key={alert.id || i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className={cn(
                "rounded-xl p-4",
                "bg-white/[0.02] backdrop-blur-sm",
                "border border-white/[0.06]",
                "border-l-2",
                style.color,
                "hover:bg-white/[0.04] transition-all duration-200"
              )}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{style.icon}</span>
                  <div>
                    <div className="font-semibold text-white text-sm">{alert.title}</div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      {new Date(alert.timestamp).toLocaleString()} • {channelIcon}{" "}
                      {alert.channel?.charAt(0).toUpperCase() + alert.channel?.slice(1)}
                    </div>
                  </div>
                </div>
              </div>

              {alert.message && (
                <p className="text-xs text-slate-400 mt-2 ml-9 line-clamp-2">
                  {alert.message.slice(0, 150)}
                </p>
              )}

              {alert.assets?.length > 0 && (
                <div className="flex items-center gap-2 flex-wrap mt-3 ml-9">
                  {alert.assets.slice(0, 4).map((asset) => (
                    <span
                      key={asset}
                      className="inline-flex items-center px-2 py-1 rounded-md bg-white/[0.05] border border-white/[0.08] text-xs text-slate-300"
                    >
                      {asset}
                    </span>
                  ))}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
