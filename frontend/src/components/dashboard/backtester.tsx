import { useState } from "react";
import { motion } from "framer-motion";
import { FlaskConical } from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { fetchApi } from "@/lib/api";
import { showToast } from "@/components/ui/toast";

interface BacktestResult {
  symbol: string;
  strategy: string;
  initial_capital: number;
  final_capital: number;
  total_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  total_trades: number;
  equity_curve: Array<{ timestamp: string; equity: number }>;
}

export function Backtester() {
  const [symbol, setSymbol] = useState("AAPL");
  const [strategy, setStrategy] = useState("sentiment_follow");
  const [hours, setHours] = useState(168);
  const [capital, setCapital] = useState(10000);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    try {
      const data = await fetchApi<BacktestResult>("/api/backtest", {
        method: "POST",
        body: JSON.stringify({
          symbol,
          strategy,
          hours,
          initial_capital: capital,
        }),
      });
      setResult(data);
      showToast("Backtest completed", "success");
    } catch {
      showToast("Backtest failed - insufficient data", "error");
    }
    setLoading(false);
  };

  const chartData = result
    ? result.equity_curve.map((e) => ({
        ...e,
        time: new Date(e.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }))
    : [];

  return (
    <div className="space-y-6">
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <FlaskConical className="h-5 w-5 text-cyan-400" />
          <h3 className="text-lg font-bold text-white">Strategy Backtester</h3>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
          <div>
            <label className="text-[10px] text-slate-400 font-mono uppercase block mb-1">Symbol</label>
            <input
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              className="w-full px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm font-mono focus:outline-none focus:border-cyan-500/50"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-400 font-mono uppercase block mb-1">Strategy</label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm focus:outline-none"
            >
              <option value="sentiment_follow">Sentiment Follow</option>
              <option value="sentiment_contrarian">Sentiment Contrarian</option>
              <option value="momentum">Momentum</option>
            </select>
          </div>
          <div>
            <label className="text-[10px] text-slate-400 font-mono uppercase block mb-1">Hours</label>
            <input
              type="number"
              value={hours}
              onChange={(e) => setHours(Number(e.target.value))}
              className="w-full px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm font-mono focus:outline-none focus:border-cyan-500/50"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-400 font-mono uppercase block mb-1">Capital ($)</label>
            <input
              type="number"
              value={capital}
              onChange={(e) => setCapital(Number(e.target.value))}
              className="w-full px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm font-mono focus:outline-none focus:border-cyan-500/50"
            />
          </div>
        </div>

        <button
          onClick={run}
          disabled={loading}
          className="w-full py-2.5 rounded-lg bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-white text-sm font-medium border border-cyan-500/30 hover:border-cyan-500/60 transition-all disabled:opacity-50"
        >
          {loading ? "Running..." : "Run Backtest"}
        </button>
      </div>

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            {[
              { label: "Total Return", value: `${(result.total_return * 100).toFixed(2)}%`, color: result.total_return >= 0 ? "text-emerald-400" : "text-red-400" },
              { label: "Final Capital", value: `$${result.final_capital.toLocaleString()}`, color: "text-white" },
              { label: "Sharpe Ratio", value: result.sharpe_ratio.toFixed(2), color: "text-cyan-400" },
              { label: "Max Drawdown", value: `${(result.max_drawdown * 100).toFixed(2)}%`, color: "text-red-400" },
              { label: "Total Trades", value: result.total_trades.toString(), color: "text-purple-400" },
            ].map((m) => (
              <div key={m.label} className="glass-card rounded-xl p-4 text-center">
                <p className="text-[10px] text-slate-400 font-mono uppercase mb-1">{m.label}</p>
                <p className={`text-lg font-bold font-mono ${m.color}`}>{m.value}</p>
              </div>
            ))}
          </div>

          <div className="glass-card rounded-2xl p-6">
            <h4 className="text-sm font-bold text-white mb-4">
              Equity Curve — {result.symbol} ({result.strategy})
            </h4>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={result.total_return >= 0 ? "#22c55e" : "#ef4444"} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={result.total_return >= 0 ? "#22c55e" : "#ef4444"} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#64748b" }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "#64748b" }} tickLine={false} axisLine={false} tickFormatter={(v: number) => `$${v.toLocaleString()}`} />
                <Tooltip
                  contentStyle={{ background: "rgba(10,10,20,0.95)", border: "1px solid rgba(0,240,255,0.2)", borderRadius: "8px", fontSize: "12px", color: "#fff" }}
                  formatter={(value) => [`$${Number(value).toLocaleString()}`, "Equity"]}
                />
                <Area type="monotone" dataKey="equity" stroke={result.total_return >= 0 ? "#22c55e" : "#ef4444"} strokeWidth={2} fill="url(#equityGrad)" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}
    </div>
  );
}
