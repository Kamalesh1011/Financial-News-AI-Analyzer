import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { KpiRow } from "./kpi-cards";
import { NewsFeed } from "./news-feed";
import { MarketPanel } from "./market-panel";
import { SentimentChart } from "./sentiment-chart";
import { ImpactView } from "./impact-view";
import { AlertHistory } from "./alert-history";
import { WatchlistManager } from "./watchlist-manager";
import { ComponentErrorBoundary } from "@/components/ui/ErrorBoundary";
import { ElegantShape } from "@/components/ui/shape-landing-hero";
import { NeuralNetworkMap } from "./neural-map";
import Chatbot from "./chatbot";
import { HealthDashboard } from "./health-dashboard";
import { PriceCharts } from "./price-charts";
import { SentimentTrend } from "./sentiment-trend";
import { PortfolioRisk } from "./portfolio-risk";
import { CorrelationHeatmap } from "./correlation-heatmap";
import { Backtester } from "./backtester";
import { SourceCredibility } from "./source-credibility";
import { SentimentPriceCorrelation } from "./sentiment-price-correlation";
import { PdfExport } from "./pdf-export";
import { ThemeToggle } from "./theme-toggle";
import { SentimentHeatmap } from "./sentiment-heatmap";
import { WatchlistPerformance } from "./watchlist-performance";
import { MultiTimeframeSentiment } from "./multi-timeframe-sentiment";
import { ConfidenceDistribution } from "./confidence-distribution";
import { VolumePriceCorrelation } from "./volume-price-correlation";
import { PriceAlertForm } from "./price-alerts";
import { DateRangeFilter } from "./date-range-filter";
import { Menu, X } from "lucide-react";
import {
  fetchNews,
  fetchMarketData,
  fetchSentimentDistribution,
  fetchImpactAnalyses,
  fetchAlerts,
  fetchWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  type NewsArticle,
  type MarketData,
  type SentimentDistribution,
  type ImpactAnalysis,
  type Alert,
  type WatchlistItem,
} from "@/lib/api";

type Tab =
  | "news"
  | "market"
  | "impact"
  | "alerts"
  | "watchlist"
  | "health"
  | "charts"
  | "analysis"
  | "tools"
  | "sentiment-deep";

interface TabDef {
  id: Tab;
  label: string;
  icon: string;
  group: string;
}

const tabs: TabDef[] = [
  { id: "news", label: "News Feed", icon: "📰", group: "Data" },
  { id: "market", label: "Market Data", icon: "💰", group: "Data" },
  { id: "impact", label: "Impact Analysis", icon: "🎯", group: "Data" },
  { id: "alerts", label: "Alerts", icon: "🔔", group: "Monitor" },
  { id: "watchlist", label: "Watchlist", icon: "📋", group: "Monitor" },
  { id: "health", label: "System Health", icon: "🩺", group: "Monitor" },
  { id: "charts", label: "Price Charts", icon: "📈", group: "Analytics" },
  { id: "analysis", label: "Analysis", icon: "🔬", group: "Analytics" },
  { id: "sentiment-deep", label: "Sentiment Deep", icon: "🧠", group: "Analytics" },
  { id: "tools", label: "Tools", icon: "🛠️", group: "Analytics" },
];

const groups = ["Data", "Monitor", "Analytics"];

export function Dashboard() {
  const [activeTab, setActiveTab] = useState<Tab>("news");
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);

  const [news, setNews] = useState<NewsArticle[]>([]);
  const [market, setMarket] = useState<MarketData[]>([]);
  const [sentiment, setSentiment] = useState<SentimentDistribution[]>([]);
  const [impacts, setImpacts] = useState<ImpactAnalysis[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>(() => ({
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
    end: new Date().toISOString().slice(0, 16),
  }));

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      const startDate = new Date(dateRange.start).getTime();
      const endDate = new Date(dateRange.end).getTime();
      const hours = Math.max(1, Math.round((endDate - startDate) / (1000 * 60 * 60)));
      const [newsData, marketData, sentimentData, impactData, alertData, watchlistData] =
        await Promise.all([
          fetchNews(hours, 50),
          fetchMarketData(),
          fetchSentimentDistribution(hours),
          fetchImpactAnalyses(hours, 20),
          fetchAlerts(hours, 30),
          fetchWatchlist(),
        ]);
      setNews(newsData);
      setMarket(marketData);
      setSentiment(sentimentData);
      setImpacts(impactData);
      setAlerts(alertData);
      setWatchlist(watchlistData);
      setLoading(false);
    };
    loadData();
  }, [dateRange]);

  const bullishPct = (() => {
    const total = sentiment.reduce((sum, s) => sum + s.count, 0);
    const bullish = sentiment.find((s) => s.sentiment === "bullish")?.count || 0;
    return total > 0 ? (bullish / total) * 100 : 50;
  })();

  const highImpact = impacts.filter((i) => i.risk_level === "high").length;

  const handleAddWatchlist = async (symbol: string, assetType: string) => {
    await addToWatchlist(symbol, assetType);
    setWatchlist([...watchlist, { symbol, asset_type: assetType }]);
  };

  const handleRemoveWatchlist = async (symbol: string) => {
    await removeFromWatchlist(symbol);
    setWatchlist(watchlist.filter((w) => w.symbol !== symbol));
  };

  const handleTabClick = (id: Tab) => {
    setActiveTab(id);
    setMobileOpen(false);
  };

  const sidebarWidth = sidebarOpen ? "w-60" : "w-[68px]";

  const renderTabContent = () => {
    switch (activeTab) {
      case "news":
        return <ComponentErrorBoundary name="News Feed"><NewsFeed articles={news} /></ComponentErrorBoundary>;
      case "market":
        return <ComponentErrorBoundary name="Market Data"><MarketPanel data={market} /></ComponentErrorBoundary>;
      case "impact":
        return (
          <ComponentErrorBoundary name="Impact Analysis">
            <div className="space-y-6">
              <NeuralNetworkMap impacts={impacts} />
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1">
                  <SentimentChart data={sentiment} />
                </div>
                <div className="lg:col-span-2">
                  <ImpactView impacts={impacts} />
                </div>
              </div>
            </div>
          </ComponentErrorBoundary>
        );
      case "alerts":
        return (
          <ComponentErrorBoundary name="Alerts">
            <div className="space-y-6">
              <AlertHistory alerts={alerts} />
              <PriceAlertForm />
            </div>
          </ComponentErrorBoundary>
        );
      case "watchlist":
        return (
          <ComponentErrorBoundary name="Watchlist">
            <div className="space-y-6">
              <WatchlistManager
                watchlist={watchlist}
                onAdd={handleAddWatchlist}
                onRemove={handleRemoveWatchlist}
              />
              <WatchlistPerformance />
            </div>
          </ComponentErrorBoundary>
        );
      case "health":
        return <ComponentErrorBoundary name="System Health"><HealthDashboard /></ComponentErrorBoundary>;
      case "charts":
        return <ComponentErrorBoundary name="Price Charts"><PriceCharts /></ComponentErrorBoundary>;
      case "analysis":
        return (
          <ComponentErrorBoundary name="Analysis">
            <div className="space-y-6">
              <SentimentTrend />
              <SentimentPriceCorrelation />
              <VolumePriceCorrelation />
              <SourceCredibility />
            </div>
          </ComponentErrorBoundary>
        );
      case "sentiment-deep":
        return (
          <ComponentErrorBoundary name="Sentiment Deep">
            <div className="space-y-6">
              <SentimentHeatmap />
              <MultiTimeframeSentiment />
              <ConfidenceDistribution />
            </div>
          </ComponentErrorBoundary>
        );
      case "tools":
        return (
          <ComponentErrorBoundary name="Tools">
            <div className="space-y-6">
              <PortfolioRisk />
              <Backtester />
              <CorrelationHeatmap />
            </div>
          </ComponentErrorBoundary>
        );
      default:
        return null;
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-[var(--bg-primary)] text-[var(--text-primary)]">
      {/* Background particles */}
      <div className="godmode-particles" />

      {/* Background shapes */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/[0.03] via-transparent to-purple-500/[0.03] blur-3xl" />
        <div className="glow-blob glow-blob-cyan" style={{ top: "10%", left: "5%" }} />
        <div className="glow-blob glow-blob-purple" style={{ top: "60%", right: "10%" }} />
        <div className="glow-blob glow-blob-rose" style={{ bottom: "10%", left: "30%" }} />
        <ElegantShape delay={0.2} width={600} height={140} rotate={12} gradient="from-cyan-500/[0.06]" className="left-[-10%] md:left-[-5%] top-[15%] md:top-[10%]" />
        <ElegantShape delay={0.4} width={500} height={120} rotate={-15} gradient="from-purple-500/[0.06]" className="right-[-5%] md:right-[0%] top-[40%] md:top-[30%]" />
        <ElegantShape delay={0.6} width={300} height={80} rotate={20} gradient="from-rose-500/[0.05]" className="left-[10%] bottom-[5%]" />
      </div>

      {/* Header */}
      <header className="header-bar border-b border-[var(--border-subtle)] backdrop-blur-2xl sticky top-0 z-50 relative shrink-0">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/[0.03] via-transparent to-purple-500/[0.03]" />
        <div className="px-4 sm:px-6 py-3 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button onClick={() => setMobileOpen(!mobileOpen)} className="lg:hidden p-2 rounded-lg hover:bg-[var(--bg-elevated)] transition-all">
                {mobileOpen ? <X className="h-5 w-5 text-[var(--text-secondary)]" /> : <Menu className="h-5 w-5 text-[var(--text-secondary)]" />}
              </button>
              <button onClick={() => setSidebarOpen(!sidebarOpen)} className="hidden lg:flex p-2 rounded-lg hover:bg-[var(--bg-elevated)] transition-all" title={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}>
                <Menu className="h-4 w-4 text-[var(--text-secondary)]" />
              </button>
              <div className="relative">
                <div className="text-2xl header-icon">📊</div>
                <div className="absolute -inset-2 bg-cyan-500/20 rounded-full blur-xl animate-pulse" />
              </div>
              <div>
                <h1 className="text-lg font-bold tracking-tight">
                  <span className="bg-clip-text text-transparent bg-gradient-to-r from-[var(--text-primary)] via-cyan-400 to-cyan-300">
                    NEURAL ENGINE
                  </span>
                </h1>
                <p className="text-[10px] text-[var(--text-muted)] hidden sm:block">
                  AI-powered sentiment analysis • Real-time market data • Smart alerts
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <PdfExport news={news} sentimentData={sentiment} impacts={impacts} alerts={alerts} marketData={market} />
              <ThemeToggle />
              <div className="text-right hidden md:block">
                <div className="text-xs text-[var(--text-muted)] font-mono">
                  {new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })} • {new Date().toLocaleTimeString()}
                </div>
              </div>
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-[10px] text-emerald-400 font-medium tracking-wider uppercase font-mono">Live</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Body: Sidebar + Content */}
      <div className="flex flex-1 overflow-hidden relative z-10">
        {/* Mobile overlay */}
        {mobileOpen && (
          <div className="fixed inset-0 bg-black/60 z-30 lg:hidden" onClick={() => setMobileOpen(false)} />
        )}

        {/* Sidebar */}
        <aside className={cn(
          "shrink-0 sidebar-panel backdrop-blur-xl border-r border-[var(--border-subtle)] overflow-y-auto overflow-x-hidden transition-all duration-300 z-40",
          sidebarWidth,
          "fixed lg:relative inset-y-0 left-0 h-full",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}>
          <div className="py-4 px-2">
            {groups.map((group) => (
              <div key={group} className="mb-4">
                <div className={cn("px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-[var(--text-muted)]", !sidebarOpen && "text-center")}>
                  {sidebarOpen ? group : "•"}
                </div>
                {tabs.filter((t) => t.group === group).map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => handleTabClick(tab.id)}
                    className={cn(
                      "w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 mb-0.5",
                      activeTab === tab.id
                        ? "sidebar-active-item"
                        : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-elevated)]",
                      !sidebarOpen && "justify-center px-2"
                    )}
                    title={tab.label}
                  >
                    <span className="text-base shrink-0">{tab.icon}</span>
                    {sidebarOpen && <span className="truncate">{tab.label}</span>}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-4 sm:p-6 space-y-5">
            {loading && (
              <div className="flex items-center justify-center py-12">
                <div className="flex items-center gap-3 text-[var(--text-secondary)]">
                  <div className="w-5 h-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm">Loading data...</span>
                </div>
              </div>
            )}

            {/* KPI Cards - always visible */}
            <KpiRow
              newsCount={news.length}
              bullishPct={bullishPct}
              highImpact={highImpact}
              alertsSent={alerts.length}
            />

            {/* Date Range Filter */}
            <DateRangeFilter onChange={(range) => setDateRange(range)} initialRange={dateRange} />

            {/* Tab Content */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.15 }}
              >
                {renderTabContent()}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>

      {/* Chatbot */}
      <Chatbot />
    </div>
  );
}
