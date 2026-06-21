import { useState } from "react";
import { motion } from "framer-motion";
import { Shield, Plus, Trash2 } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { fetchApi } from "@/lib/api";
import { showToast } from "@/components/ui/toast";

interface Holding {
  symbol: string;
  weight: number;
  asset_type: string;
}

interface RiskResult {
  portfolio_volatility: number;
  sharpe_ratio: number;
  var_95: number;
  diversification_score: number;
  risk_breakdown: Array<{
    symbol: string;
    weight: number;
    volatility: number;
    var_95: number;
    contribution: number;
  }>;
}

export function PortfolioRisk() {
  const [holdings, setHoldings] = useState<Holding[]>([
    { symbol: "AAPL", weight: 30, asset_type: "stock" },
    { symbol: "BTC", weight: 20, asset_type: "crypto" },
    { symbol: "NVDA", weight: 25, asset_type: "stock" },
    { symbol: "ETH", weight: 25, asset_type: "crypto" },
  ]);
  const [result, setResult] = useState<RiskResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [newSymbol, setNewSymbol] = useState("");
  const [newWeight, setNewWeight] = useState(10);
  const [newType, setNewType] = useState("stock");

  const addHolding = () => {
    if (!newSymbol) return;
    setHoldings([...holdings, { symbol: newSymbol.toUpperCase(), weight: newWeight, asset_type: newType }]);
    setNewSymbol("");
  };

  const removeHolding = (idx: number) => {
    setHoldings(holdings.filter((_, i) => i !== idx));
  };

  const calculate = async () => {
    if (holdings.length === 0) {
      showToast("Add at least one holding", "error");
      return;
    }
    setLoading(true);
    try {
      const data = await fetchApi<RiskResult>("/api/portfolio/risk", {
        method: "POST",
        body: JSON.stringify({ holdings }),
      });
      setResult(data);
      showToast("Risk calculated successfully", "success");
    } catch {
      showToast("Failed to calculate risk", "error");
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Shield className="h-5 w-5 text-cyan-400" />
          <h3 className="text-lg font-bold text-white">Portfolio Risk Calculator</h3>
        </div>

        <div className="space-y-3 mb-4">
          {holdings.map((h, i) => (
            <motion.div
              key={`${h.symbol}-${i}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]"
            >
              <span className="text-sm font-mono text-white w-16">{h.symbol}</span>
              <span className="text-xs text-slate-400">{h.weight}%</span>
              <span className="text-xs text-slate-500 font-mono">{h.asset_type}</span>
              <button onClick={() => removeHolding(i)} className="ml-auto text-slate-500 hover:text-red-400 transition-colors">
                <Trash2 className="h-4 w-4" />
              </button>
            </motion.div>
          ))}
        </div>

        <div className="flex gap-2 mb-6">
          <input
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value)}
            placeholder="Symbol"
            className="flex-1 px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm font-mono focus:outline-none focus:border-cyan-500/50"
          />
          <input
            type="number"
            value={newWeight}
            onChange={(e) => setNewWeight(Number(e.target.value))}
            className="w-20 px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm font-mono focus:outline-none focus:border-cyan-500/50"
          />
          <select
            value={newType}
            onChange={(e) => setNewType(e.target.value)}
            className="px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm focus:outline-none"
          >
            <option value="stock">Stock</option>
            <option value="crypto">Crypto</option>
            <option value="forex">Forex</option>
          </select>
          <button onClick={addHolding} className="px-3 py-2 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/30 transition-all">
            <Plus className="h-4 w-4" />
          </button>
        </div>

        <button
          onClick={calculate}
          disabled={loading}
          className="w-full py-2.5 rounded-lg bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-white text-sm font-medium border border-cyan-500/30 hover:border-cyan-500/60 transition-all disabled:opacity-50"
        >
          {loading ? "Calculating..." : "Calculate Risk"}
        </button>
      </div>

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Volatility", value: `${(result.portfolio_volatility * 100).toFixed(1)}%` },
              { label: "Sharpe Ratio", value: result.sharpe_ratio.toFixed(2) },
              { label: "VaR (95%)", value: `${(result.var_95 * 100).toFixed(2)}%` },
              { label: "Diversification", value: `${(result.diversification_score * 100).toFixed(0)}%` },
            ].map((m) => (
              <div key={m.label} className="glass-card rounded-xl p-4 text-center">
                <p className="text-xs text-slate-400 font-mono uppercase mb-1">{m.label}</p>
                <p className="text-xl font-bold text-white font-mono">{m.value}</p>
              </div>
            ))}
          </div>

          <div className="glass-card rounded-2xl p-6">
            <h4 className="text-sm font-bold text-white mb-4">Risk Contribution by Asset</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={result.risk_breakdown}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="symbol" tick={{ fontSize: 10, fill: "#64748b" }} />
                <YAxis tick={{ fontSize: 10, fill: "#64748b" }} tickFormatter={(v: number) => `${(v * 100).toFixed(1)}%`} />
                <Tooltip
                  contentStyle={{ background: "rgba(10,10,20,0.95)", border: "1px solid rgba(0,240,255,0.2)", borderRadius: "8px", fontSize: "12px", color: "#fff" }}
                  formatter={(value) => [`${(Number(value) * 100).toFixed(2)}%`, "Contribution"]}
                />
                <Bar dataKey="contribution" fill="#00f0ff" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}
    </div>
  );
}
