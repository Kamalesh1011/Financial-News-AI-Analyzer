import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

// Mock fetch
vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
  ok: true,
  json: async () => ({ articles: [], data: [], distribution: {}, analyses: [], alerts: [], watchlist: [] }),
}));

// Mock react-hot-toast
vi.mock("react-hot-toast", () => ({
  default: { success: vi.fn(), error: vi.fn() },
}));

import { ErrorBoundary } from "@/components/ui/ErrorBoundary";

describe("ErrorBoundary", () => {
  it("renders children when no error", () => {
    render(
      <ErrorBoundary>
        <div>Test child</div>
      </ErrorBoundary>
    );
    expect(screen.getByText("Test child")).toBeInTheDocument();
  });

  it("renders error UI when child throws", () => {
    const ThrowingChild = () => {
      throw new Error("Test error");
    };

    render(
      <ErrorBoundary>
        <ThrowingChild />
      </ErrorBoundary>
    );

    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    expect(screen.getByText("Test error")).toBeInTheDocument();
    expect(screen.getByText("Reload Page")).toBeInTheDocument();
  });
});
