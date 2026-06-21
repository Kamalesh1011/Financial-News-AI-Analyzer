import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { KpiRow } from "@/components/dashboard/kpi-cards";

describe("KpiRow", () => {
  it("renders all KPI cards", () => {
    render(<KpiRow newsCount={42} bullishPct={65.5} highImpact={3} alertsSent={12} />);

    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("65.5%")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });
});
