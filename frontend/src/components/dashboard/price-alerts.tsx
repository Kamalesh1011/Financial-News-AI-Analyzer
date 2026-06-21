import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, Trash2, AlertCircle } from "lucide-react";
import { fetchApi } from "@/lib/api";
import { showToast } from "@/components/ui/toast";

interface Alert {
  id: string;
  symbol: string;
  target_price: number;
  direction: "above" | "below";
  active: boolean;
}

interface PriceAlertFormProps {
  onAlertCreated?: () => void;
}

export function PriceAlertForm({ onAlertCreated }: PriceAlertFormProps) {
  const [symbol, setSymbol] = useState("");
  const [targetPrice, setTargetPrice] = useState("");
  const [direction, setDirection] = useState<"above" | "below">("above");
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol.trim() || !targetPrice) return;

    setLoading(true);
    try {
      const newAlert = await fetchApi<{ alert: Alert }>("/api/alerts/price", {
        method: "POST",
        body: JSON.stringify({
          symbol: symbol.trim().toUpperCase(),
          target_price: parseFloat(targetPrice),
          direction,
        }),
      });
      setAlerts((prev) => [...prev, newAlert.alert]);
      setSymbol("");
      setTargetPrice("");
      showToast("Price alert created", "success");
      onAlertCreated?.();
    } catch {
      showToast("Failed to create alert", "error");
    }
    setLoading(false);
  };

  const deleteAlert = async (id: string) => {
    try {
      await fetchApi(`/api/alerts/price/${id}`, { method: "DELETE" });
      setAlerts((prev) => prev.filter((a) => a.id !== id));
      showToast("Alert deleted", "success");
    } catch {
      showToast("Failed to delete alert", "error");
    }
  };

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <Bell className="h-5 w-5 text-cyan-400" />
        <h3 className="text-lg font-bold text-white">Price Alerts</h3>
      </div>

      <form onSubmit={handleSubmit} className="flex items-end gap-3 mb-4 flex-wrap">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Symbol</label>
          <input
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            placeholder="AAPL"
            className="px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm font-mono focus:outline-none focus:border-cyan-500/50 w-24"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Target Price ($)</label>
          <input
            type="number"
            value={targetPrice}
            onChange={(e) => setTargetPrice(e.target.value)}
            placeholder="150.00"
            step="0.01"
            className="px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm font-mono focus:outline-none focus:border-cyan-500/50 w-28"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Direction</label>
          <select
            value={direction}
            onChange={(e) => setDirection(e.target.value as "above" | "below")}
            className="px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm focus:outline-none focus:border-cyan-500/50"
          >
            <option value="above">Above ↑</option>
            <option value="below">Below ↓</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={loading || !symbol.trim() || !targetPrice}
          className="px-4 py-2 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-sm font-medium hover:bg-cyan-500/30 transition-all disabled:opacity-50"
        >
          {loading ? "Creating..." : "Create Alert"}
        </button>
      </form>

      <AnimatePresence>
        {alerts.length > 0 && (
          <div className="space-y-2">
            {alerts.map((alert) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="flex items-center justify-between p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]"
              >
                <div className="flex items-center gap-3">
                  <AlertCircle className="h-4 w-4 text-amber-400" />
                  <span className="text-sm font-mono text-white">{alert.symbol}</span>
                  <span className="text-xs text-slate-400">
                    {alert.direction === "above" ? "↑ Above" : "↓ Below"} ${alert.target_price.toFixed(2)}
                  </span>
                </div>
                <button
                  onClick={() => deleteAlert(alert.id)}
                  className="p-1.5 rounded-lg hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-all"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </motion.div>
            ))}
          </div>
        )}
      </AnimatePresence>

      {alerts.length === 0 && (
        <p className="text-xs text-slate-500 text-center py-4">No active price alerts</p>
      )}
    </div>
  );
}
