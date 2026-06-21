const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  source: string;
  url: string;
  published_at: string;
  tickers: string[];
  sentiment?: {
    sentiment: "bullish" | "bearish" | "neutral";
    confidence: number;
  };
}

export interface MarketData {
  symbol: string;
  price: number;
  change_pct: number;
  asset_type: "stock" | "crypto" | "forex";
}

export interface SentimentDistribution {
  sentiment: string;
  count: number;
}

export interface ImpactAnalysis {
  id: string;
  news_title: string;
  affected_assets: Array<{
    symbol: string;
    direction: "bullish" | "bearish" | "neutral";
  }>;
  impact_score: number;
  risk_level: "high" | "medium" | "low";
  reasoning: string;
}

export interface Alert {
  id: string;
  type: string;
  title: string;
  message: string;
  timestamp: string;
  assets: string[];
  channel: string;
}

export interface WatchlistItem {
  symbol: string;
  asset_type: string;
}

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

export async function fetchNews(hours = 24, limit = 30): Promise<NewsArticle[]> {
  try {
    const data = await fetchApi<{ articles: NewsArticle[] }>(
      `/api/news?hours=${hours}&limit=${limit}`
    );
    return data.articles || [];
  } catch {
    return [];
  }
}

export async function fetchMarketData(): Promise<MarketData[]> {
  try {
    const data = await fetchApi<{ data: Record<string, unknown>[] }>("/api/market");
    return (data.data || []).map((item) => {
      let asset_type: "stock" | "crypto" | "forex" = "stock";
      const symbol = (item.symbol as string) || "";
      if (item.source === "coingecko" || item.source === "binance" || ["BTC", "ETH", "SOL"].includes(symbol)) {
        asset_type = "crypto";
      } else if (symbol.endsWith("=X")) {
        asset_type = "forex";
      }

      const change_pct = item.change_pct_24h !== undefined && item.change_pct_24h !== null
        ? Number(item.change_pct_24h)
        : item.change_pct !== undefined && item.change_pct !== null
        ? Number(item.change_pct)
        : 0;

      return {
        ...item,
        symbol,
        price: Number(item.price) || 0,
        asset_type,
        change_pct,
      } as MarketData;
    });
  } catch {
    return [];
  }
}

export async function fetchSentimentDistribution(hours = 24): Promise<SentimentDistribution[]> {
  try {
    const data = await fetchApi<{ distribution: Record<string, number> }>(
      `/api/sentiment/distribution?hours=${hours}`
    );
    return Object.entries(data.distribution || {}).map(([sentiment, count]) => ({
      sentiment,
      count,
    }));
  } catch {
    return [];
  }
}

export async function fetchImpactAnalyses(hours = 24, limit = 20): Promise<ImpactAnalysis[]> {
  try {
    const data = await fetchApi<{ analyses: ImpactAnalysis[] }>(
      `/api/impact?hours=${hours}&limit=${limit}`
    );
    return data.analyses || [];
  } catch {
    return [];
  }
}

export async function fetchAlerts(hours = 24, limit = 30): Promise<Alert[]> {
  try {
    const data = await fetchApi<{ alerts: Alert[] }>(
      `/api/alerts?hours=${hours}&limit=${limit}`
    );
    return data.alerts || [];
  } catch {
    return [];
  }
}

export async function fetchWatchlist(): Promise<WatchlistItem[]> {
  try {
    const data = await fetchApi<{ watchlist: WatchlistItem[] }>("/api/watchlist");
    return data.watchlist || [];
  } catch {
    return [];
  }
}

export async function addToWatchlist(symbol: string, assetType: string): Promise<boolean> {
  try {
    await fetchApi("/api/watchlist", {
      method: "POST",
      body: JSON.stringify({ symbol, asset_type: assetType }),
    });
    return true;
  } catch {
    return false;
  }
}

export async function removeFromWatchlist(symbol: string): Promise<boolean> {
  try {
    await fetchApi(`/api/watchlist/${symbol}`, { method: "DELETE" });
    return true;
  } catch {
    return false;
  }
}

export async function sendChatMessage(message: string): Promise<string> {
  try {
    const data = await fetchApi<{ reply: string }>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    return data.reply;
  } catch {
    return "I'm currently in offline mode. Please try again later.";
  }
}

export async function fetchSentimentTrend(hours = 24, interval = 60): Promise<TrendPoint[]> {
  try {
    const data = await fetchApi<{ trend: TrendPoint[] }>(
      `/api/sentiment/trend?hours=${hours}&interval=${interval}`
    );
    return data.trend || [];
  } catch {
    return [];
  }
}

export async function fetchSourceCredibility(): Promise<SourceCredibility[]> {
  try {
    const data = await fetchApi<{ sources: SourceCredibility[] }>("/api/sources/credibility");
    return data.sources || [];
  } catch {
    return [];
  }
}

export async function fetchPortfolioRisk(
  holdings: Array<{ symbol: string; weight: number; asset_type: string }>
): Promise<PortfolioRiskResult> {
  return fetchApi<PortfolioRiskResult>("/api/portfolio/risk", {
    method: "POST",
    body: JSON.stringify({ holdings }),
  });
}

export async function fetchCorrelation(
  symbols: string[],
  hours = 72
): Promise<CorrelationResult> {
  return fetchApi<CorrelationResult>(
    `/api/correlation?symbols=${symbols.join(",")}&hours=${hours}`
  );
}

export async function fetchBacktest(params: {
  symbol: string;
  strategy: string;
  hours: number;
  initial_capital: number;
}): Promise<BacktestResult> {
  return fetchApi<BacktestResult>("/api/backtest", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function fetchHealthSystem(): Promise<SystemHealth> {
  return fetchApi<SystemHealth>("/api/health/system");
}

export async function login(username: string, password: string): Promise<{ token: string; user: { id: string; username: string } }> {
  return fetchApi("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function register(
  username: string,
  email: string,
  password: string
): Promise<{ token: string; user: { id: string; username: string } }> {
  return fetchApi("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

// Additional interfaces
interface TrendPoint {
  timestamp: string;
  bullish_count: number;
  bearish_count: number;
  neutral_count: number;
  avg_confidence: number;
}

interface SourceCredibility {
  source: string;
  article_count: number;
  avg_confidence: number;
  credibility_score: number;
}

interface PortfolioRiskResult {
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

interface CorrelationResult {
  symbols: string[];
  matrix: number[][];
}

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
  }>;
  timestamp: string;
}
