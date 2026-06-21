import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown } from "lucide-react";
import { fetchApi } from "@/lib/api";
import type { WatchlistItem } from "@/lib/api";

interface PerformanceItem extends WatchlistItem {
  currentPrice: number;
  change24h: number;
  history: number[];
}

function Sparkline({ data, positive }: { data: number[]; positive: boolean }) {
  if (data.length < 2) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const h = 30;
  const w = 80;
  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / range) * h;
    return `${x},${y}`;
  }).join(" ");

  return (
    <svg width={w} height={h} className="inline-block">
      <polyline
        points={points}
        fill="none"
        stroke={positive ? "#22c55e" : "#ef4444"}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function WatchlistPerformance() {
  const [items, setItems] = useState<PerformanceItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const wl = await fetchApi<{ watchlist: WatchlistItem[] }>("/api/watchlist");
        const watchlist = wl.watchlist || [];
        const results: PerformanceItem[] = [];

        for (const item of watchlist) {
          try {
            const hist = await fetchApi<{ data: Array<{ price: number; timestamp: string }> }>(
              `/api/market/${item.symbol}?hours=24`
            );
            const prices = (hist.data || []).map((d) => d.price);
            const current = prices[prices.length - 1] || 0;
            const prev = prices[0] || current;
            const change = prev > 0 ? ((current - prev) / prev) * 100 : 0;
            results.push({
              ...item,
              currentPrice: current,
              change24h: change,
              history: prices,
            });
          } catch {
            results.push({
              ...item,
              currentPrice: 0,
              change24h: 0,
              history: [],
            });
          }
        }

        setItems(results);
      } catch {
        setItems([]);
      }
      setLoading(false);
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center justify-center py-10">
          <div className="w-5 h-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="glass-card rounded-2xl p-6 text-center text-slate-400 py-10">
        Add items to your watchlist to track performance
      </div>
    );
  }

  return (
    <div className="glass-card rounded-2xl p-6">
      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <TrendingUp className="h-5 w-5 text-cyan-400" />
        Watchlist Performance
      </h3>
      <div className="space-y-2">
        {items.map((item, i) => (
          <motion.div
            key={item.symbol}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
            className="flex items-center justify-between p-3 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.05] transition-all"
          >
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-500 font-mono uppercase w-6">{item.asset_type === "crypto" ? "₿" : "💹"}</span>
              <div>
                <span className="text-sm font-bold text-white font-mono">{item.symbol}</span>
                <span className="text-xs text-slate-500 ml-2 uppercase">{item.asset_type}</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Sparkline data={item.history} positive={item.change24h >= 0} />
              <div className="text-right w-20">
                <div className="text-sm font-mono text-white">${item.currentPrice.toFixed(2)}</div>
                <div className={`text-xs font-mono flex items-center gap-1 justify-end ${item.change24h >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                  {item.change24h >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  {item.change24h >= 0 ? "+" : ""}{item.change24h.toFixed(2)}%
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
