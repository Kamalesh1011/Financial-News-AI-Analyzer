import { Component, type ReactNode, type ErrorInfo } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center p-8">
          <div className="glass-card rounded-2xl p-8 max-w-md w-full text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center">
              <span className="text-3xl">⚠️</span>
            </div>
            <h2 className="text-xl font-bold text-[var(--text-primary)] mb-2">Something went wrong</h2>
            <p className="text-sm text-[var(--text-secondary)] mb-6">
              {this.state.error?.message || "An unexpected error occurred"}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-[var(--text-primary)] text-sm font-medium border border-cyan-500/30 hover:border-cyan-500/60 transition-all"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export function ComponentErrorBoundary({ children, name }: { children: ReactNode; name: string }) {
  return (
    <ErrorBoundary
      fallback={
        <div className="glass-card rounded-2xl p-6 text-center">
          <div className="text-2xl mb-2">⚠️</div>
          <p className="text-sm text-[var(--text-secondary)]">Failed to load {name}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-3 px-4 py-1.5 rounded-lg text-xs bg-cyan-500/10 text-cyan-500 border border-cyan-500/20 hover:bg-cyan-500/20 transition-all"
          >
            Reload
          </button>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
}
