import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/contexts/ThemeContext";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative p-2 rounded-lg bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.1] transition-all group"
      title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
    >
      {theme === "dark" ? (
        <Sun className="h-4 w-4 text-amber-400 group-hover:text-amber-300 transition-colors" />
      ) : (
        <Moon className="h-4 w-4 text-slate-400 group-hover:text-slate-300 transition-colors" />
      )}
    </button>
  );
}
