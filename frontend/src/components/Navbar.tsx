import React from "react";
import { Activity, Brain, Calculator, Trophy, BookOpen, WifiOff } from "lucide-react";

interface NavbarProps {
  activeTab: "matches" | "simulator" | "models" | "guide";
  setActiveTab: (tab: "matches" | "simulator" | "models" | "guide") => void;
  isBackendOnline: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, isBackendOnline }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-slate-950 shadow-lg shadow-emerald-500/20">
            <Brain className="h-6 w-6 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-tight text-white">
                Predicción<span className="text-emerald-400">Deportiva</span>
              </span>
              <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-300 uppercase tracking-wider">
                AI +EV
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Modelos Estadísticos & Análisis de Valor</p>
          </div>
        </div>

        <nav className="flex items-center gap-1 sm:gap-2">
          <button
            onClick={() => setActiveTab("matches")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-medium transition-all ${
              activeTab === "matches"
                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm"
                : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
            }`}
          >
            <Trophy className="h-4 w-4" />
            <span className="hidden md:inline">Partidos & Pronósticos</span>
            <span className="md:hidden">Partidos</span>
          </button>

          <button
            onClick={() => setActiveTab("simulator")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-medium transition-all ${
              activeTab === "simulator"
                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm"
                : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
            }`}
          >
            <Calculator className="h-4 w-4" />
            <span className="hidden md:inline">Simulador +EV</span>
            <span className="md:hidden">Simulador</span>
          </button>

          <button
            onClick={() => setActiveTab("models")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-medium transition-all ${
              activeTab === "models"
                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm"
                : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
            }`}
          >
            <Activity className="h-4 w-4" />
            <span className="hidden md:inline">Modelos ML</span>
            <span className="md:hidden">Modelos</span>
          </button>

          <button
            onClick={() => setActiveTab("guide")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-medium transition-all ${
              activeTab === "guide"
                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm"
                : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
            }`}
          >
            <BookOpen className="h-4 w-4" />
            <span className="hidden md:inline">Guía +EV</span>
            <span className="md:hidden">Guía</span>
          </button>
        </nav>

        <div className="flex items-center gap-2 pl-2">
          <div
            className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${
              isBackendOnline
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border-amber-500/30 bg-amber-500/10 text-amber-300"
            }`}
            title={isBackendOnline ? "Backend conectado" : "Conectando con Backend..."}
          >
            {isBackendOnline ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
                </span>
                <span className="hidden sm:inline">Backend Activo</span>
              </>
            ) : (
              <>
                <WifiOff className="h-3 w-3 animate-pulse" />
                <span className="hidden sm:inline">Conectando...</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
