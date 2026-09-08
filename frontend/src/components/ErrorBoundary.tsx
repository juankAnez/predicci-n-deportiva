import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-rose-500/30 bg-rose-500/5 p-8 text-center backdrop-blur-sm my-4">
          <div className="rounded-xl bg-rose-500/20 p-3 text-rose-400 mb-3">
            <AlertTriangle className="h-8 w-8" />
          </div>
          <h3 className="text-base font-bold text-white">
            {this.props.fallbackTitle || "Ocurrió un problema al cargar esta sección"}
          </h3>
          <p className="mt-1 max-w-md text-xs text-rose-300/80 font-mono">
            {this.state.error?.message || "Error desconocido en el renderizado"}
          </p>
          <button
            onClick={this.handleReset}
            className="mt-4 flex items-center gap-1.5 rounded-xl bg-slate-800 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-700 transition-all shadow-sm"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Reintentar</span>
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
