import { useState } from "react";
import { motion } from "framer-motion";
import { Brain, Cpu, Sparkles, TrendingUp, TrendingDown, HelpCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  sentiment?: "bullish" | "bearish" | "neutral";
  confidence?: number;
  reasoning?: string;
  newsTitle?: string;
}

interface NeuralMapProps {
  impacts: Array<{
    affected_assets?: Array<{
      symbol: string;
      direction: "bullish" | "bearish" | "neutral";
      confidence?: number;
    }>;
    news_title?: string;
    reasoning?: string;
    risk_level?: string;
  }>;
}

export function NeuralNetworkMap({ impacts }: NeuralMapProps) {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  // Default asset nodes to show if there's no dynamic impact data yet
  const defaultNodes: Node[] = [
    { id: "BTC", label: "BTC", x: 25, y: 25, sentiment: "bullish", confidence: 0.82, newsTitle: "Institutional demand drives Bitcoin surge", reasoning: "Strong spot ETF inflows and whale accumulation indicate continued bullish continuation." },
    { id: "AAPL", label: "AAPL", x: 75, y: 25, sentiment: "neutral", confidence: 0.55, newsTitle: "Apple announces new AI initiatives", reasoning: "Market awaits concrete feature rollouts. Neutral sentiment in short term." },
    { id: "NVDA", label: "NVDA", x: 15, y: 70, sentiment: "bullish", confidence: 0.94, newsTitle: "Next-gen Blackwell chips see supply deficit", reasoning: "Demand far outstrips supply, guaranteeing massive revenue growth for upcoming quarters." },
    { id: "TSLA", label: "TSLA", x: 85, y: 70, sentiment: "bearish", confidence: 0.71, newsTitle: "Tesla faces regulatory headwinds in Europe", reasoning: "New tariff discussions and supply chain issues are putting pressure on delivery margins." },
    { id: "ETH", label: "ETH", x: 45, y: 85, sentiment: "bullish", confidence: 0.68, newsTitle: "Ethereum gas fees hit multi-year lows", reasoning: "L2 scaling success shifts transaction volume, long-term bullish for ecosystem utility." },
    { id: "SPY", label: "SPY", x: 50, y: 15, sentiment: "bullish", confidence: 0.65, newsTitle: "Macro outlook remains stable post CPI data", reasoning: "Cooling inflation expectations support broader market indices." },
  ];

  // Map dynamic impacts to nodes if available
  const nodes: Node[] = impacts.length > 0 
    ? impacts.slice(0, 7).reduce((acc: Node[], impact, index) => {
        const affected = impact.affected_assets?.[0];
        if (affected) {
          const positions = [
            { x: 20, y: 25 },
            { x: 80, y: 25 },
            { x: 15, y: 70 },
            { x: 85, y: 70 },
            { x: 45, y: 85 },
            { x: 50, y: 15 },
            { x: 75, y: 85 }
          ];
          const pos = positions[index % positions.length];
          acc.push({
            id: affected.symbol,
            label: affected.symbol,
            x: pos.x,
            y: pos.y,
            sentiment: affected.direction,
            confidence: affected.confidence,
            newsTitle: impact.news_title,
            reasoning: impact.reasoning
          });
        }
        return acc;
      }, [])
    : defaultNodes;

  const getSentimentStyles = (sentiment?: string) => {
    switch (sentiment) {
      case "bullish":
        return {
          bg: "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
          glow: "rgba(16, 185, 129, 0.4)",
          stroke: "#10b981"
        };
      case "bearish":
        return {
          bg: "bg-red-500/10 border-red-500/30 text-red-400",
          glow: "rgba(239, 68, 68, 0.4)",
          stroke: "#ef4444"
        };
      default:
        return {
          bg: "bg-slate-500/10 border-slate-500/30 text-slate-300",
          glow: "rgba(148, 163, 184, 0.4)",
          stroke: "#94a3b8"
        };
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
      {/* Node Map Panel */}
      <div className="lg:col-span-2 glass-card rounded-2xl p-6 relative min-h-[400px] overflow-hidden flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Cpu className="h-5 w-5 text-cyan-400 animate-pulse" />
            <h3 className="text-lg font-bold text-white tracking-tight">Neural Asset Correlation Map</h3>
          </div>
          <p className="text-xs text-slate-400">Click any asset node to visualize sentiment propagation paths.</p>
        </div>

        {/* SVG Connection Lines */}
        <div className="absolute inset-0 z-0">
          <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            {nodes.map((node) => {
              const styles = getSentimentStyles(node.sentiment);
              const isSelected = selectedNode?.id === node.id;
              return (
                <g key={`link-${node.id}`}>
                  {/* Connection Line */}
                  <motion.line
                    x1="50"
                    y1="50"
                    x2={node.x}
                    y2={node.y}
                    stroke={styles.stroke}
                    strokeWidth={isSelected ? 1.5 : 0.8}
                    opacity={isSelected ? 0.7 : 0.25}
                    className="node-line"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 1.5 }}
                  />
                  {/* Glowing Flow Particle */}
                  <motion.circle
                    r={isSelected ? 0.8 : 0.5}
                    fill={styles.stroke}
                    initial={{ offset: 0 }}
                    animate={{
                      cx: [50, node.x],
                      cy: [50, node.y],
                    }}
                    transition={{
                      duration: 4,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                    style={{ filter: `drop-shadow(0 0 4px ${styles.stroke})` }}
                  />
                </g>
              );
            })}
          </svg>
        </div>

        {/* Interactive Nodes Layer */}
        <div className="absolute inset-0 z-10 pointer-events-none">
          {/* Central AI Node */}
          <div
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-auto"
            style={{ zIndex: 30 }}
          >
            <motion.div
              animate={{
                scale: [1, 1.05, 1],
                boxShadow: [
                  "0 0 20px rgba(6,182,212,0.25)",
                  "0 0 35px rgba(168,85,247,0.35)",
                  "0 0 20px rgba(6,182,212,0.25)",
                ],
              }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="w-16 h-16 rounded-full glass-card border-cyan-500/50 flex items-center justify-center cursor-pointer"
              onClick={() => setSelectedNode(null)}
            >
              <Brain className="h-7 w-7 text-cyan-400" />
            </motion.div>
          </div>

          {/* Outer Asset Nodes */}
          {nodes.map((node) => {
            const styles = getSentimentStyles(node.sentiment);
            const isSelected = selectedNode?.id === node.id;
            return (
              <div
                key={node.id}
                className="absolute pointer-events-auto cursor-pointer"
                style={{
                  left: `${node.x}%`,
                  top: `${node.y}%`,
                  transform: "translate(-50%, -50%)",
                }}
                onClick={() => setSelectedNode(node)}
              >
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  animate={{
                    borderColor: isSelected ? styles.stroke : "rgba(255,255,255,0.08)",
                    boxShadow: isSelected ? `0 0 15px ${styles.glow}` : "none",
                  }}
                  className={cn(
                    "px-3 py-1.5 rounded-full border text-xs font-bold font-mono tracking-wider transition-all",
                    styles.bg
                  )}
                >
                  {node.label}
                </motion.div>
              </div>
            );
          })}
        </div>

        <div className="z-10 text-[10px] text-slate-500 font-mono mt-4">
          Status: ACTIVE • Flow rate: 450ms/node
        </div>
      </div>

      {/* Details Display Panel */}
      <div className="glass-card rounded-2xl p-6 flex flex-col justify-between min-h-[300px]">
        {selectedNode ? (
          <div className="space-y-4 flex-1 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🎯</span>
                  <div>
                    <h4 className="font-bold text-white font-mono">{selectedNode.label} Analysis</h4>
                    <p className="text-[10px] text-slate-500 font-mono">NODE PROPAGATION DETECTED</p>
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  {selectedNode.sentiment === "bullish" ? (
                    <TrendingUp className="h-4 w-4 text-emerald-400" />
                  ) : selectedNode.sentiment === "bearish" ? (
                    <TrendingDown className="h-4 w-4 text-red-400" />
                  ) : (
                    <HelpCircle className="h-4 w-4 text-slate-400" />
                  )}
                  <span
                    className={cn(
                      "text-xs font-bold uppercase",
                      selectedNode.sentiment === "bullish" && "text-emerald-400",
                      selectedNode.sentiment === "bearish" && "text-red-400",
                      selectedNode.sentiment === "neutral" && "text-slate-400"
                    )}
                  >
                    {selectedNode.sentiment}
                  </span>
                </div>
              </div>

              <div>
                <span className="text-[10px] text-cyan-400 font-mono block mb-1">CORRELATED HEADLINE</span>
                <p className="text-sm font-semibold text-white leading-snug">{selectedNode.newsTitle}</p>
              </div>

              <div>
                <span className="text-[10px] text-purple-400 font-mono block mb-1">AI PROJECTION LOGIC</span>
                <p className="text-xs text-slate-400 leading-relaxed">{selectedNode.reasoning}</p>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-white/[0.08] flex items-center justify-between">
              <span className="text-[10px] text-slate-500 font-mono">CONFIDENCE COEFFICIENT</span>
              <span className="text-xs font-mono font-bold text-cyan-400">
                {(selectedNode.confidence || 0.5) * 100}%
              </span>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center text-center flex-1 py-8">
            <div className="w-16 h-16 rounded-full bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-4 animate-bounce">
              <Sparkles className="h-7 w-7 text-cyan-400" />
            </div>
            <h4 className="text-sm font-bold text-white mb-2">Neural Node Analysis</h4>
            <p className="text-xs text-slate-400 max-w-xs leading-relaxed">
              Select an asset node (such as <span className="text-emerald-400 font-mono">BTC</span> or <span className="text-cyan-400 font-mono">NVDA</span>) in the correlation grid to view the dynamic AI news-to-asset mapping logic.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
