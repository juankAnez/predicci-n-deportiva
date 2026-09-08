import React from "react";
import { Activity, SlidersHorizontal, Trophy, BookOpen, CheckCircle2, AlertCircle } from "lucide-react";

interface NavbarProps {
  activeTab: "matches" | "simulator" | "models" | "guide";
  setActiveTab: (tab: "matches" | "simulator" | "models" | "guide") => void;
  isBackendOnline: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, isBackendOnline }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-[#050b17]/95 backdrop-blur-md transition-colors">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        {/* Brand identity with user's new logo */}
        <div className="flex items-center gap-3">
          <img
            src="/logo_ev_vector.svg"
            alt="SportPredict AI"
            className="h-10 w-10 rounded-xl object-contain border border-slate-700/60 bg-[#030A16] shadow-md shadow-teal-500/10"
          />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-tight text-white">
                SportPredict <span className="text-teal-400 font-black">AI</span>
              </span>
              <span className="rounded-md bg-teal-500/10 px-2 py-0.5 text-[10px] font-bold text-teal-300 border border-teal-500/30">
                PRO +EV
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Predicciones de Fútbol & Inteligencia Cuantitativa
            </p>
          </div>
        </div>

        {/* Minimal Dark Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-1.5 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab("matches")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === "matches"
                ? "bg-slate-800 text-teal-300 shadow-sm border border-teal-500/30 font-bold"
                : "text-slate-400 hover:text-white hover:bg-slate-800/50"
            }`}
          >
            <Trophy className="h-4 w-4 text-teal-400" />
            <span className="hidden md:inline">Partidos & Pronósticos</span>
            <span className="md:hidden">Partidos</span>
          </button>

          <button
            onClick={() => setActiveTab("simulator")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === "simulator"
                ? "bg-slate-800 text-teal-300 shadow-sm border border-teal-500/30 font-bold"
                : "text-slate-400 hover:text-white hover:bg-slate-800/50"
            }`}
          >
            <SlidersHorizontal className="h-4 w-4 text-cyan-400" />
            <span className="hidden md:inline">Simulador Táctico</span>
            <span className="md:hidden">Simulador</span>
          </button>

          <button
            onClick={() => setActiveTab("models")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === "models"
                ? "bg-slate-800 text-teal-300 shadow-sm border border-teal-500/30 font-bold"
                : "text-slate-400 hover:text-white hover:bg-slate-800/50"
            }`}
          >
            <Activity className="h-4 w-4 text-emerald-400" />
            <span className="hidden md:inline">Modelos de IA</span>
            <span className="md:hidden">Modelos</span>
          </button>

          <button
            onClick={() => setActiveTab("guide")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === "guide"
                ? "bg-slate-800 text-teal-300 shadow-sm border border-teal-500/30 font-bold"
                : "text-slate-400 hover:text-white hover:bg-slate-800/50"
            }`}
          >
            <BookOpen className="h-4 w-4 text-amber-400" />
            <span className="hidden md:inline">Metodología</span>
            <span className="md:hidden">Guía</span>
          </button>
        </nav>

        {/* Backend Online status indicator */}
        <div className="flex items-center gap-2 pl-2">
          <div
            className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${
              isBackendOnline
                ? "border-teal-500/30 bg-teal-500/10 text-teal-300"
                : "border-amber-500/30 bg-amber-500/10 text-amber-300"
            }`}
          >
            {isBackendOnline ? (
              <>
                <CheckCircle2 className="h-3.5 w-3.5 text-teal-400" />
                <span className="hidden sm:inline">Backend Activo</span>
              </>
            ) : (
              <>
                <AlertCircle className="h-3.5 w-3.5 text-amber-400 animate-pulse" />
                <span className="hidden sm:inline">Conectando...</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
