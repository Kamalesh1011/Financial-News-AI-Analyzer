import { useState } from "react";
import { Download } from "lucide-react";
import { showToast } from "@/components/ui/toast";

interface PdfExportProps {
  newsCount: number;
  sentimentData: Array<{ sentiment: string; count: number }>;
  impactCount: number;
  alertCount: number;
  marketData: Array<{ symbol: string; price: number; change_pct: number }>;
}

export function PdfExport({ newsCount, sentimentData, impactCount, alertCount, marketData }: PdfExportProps) {
  const [generating, setGenerating] = useState(false);

  const generate = async () => {
    setGenerating(true);
    try {
      const { jsPDF } = await import("jspdf");
      const doc = new jsPDF();

      // Title
      doc.setFontSize(20);
      doc.text("Neural Engine AI - Financial Report", 20, 20);
      doc.setFontSize(10);
      doc.setTextColor(100);
      doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 28);

      // KPI Summary
      doc.setFontSize(14);
      doc.setTextColor(0);
      doc.text("Key Metrics", 20, 45);
      doc.setFontSize(10);
      doc.text(`Total News Articles: ${newsCount}`, 20, 55);
      doc.text(`Impact Analyses: ${impactCount}`, 20, 63);
      doc.text(`Alerts Sent: ${alertCount}`, 20, 71);

      // Sentiment Distribution
      doc.setFontSize(14);
      doc.text("Sentiment Distribution", 20, 90);
      let y = 100;
      sentimentData.forEach((s) => {
        doc.setFontSize(10);
        doc.text(`${s.sentiment}: ${s.count}`, 20, y);
        y += 8;
      });

      // Market Overview
      doc.setFontSize(14);
      doc.text("Market Overview", 20, y + 10);
      y += 20;
      doc.setFontSize(8);
      doc.text("Symbol", 20, y);
      doc.text("Price", 80, y);
      doc.text("Change %", 130, y);
      y += 6;
      marketData.slice(0, 15).forEach((m) => {
        doc.text(m.symbol, 20, y);
        doc.text(`$${m.price.toFixed(2)}`, 80, y);
        doc.text(`${m.change_pct.toFixed(2)}%`, 130, y);
        y += 6;
      });

      doc.save("neural-engine-report.pdf");
      showToast("PDF report downloaded", "success");
    } catch {
      showToast("Failed to generate PDF", "error");
    }
    setGenerating(false);
  };

  return (
    <button
      onClick={generate}
      disabled={generating}
      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500/20 to-rose-500/20 text-white text-sm font-medium border border-purple-500/30 hover:border-purple-500/60 transition-all disabled:opacity-50"
    >
      <Download className="h-4 w-4" />
      {generating ? "Generating..." : "Export PDF"}
    </button>
  );
}
