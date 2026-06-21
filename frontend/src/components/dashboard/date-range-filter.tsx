import { useState } from "react";
import { Calendar } from "lucide-react";

interface DateRange {
  start: string;
  end: string;
}

interface DateRangeFilterProps {
  onChange: (range: DateRange) => void;
  initialRange?: DateRange;
}

export function DateRangeFilter({ onChange, initialRange }: DateRangeFilterProps) {
  const now = new Date();
  const fmt = (d: Date) => d.toISOString().slice(0, 16);

  const [start, setStart] = useState(initialRange?.start || fmt(new Date(now.getTime() - 24 * 60 * 60 * 1000)));
  const [end, setEnd] = useState(initialRange?.end || fmt(now));
  const [activePreset, setActivePreset] = useState<string | null>(null);

  const presets = [
    { label: "1H", hours: 1 },
    { label: "6H", hours: 6 },
    { label: "24H", hours: 24 },
    { label: "7D", hours: 168 },
    { label: "30D", hours: 720 },
  ];

  const applyPreset = (label: string, hours: number) => {
    const e = new Date();
    const s = new Date(e.getTime() - hours * 60 * 60 * 1000);
    setStart(fmt(s));
    setEnd(fmt(e));
    setActivePreset(label);
    onChange({ start: fmt(s), end: fmt(e) });
  };

  const applyCustom = () => {
    setActivePreset(null);
    onChange({ start, end });
  };

  return (
    <div className="flex items-center gap-3 flex-wrap">
      <div className="flex items-center gap-1.5 text-xs text-slate-400">
        <Calendar className="h-3.5 w-3.5" />
        <span>Range:</span>
      </div>

      <div className="flex gap-1.5">
        {presets.map((p) => (
          <button
            key={p.label}
            onClick={() => applyPreset(p.label, p.hours)}
            className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all ${
              activePreset === p.label
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                : "text-slate-400 hover:text-white bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.12]"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="h-4 w-px bg-white/[0.08]" />

      <input
        type="datetime-local"
        value={start}
        onChange={(e) => setStart(e.target.value)}
        className="px-2 py-1 rounded-lg bg-white/[0.05] border border-white/[0.1] text-xs text-white font-mono focus:outline-none focus:border-cyan-500/50 w-40"
      />
      <span className="text-xs text-slate-500">to</span>
      <input
        type="datetime-local"
        value={end}
        onChange={(e) => setEnd(e.target.value)}
        className="px-2 py-1 rounded-lg bg-white/[0.05] border border-white/[0.1] text-xs text-white font-mono focus:outline-none focus:border-cyan-500/50 w-40"
      />

      <button
        onClick={applyCustom}
        className="px-3 py-1 rounded-lg text-xs font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 transition-all"
      >
        Apply
      </button>
    </div>
  );
}
