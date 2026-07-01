import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Search, X } from "lucide-react";
import type { NewsArticle } from "@/lib/api";

interface NewsFeedProps {
  articles: NewsArticle[];
}

function SentimentBadge({ sentiment, confidence }: { sentiment: string; confidence: number }) {
  const styles = {
    bullish: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    bearish: "bg-red-500/10 text-red-400 border-red-500/20",
    neutral: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  };
  const icons = { bullish: "📈", bearish: "📉", neutral: "➡️" };
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${styles[sentiment as keyof typeof styles] || styles.neutral}`}>
      {icons[sentiment as keyof typeof icons] || "➡️"} {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
      {confidence > 0 && ` (${(confidence * 100).toFixed(0)}%)`}
    </span>
  );
}

function AssetChip({ symbol }: { symbol: string }) {
  return (
    <span className="inline-flex items-center px-2 py-1 rounded-md bg-white/[0.05] border border-white/[0.08] text-xs text-slate-300 font-medium">
      {symbol}
    </span>
  );
}

export function NewsFeed({ articles }: NewsFeedProps) {
  const [search, setSearch] = useState("");
  const filtered = useMemo(() => {
    if (!search.trim()) return articles;
    const q = search.toLowerCase();
    return articles.filter(
      (a) =>
        a.title.toLowerCase().includes(q) ||
        a.summary?.toLowerCase().includes(q) ||
        a.source.toLowerCase().includes(q) ||
        a.tickers?.some((t) => t.toLowerCase().includes(q))
    );
  }, [search, articles]);

  if (!articles.length) {
    return (
      <div className="text-center py-16">
        <div className="text-4xl mb-4">📰</div>
        <h3 className="text-lg font-semibold text-white mb-2">No news articles yet</h3>
        <p className="text-slate-400">The News Collector agent will fetch news automatically.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">📰 News Feed</h2>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search news..."
              className="pl-9 pr-8 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white text-sm focus:outline-none focus:border-cyan-500/50 w-48 transition-all"
            />
            {search && (
              <button onClick={() => setSearch("")} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white">
                <X className="h-3 w-3" />
              </button>
            )}
          </div>
          <span className="text-xs text-slate-500">{filtered.length} articles</span>
        </div>
      </div>

      <div className="space-y-4">
        {filtered.slice(0, 20).map((article, i) => {
          const sentiment = article.sentiment?.sentiment || "neutral";
          const confidence = article.sentiment?.confidence || 0;
          return (
            <motion.div
              key={article.id || i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className={`relative rounded-xl p-5 glass-card transition-all duration-300 ${
                sentiment === "bullish" ? "border-l-2 border-l-emerald-500 hover:border-emerald-400/50 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)]" :
                sentiment === "bearish" ? "border-l-2 border-l-red-500 hover:border-red-400/50 hover:shadow-[0_0_20px_rgba(239,68,68,0.15)]" :
                "border-l-2 border-l-amber-500 hover:border-amber-400/50 hover:shadow-[0_0_20px_rgba(245,158,11,0.15)]"
              }`}
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <a href={article.url} target="_blank" rel="noopener noreferrer" className="text-base font-semibold text-white hover:text-blue-400 transition-colors leading-snug">
                  {article.title}
                </a>
                <SentimentBadge sentiment={sentiment} confidence={confidence} />
              </div>
              <div className="text-xs text-slate-500 mb-3">
                {article.source_name || article.source} • {new Date(article.published_at).toLocaleDateString()}
              </div>
              {article.summary && (
                <p className="text-sm text-slate-400 mb-4 line-clamp-2 leading-relaxed">{article.summary.slice(0, 200)}...</p>
              )}
              <div className="flex items-center gap-2 flex-wrap">
                {article.tickers?.slice(0, 4).map((ticker) => <AssetChip key={ticker} symbol={ticker} />)}
                <a href={article.url} target="_blank" rel="noopener noreferrer" className="ml-auto text-xs text-blue-400 hover:text-blue-300 transition-colors">
                  Read More →
                </a>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
