import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Star } from "lucide-react";
import { fetchApi } from "@/lib/api";

interface Source {
  source: string;
  article_count: number;
  avg_confidence: number;
  credibility_score: number;
}

export function SourceCredibility() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchApi<{ sources: Source[] }>("/api/sources/credibility");
        setSources(data.sources || []);
      } catch {
        setSources([]);
      }
      setLoading(false);
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-5 h-5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <Star className="h-5 w-5 text-cyan-400" />
        <h3 className="text-lg font-bold text-white">News Source Credibility</h3>
      </div>

      {sources.length === 0 ? (
        <p className="text-sm text-slate-400 text-center py-10">No source data available</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/[0.08]">
                <th className="text-left text-[10px] text-slate-400 font-mono uppercase pb-3">#</th>
                <th className="text-left text-[10px] text-slate-400 font-mono uppercase pb-3">Source</th>
                <th className="text-right text-[10px] text-slate-400 font-mono uppercase pb-3">Articles</th>
                <th className="text-right text-[10px] text-slate-400 font-mono uppercase pb-3">Avg Confidence</th>
                <th className="text-right text-[10px] text-slate-400 font-mono uppercase pb-3">Credibility</th>
              </tr>
            </thead>
            <tbody>
              {sources.map((s, i) => (
                <motion.tr
                  key={s.source}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors"
                >
                  <td className="py-3 text-xs text-slate-500 font-mono">{i + 1}</td>
                  <td className="py-3 text-sm text-white font-mono font-medium">{s.source}</td>
                  <td className="py-3 text-sm text-slate-300 font-mono text-right">{s.article_count}</td>
                  <td className="py-3 text-sm text-slate-300 font-mono text-right">
                    {(s.avg_confidence * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 text-right">
                    <div className="inline-flex items-center gap-2">
                      <div className="w-16 h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all"
                          style={{
                            width: `${s.credibility_score * 100}%`,
                            background: s.credibility_score > 0.7
                              ? "#22c55e"
                              : s.credibility_score > 0.4
                              ? "#eab308"
                              : "#ef4444",
                          }}
                        />
                      </div>
                      <span className="text-xs font-mono text-slate-300 w-10 text-right">
                        {(s.credibility_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
