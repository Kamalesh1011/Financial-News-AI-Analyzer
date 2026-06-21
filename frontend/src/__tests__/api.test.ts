import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock fetch globally
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

beforeEach(() => {
  mockFetch.mockReset();
  localStorage.clear();
});

describe("fetchApi", async () => {
  const { fetchApi } = await import("@/lib/api");

  it("calls the correct URL", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: "test" }),
    });

    await fetchApi("/api/test");
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/test"),
      expect.objectContaining({
        headers: expect.objectContaining({
          "Content-Type": "application/json",
        }),
      })
    );
  });

  it("throws on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    await expect(fetchApi("/api/error")).rejects.toThrow("API error: 500");
  });

  it("includes auth token when present", async () => {
    localStorage.setItem("token", "test-jwt-token");
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: "test" }),
    });

    await fetchApi("/api/test");
    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer test-jwt-token",
        }),
      })
    );
  });
});

describe("fetchNews", async () => {
  const { fetchNews } = await import("@/lib/api");

  it("returns articles on success", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        articles: [{ id: "1", title: "Test News" }],
        count: 1,
      }),
    });

    const articles = await fetchNews();
    expect(articles).toHaveLength(1);
    expect(articles[0].title).toBe("Test News");
  });

  it("returns empty array on error", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    const articles = await fetchNews();
    expect(articles).toEqual([]);
  });
});

describe("fetchMarketData", async () => {
  const { fetchMarketData } = await import("@/lib/api");

  it("returns market data on success", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: [
          { symbol: "AAPL", price: 150, change_pct_24h: 2.5, source: "finnhub" },
          { symbol: "BTC", price: 45000, change_pct_24h: -1.2, source: "coingecko" },
        ],
        count: 2,
      }),
    });

    const data = await fetchMarketData();
    expect(data).toHaveLength(2);
    expect(data[0].asset_type).toBe("stock");
    expect(data[1].asset_type).toBe("crypto");
  });
});
