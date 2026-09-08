import React from "react";
import { Activity, BrainCircuit, SlidersHorizontal, Trophy, BookOpen, CheckCircle2, AlertCircle } from "lucide-react";

interface NavbarProps {
  activeTab: "matches" | "simulator" | "models" | "guide";
  setActiveTab: (tab: "matches" | "simulator" | "models" | "guide") => void;
  isBackendOnline: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, isBackendOnline }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/95 backdrop-blur-md transition-colors">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        {/* Brand identity */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm shadow-blue-500/20">
            <BrainCircuit className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-tight text-slate-900">
                SportPredict <span className="text-blue-600 font-extrabold">AI</span>
              </span>
              <span className="rounded-md bg-blue-50 px-2 py-0.5 text-[10px] font-bold text-blue-700 border border-blue-200">
                PRO
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              Predicciones de Fútbol & Inteligencia Cuantitativa
            </p>
          </div>
        </div>

        {/* Minimal Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-1.5 bg-slate-100 p-1 rounded-xl border border-slate-200/80">
          <button
            onClick={() => setActiveTab("matches")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === "matches"
                ? "bg-white text-slate-900 shadow-sm border border-slate-200/60"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
            }`}
          >
            <Trophy className="h-4 w-4 text-blue-600" />
            <span className="hidden md:inline">Partidos & Pronósticos</span>
            <span className="md:hidden">Partidos</span>
          </button>

          <button
            onClick={() => setActiveTab("simulator")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === "simulator"
                ? "bg-white text-slate-900 shadow-sm border border-slate-200/60"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
            }`}
          >
            <SlidersHorizontal className="h-4 w-4 text-indigo-600" />
            <span className="hidden md:inline">Simulador Táctico</span>
            <span className="md:hidden">Simulador</span>
          </button>

          <button
            onClick={() => setActiveTab("models")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === "models"
                ? "bg-white text-slate-900 shadow-sm border border-slate-200/60"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
            }`}
          >
            <Activity className="h-4 w-4 text-emerald-600" />
            <span className="hidden md:inline">Modelos de IA</span>
            <span className="md:hidden">Modelos</span>
          </button>

          <button
            onClick={() => setActiveTab("guide")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === "guide"
                ? "bg-white text-slate-900 shadow-sm border border-slate-200/60"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
            }`}
          >
            <BookOpen className="h-4 w-4 text-amber-600" />
            <span className="hidden md:inline">Metodología</span>
            <span className="md:hidden">Guía</span>
          </button>
        </nav>

        {/* Backend Online status pill */}
        <div className="flex items-center gap-2 pl-2">
          <div
            className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${
              isBackendOnline
                ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                : "border-amber-200 bg-amber-50 text-amber-700"
            }`}
          >
            {isBackendOnline ? (
              <>
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                <span className="hidden sm:inline">Sistema Conectado</span>
              </>
            ) : (
              <>
                <AlertCircle className="h-3.5 w-3.5 text-amber-600 animate-pulse" />
                <span className="hidden sm:inline">Conectando...</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
