import { useState, useMemo } from "react";
import { Search, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";
import type { MarketData } from "@/lib/api";

interface MarketPanelProps {
  data: MarketData[];
}

type SortKey = "symbol" | "price" | "change";
type SortDir = "asc" | "desc";
type FilterType = "all" | "stock" | "crypto" | "forex";

function MarketItem({ asset }: { asset: MarketData }) {
  const isPositive = asset.change_pct > 0;
  const isNegative = asset.change_pct < 0;
  const direction = isPositive ? "bullish" : isNegative ? "bearish" : "neutral";
  const arrow = isPositive ? "📈" : isNegative ? "📉" : "➡️";
  const changeColor = isPositive ? "text-emerald-500" : isNegative ? "text-red-500" : "text-[var(--text-muted)]";

  const formatPrice = (price: number) => {
    if (price >= 1000) return `$${price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
    if (price >= 100) return `$${price.toFixed(2)}`;
    return `$${price.toFixed(4)}`;
  };

  return (
    <div
      className={cn(
        "flex items-center justify-between p-3 rounded-lg",
        "bg-[var(--bg-elevated)] border border-[var(--border-subtle)]",
        "hover:border-[var(--border-medium)] transition-all duration-200",
        direction === "bullish" && "hover:border-emerald-500/20",
        direction === "bearish" && "hover:border-red-500/20"
      )}
    >
      <div className="flex items-center gap-2">
        <span className="text-sm">{arrow}</span>
        <span className="font-semibold text-[var(--text-primary)] text-sm">{asset.symbol}</span>
        <span className="text-[10px] text-[var(--text-muted)] uppercase px-1.5 py-0.5 rounded bg-[var(--bg-elevated)] border border-[var(--border-subtle)]">
          {asset.asset_type}
        </span>
      </div>
      <div className="text-right">
        <div className="font-mono font-semibold text-[var(--text-primary)] text-sm">
          {formatPrice(asset.price)}
        </div>
        <div className={cn("font-mono text-xs", changeColor)}>
          {isPositive ? "+" : ""}{asset.change_pct.toFixed(2)}%
        </div>
      </div>
    </div>
  );
}

export function MarketPanel({ data }: MarketPanelProps) {
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState<FilterType>("all");
  const [sortKey, setSortKey] = useState<SortKey>("symbol");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const filtered = useMemo(() => {
    let result = data;

    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter((d) => d.symbol.toLowerCase().includes(q));
    }

    if (filterType !== "all") {
      result = result.filter((d) => d.asset_type === filterType);
    }

    result = [...result].sort((a, b) => {
      const mul = sortDir === "asc" ? 1 : -1;
      if (sortKey === "symbol") return mul * a.symbol.localeCompare(b.symbol);
      if (sortKey === "price") return mul * (a.price - b.price);
      return mul * (a.change_pct - b.change_pct);
    });

    return result;
  }, [data, search, filterType, sortKey, sortDir]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  if (!data.length) {
    return (
      <div className="text-center py-16">
        <div className="text-4xl mb-4">📈</div>
        <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">No market data yet</h3>
        <p className="text-[var(--text-secondary)]">The Market Collector agent will fetch prices automatically.</p>
      </div>
    );
  }

  const filterButtons: { value: FilterType; label: string }[] = [
    { value: "all", label: "All" },
    { value: "stock", label: "Stocks" },
    { value: "crypto", label: "Crypto" },
    { value: "forex", label: "Forex" },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-[var(--text-primary)]">📈 Market Overview</h2>
        <span className="text-xs text-[var(--text-muted)]">{filtered.length} assets</span>
      </div>

      {/* Search + Filters + Sort */}
      <div className="flex items-center gap-3 mb-5 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search assets..."
            className={cn(
              "w-full pl-9 pr-4 py-2 rounded-lg text-sm",
              "bg-[var(--bg-elevated)] border border-[var(--border-subtle)]",
              "text-[var(--text-primary)] placeholder:text-[var(--text-muted)]",
              "focus:outline-none focus:border-cyan-500/50 transition-all"
            )}
          />
        </div>

        <div className="flex gap-1">
          {filterButtons.map((f) => (
            <button
              key={f.value}
              onClick={() => setFilterType(f.value)}
              className={cn(
                "px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                filterType === f.value
                  ? "bg-cyan-500/15 text-cyan-500 border border-cyan-500/25"
                  : "text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-transparent"
              )}
            >
              {f.label}
            </button>
          ))}
        </div>

        <div className="flex gap-1">
          {([
            { key: "symbol" as SortKey, label: "A-Z" },
            { key: "price" as SortKey, label: "Price" },
            { key: "change" as SortKey, label: "Change" },
          ]).map((s) => (
            <button
              key={s.key}
              onClick={() => toggleSort(s.key)}
              className={cn(
                "flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all",
                sortKey === s.key
                  ? "bg-purple-500/15 text-purple-500 border border-purple-500/25"
                  : "text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-transparent"
              )}
            >
              {s.label}
              {sortKey === s.key && (
                sortDir === "asc" ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Asset Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-12 text-[var(--text-muted)]">
          <div className="text-3xl mb-2">🔍</div>
          <p className="text-sm">No assets match your filters</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {filtered.map((asset) => (
            <MarketItem key={asset.symbol} asset={asset} />
          ))}
        </div>
      )}
    </div>
  );
}
