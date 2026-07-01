import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Search, X } from "lucide-react";
import { cn } from "@/lib/utils";
import type { WatchlistItem } from "@/lib/api";
import { showToast } from "@/components/ui/toast";

interface WatchlistManagerProps {
  watchlist: WatchlistItem[];
  onAdd: (symbol: string, assetType: string) => void;
  onRemove: (symbol: string) => void;
}

const assetTypeOptions = [
  { value: "stock", label: "Stock" },
  { value: "crypto", label: "Crypto" },
  { value: "forex", label: "Forex" },
  { value: "etf", label: "ETF" },
  { value: "commodity", label: "Commodity" },
];

export function WatchlistManager({ watchlist, onAdd, onRemove }: WatchlistManagerProps) {
  const [newSymbol, setNewSymbol] = useState("");
  const [assetType, setAssetType] = useState("stock");
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");

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

  const filtered = useMemo(() => {
    let items = watchlist;
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(
        (w) =>
          w.symbol.toLowerCase().includes(q) ||
          w.asset_type?.toLowerCase().includes(q)
      );
    }
    if (typeFilter !== "all") {
      items = items.filter((w) => w.asset_type === typeFilter);
    }
    return items;
  }, [watchlist, search, typeFilter]);

  const stocks = filtered.filter((w) => w.asset_type === "stock" || !w.asset_type);
  const crypto = filtered.filter((w) => w.asset_type === "crypto");
  const forex = filtered.filter((w) => w.asset_type === "forex");
  const etf = filtered.filter((w) => w.asset_type === "etf");
  const commodity = filtered.filter((w) => w.asset_type === "commodity");

  const typeEmoji: Record<string, string> = {
    stock: "💹",
    crypto: "₿",
    forex: "💱",
    etf: "📊",
    commodity: "🥇",
  };

  const groups = [
    { label: "Stocks", emoji: "💹", items: stocks },
    { label: "Crypto", emoji: "₿", items: crypto },
    { label: "Forex", emoji: "💱", items: forex },
    { label: "ETF", emoji: "📊", items: etf },
    { label: "Commodity", emoji: "🥇", items: commodity },
  ].filter((g) => g.items.length > 0);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-[var(--text-primary)]">👁️ Watchlist</h2>
        <span className="text-xs text-[var(--text-muted)]">{watchlist.length} tracked assets</span>
      </div>

      {/* Add Asset Form */}
      <div className="rounded-xl p-4 bg-[var(--bg-elevated)] border border-[var(--border-subtle)] mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAdd()}
            placeholder="Add symbol (e.g., TSLA)"
            className={cn(
              "flex-1 px-3 py-2 rounded-lg",
              "bg-[var(--bg-surface)] border border-[var(--border-subtle)]",
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
              "bg-[var(--bg-surface)] border border-[var(--border-subtle)]",
              "text-[var(--text-primary)] text-sm",
              "focus:outline-none focus:border-cyan-500/50",
              "transition-colors appearance-none min-w-[100px]"
            )}
            style={{ colorScheme: "dark" }}
          >
            {assetTypeOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
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

      {/* Search and Filter */}
      <div className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter watchlist..."
            className={cn(
              "w-full pl-9 pr-8 py-2 rounded-lg",
              "bg-[var(--bg-elevated)] border border-[var(--border-subtle)]",
              "text-[var(--text-primary)] text-sm placeholder:text-[var(--text-muted)]",
              "focus:outline-none focus:border-cyan-500/50",
              "transition-colors"
            )}
          />
          {search && (
            <button
              onClick={() => setSearch("")}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
        <div className="flex gap-1 bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded-lg p-0.5">
          {[
            { value: "all", label: "All" },
            { value: "stock", label: "💹" },
            { value: "crypto", label: "₿" },
            { value: "forex", label: "💱" },
            { value: "etf", label: "📊" },
          ].map((f) => (
            <button
              key={f.value}
              onClick={() => setTypeFilter(f.value)}
              className={cn(
                "px-2 py-1 rounded-md text-xs transition-all",
                typeFilter === f.value
                  ? "bg-cyan-500/20 text-cyan-400"
                  : "text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              )}
              title={f.value === "all" ? "All types" : f.value}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Watchlist Groups */}
      {watchlist.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">👁️</div>
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">Watchlist is empty</h3>
          <p className="text-[var(--text-secondary)]">Add assets to track sentiment and impact.</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">No matches</h3>
          <p className="text-[var(--text-secondary)]">Try a different search or filter.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {groups.map((group) => (
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
