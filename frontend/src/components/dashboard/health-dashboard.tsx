import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Activity, Database, Clock, Server } from "lucide-react";
import { fetchApi } from "@/lib/api";

interface SystemHealth {
  database: {
    database: string;
    collections: string[];
    documents: number;
    storage_size_mb: number;
    data_size_mb: number;
  };
  recent_agent_runs: Array<{
    agent_name: string;
    status: string;
    items_processed: number;
    started_at: string;
    error?: string;
  }>;
  timestamp: string;
}

export function HealthDashboard() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchApi<SystemHealth>("/api/health/system");
        setHealth(data);
      } catch {
        // silently fail
      }
      setLoading(false);
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-5 h-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!health) {
    return (
      <div className="glass-card rounded-2xl p-8 text-center text-slate-400">
        Unable to fetch system health data
      </div>
    );
  }

  const agentColors: Record<string, string> = {
    news_collector: "text-cyan-400",
    market_collector: "text-purple-400",
    sentiment_analyzer: "text-yellow-400",
    impact_mapper: "text-rose-400",
    alert_engine: "text-emerald-400",
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Database", value: health.database.database, icon: <Database className="h-5 w-5 text-cyan-400" /> },
          { label: "Documents", value: health.database.documents.toLocaleString(), icon: <Activity className="h-5 w-5 text-purple-400" /> },
          { label: "Storage", value: `${health.database.storage_size_mb} MB`, icon: <Server className="h-5 w-5 text-rose-400" /> },
          { label: "Collections", value: health.database.collections.length.toString(), icon: <Clock className="h-5 w-5 text-emerald-400" /> },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card rounded-xl p-5"
          >
            <div className="flex items-center gap-3 mb-2">
              {stat.icon}
              <span className="text-xs text-slate-400 font-mono uppercase">{stat.label}</span>
            </div>
            <p className="text-2xl font-bold text-white font-mono">{stat.value}</p>
          </motion.div>
        ))}
      </div>

      <div className="glass-card rounded-2xl p-6">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Activity className="h-5 w-5 text-cyan-400" />
          Agent Run History
        </h3>
        {health.recent_agent_runs.length === 0 ? (
          <p className="text-sm text-slate-400">No recent agent runs</p>
        ) : (
          <div className="space-y-3">
            {health.recent_agent_runs.map((run, i) => (
              <motion.div
                key={`${run.agent_name}-${i}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center justify-between p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${run.status === "completed" ? "bg-emerald-400" : run.status === "failed" ? "bg-red-400" : "bg-yellow-400"}`} />
                  <span className={`text-sm font-mono font-medium ${agentColors[run.agent_name] || "text-slate-300"}`}>
                    {run.agent_name}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-400 font-mono">
                  <span>{run.items_processed} items</span>
                  <span className={run.status === "completed" ? "text-emerald-400" : "text-red-400"}>{run.status}</span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
