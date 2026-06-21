import { useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { WatchlistItem } from "@/lib/api";
import { showToast } from "@/components/ui/toast";

interface WatchlistManagerProps {
  watchlist: WatchlistItem[];
  onAdd: (symbol: string, assetType: string) => void;
  onRemove: (symbol: string) => void;
}

export function WatchlistManager({ watchlist, onAdd, onRemove }: WatchlistManagerProps) {
  const [newSymbol, setNewSymbol] = useState("");
  const [assetType, setAssetType] = useState("stock");
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const handleAdd = () => {
    if (newSymbol.trim()) {
      onAdd(newSymbol.toUpperCase(), assetType);
      showToast(`Added ${newSymbol.toUpperCase()} to watchlist`, "success");
      setNewSymbol("");
    }
  };

  const handleRemove = (symbol: string) => {
    onRemove(symbol);
    showToast(`Removed ${symbol} from watchlist`, "success");
    setConfirmDelete(null);
  };

  const stocks = watchlist.filter((w) => w.asset_type === "stock" || !w.asset_type);
  const crypto = watchlist.filter((w) => w.asset_type === "crypto");
  const forex = watchlist.filter((w) => w.asset_type === "forex");

  const typeEmoji: Record<string, string> = {
    stock: "💹",
    crypto: "₿",
    forex: "💱",
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-[var(--text-primary)]">👁️ Watchlist</h2>
        <span className="text-xs text-[var(--text-muted)]">Tracked assets</span>
      </div>

      {/* Add Asset Form */}
      <div className="rounded-xl p-4 bg-[var(--bg-elevated)] border border-[var(--border-subtle)] mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAdd()}
            placeholder="Add symbol (e.g., TSLA)"
            className={cn(
              "flex-1 px-3 py-2 rounded-lg",
              "bg-[var(--bg-elevated)] border border-[var(--border-subtle)]",
              "text-[var(--text-primary)] text-sm placeholder:text-[var(--text-muted)]",
              "focus:outline-none focus:border-cyan-500/50",
              "transition-colors"
            )}
          />
          <select
            value={assetType}
            onChange={(e) => setAssetType(e.target.value)}
            className={cn(
              "px-3 py-2 rounded-lg",
              "bg-[var(--bg-elevated)] border border-[var(--border-subtle)]",
              "text-[var(--text-primary)] text-sm",
              "focus:outline-none focus:border-cyan-500/50",
              "transition-colors"
            )}
          >
            <option value="stock">Stock</option>
            <option value="crypto">Crypto</option>
            <option value="forex">Forex</option>
          </select>
          <button
            onClick={handleAdd}
            className={cn(
              "px-4 py-2 rounded-lg",
              "bg-cyan-500/20 text-cyan-500 border border-cyan-500/30",
              "text-sm font-medium",
              "hover:bg-cyan-500/30 transition-all"
            )}
          >
            Add
          </button>
        </div>
      </div>

      {/* Watchlist Groups */}
      {watchlist.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">👁️</div>
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">Watchlist is empty</h3>
          <p className="text-[var(--text-secondary)]">Add assets to track sentiment and impact.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {[
            { label: "Stocks", emoji: "💹", items: stocks },
            { label: "Crypto", emoji: "₿", items: crypto },
            { label: "Forex", emoji: "💱", items: forex },
          ]
            .filter((g) => g.items.length > 0)
            .map((group) => (
              <div key={group.label}>
                <div className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
                  {group.emoji} {group.label} ({group.items.length})
                </div>
                <div className="space-y-1">
                  {group.items.map((item) => (
                    <motion.div
                      key={item.symbol}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={cn(
                        "flex items-center justify-between p-2 rounded-lg",
                        "bg-[var(--bg-elevated)] border border-[var(--border-subtle)]",
                        "hover:bg-[var(--bg-elevated)] transition-all duration-200"
                      )}
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-sm">{typeEmoji[item.asset_type] || "📊"}</span>
                        <span className="font-medium text-[var(--text-primary)] text-sm">{item.symbol}</span>
                        <span className="text-xs text-[var(--text-muted)] uppercase">{item.asset_type}</span>
                      </div>
                      {confirmDelete === item.symbol ? (
                        <div className="flex items-center gap-1.5">
                          <span className="text-xs text-red-400 mr-1">Remove?</span>
                          <button
                            onClick={() => handleRemove(item.symbol)}
                            className="px-2 py-0.5 rounded text-xs bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 transition-all"
                          >
                            Yes
                          </button>
                          <button
                            onClick={() => setConfirmDelete(null)}
                            className="px-2 py-0.5 rounded text-xs bg-[var(--bg-elevated)] text-[var(--text-secondary)] border border-[var(--border-subtle)] hover:bg-[var(--bg-elevated)] transition-all"
                          >
                            No
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setConfirmDelete(item.symbol)}
                          className="text-[var(--text-muted)] hover:text-red-400 transition-colors text-sm"
                        >
                          🗑️
                        </button>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
