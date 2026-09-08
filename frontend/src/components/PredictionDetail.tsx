import React, { useState, useEffect } from "react";
import {
  TrendingUp,
  CheckCircle2,
  Sparkles,
  BarChart3,
  Flame,
  RotateCcw,
  Loader2,
  Layers,
  Users,
} from "lucide-react";
import type { PredictionResult } from "../types/api";

interface PredictionDetailProps {
  prediction: PredictionResult | null;
  loading: boolean;
  onRecalculateOdds: (hOdds: number, dOdds: number, aOdds: number) => void;
  initialOdds?: { h?: number; d?: number; a?: number };
}

const getPosBadge = (pos: string) => {
  switch (pos?.toUpperCase()) {
    case "GK":
      return "bg-amber-500/20 text-amber-300 border-amber-500/30";
    case "DF":
      return "bg-sky-500/20 text-sky-300 border-sky-500/30";
    case "MF":
      return "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
    case "FW":
      return "bg-rose-500/20 text-rose-300 border-rose-500/30";
    default:
      return "bg-slate-700/50 text-slate-300 border-slate-600";
  }
};

const formatMarketVal = (eur: number) => {
  if (!eur) return "—";
  if (eur >= 1_000_000) return `€${(eur / 1_000_000).toFixed(0)}M`;
  return `€${(eur / 1_000).toFixed(0)}K`;
};

export const PredictionDetail: React.FC<PredictionDetailProps> = ({
  prediction,
  loading,
  onRecalculateOdds,
  initialOdds,
}) => {
  const [hOdds, setHOdds] = useState<string>(initialOdds?.h?.toString() || "2.20");
  const [dOdds, setDOdds] = useState<string>(initialOdds?.d?.toString() || "3.40");
  const [aOdds, setAOdds] = useState<string>(initialOdds?.a?.toString() || "3.30");

  useEffect(() => {
    if (initialOdds) {
      if (initialOdds.h) setHOdds(initialOdds.h.toString());
      if (initialOdds.d) setDOdds(initialOdds.d.toString());
      if (initialOdds.a) setAOdds(initialOdds.a.toString());
    }
  }, [initialOdds]);

  const handleCalculate = (e: React.FormEvent) => {
    e.preventDefault();
    const h = parseFloat(hOdds);
    const d = parseFloat(dOdds);
    const a = parseFloat(aOdds);
    if (!isNaN(h) && !isNaN(d) && !isNaN(a) && h > 1 && d > 1 && a > 1) {
      onRecalculateOdds(h, d, a);
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/60 p-8 backdrop-blur-sm">
        <Loader2 className="h-10 w-10 animate-spin text-emerald-400" />
        <p className="mt-4 text-base font-medium text-white">Calculando inferencia con Ensamble de IA...</p>
        <p className="text-xs text-slate-400">Procesando árboles XGBoost, Poisson y 89 variables estadísticas</p>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="flex h-96 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 p-8 text-center backdrop-blur-sm">
        <Sparkles className="h-12 w-12 text-slate-600 mb-3" />
        <h3 className="text-base font-semibold text-white">Selecciona un partido para analizar</h3>
        <p className="mt-1 max-w-sm text-xs text-slate-400">
          Haz clic en cualquier partido de la lista o usa el Simulador +EV para obtener probabilidades reales y cálculo de valor de apuestas.
        </p>
      </div>
    );
  }

  const { result, goals, over_under, explanation, market_analysis, teams } = prediction;
  const bestBet = market_analysis?.best_bet;

  return (
    <div className="space-y-6">
      {/* Header Match Card */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-950 p-6 shadow-xl backdrop-blur-md">
        <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="relative flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Predicción Generada por Inteligencia Artificial</span>
            </div>
            <h2 className="mt-1 text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
              {teams.home} <span className="text-slate-500 text-xl font-normal">vs</span> {teams.away}
            </h2>
            <p className="mt-0.5 text-xs text-slate-400">
              Partido #{prediction.match_id > 0 ? prediction.match_id : "Simulación Libre"} | 5 Modelos en Consenso
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-right">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">
                Pronóstico Principal
              </span>
              <span className="text-lg font-black text-emerald-400">
                {result.predicted === "H"
                  ? `Victoria ${teams.home}`
                  : result.predicted === "A"
                  ? `Victoria ${teams.away}`
                  : "Empate"}
              </span>
              <span className="text-[11px] text-slate-400 block font-medium">
                Confianza: {result.confidence}%
              </span>
            </div>
          </div>
        </div>

        {/* 1X2 Probabilities Visualizer */}
        <div className="mt-6 space-y-3 border-t border-slate-800/80 pt-5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
            <span>Probabilidades 1X2 (Ensemble ML)</span>
            <span className="text-slate-500 font-normal">Suma calibrada al 100%</span>
          </div>

          {/* Combined Progress Bar */}
          <div className="flex h-5 w-full overflow-hidden rounded-xl border border-slate-800 bg-slate-950/60 p-0.5 shadow-inner">
            <div
              style={{ width: `${result.home_win.probability}%` }}
              className="group relative flex items-center justify-center bg-emerald-500 transition-all duration-500 rounded-l-lg hover:brightness-110"
              title={`Victoria Local: ${result.home_win.probability}%`}
            >
              {result.home_win.probability >= 15 && (
                <span className="text-[10px] font-extrabold text-slate-950 truncate px-1">
                  {result.home_win.probability}%
                </span>
              )}
            </div>
            <div
              style={{ width: `${result.draw.probability}%` }}
              className="group relative flex items-center justify-center bg-amber-400 transition-all duration-500 hover:brightness-110"
              title={`Empate: ${result.draw.probability}%`}
            >
              {result.draw.probability >= 15 && (
                <span className="text-[10px] font-extrabold text-slate-950 truncate px-1">
                  {result.draw.probability}%
                </span>
              )}
            </div>
            <div
              style={{ width: `${result.away_win.probability}%` }}
              className="group relative flex items-center justify-center bg-indigo-500 transition-all duration-500 rounded-r-lg hover:brightness-110"
              title={`Victoria Visitante: ${result.away_win.probability}%`}
            >
              {result.away_win.probability >= 15 && (
                <span className="text-[10px] font-extrabold text-white truncate px-1">
                  {result.away_win.probability}%
                </span>
              )}
            </div>
          </div>

          {/* 3 Outcome Cards */}
          <div className="grid grid-cols-3 gap-2 sm:gap-4 pt-1">
            <div
              className={`rounded-xl border p-3 text-center transition-all ${
                result.predicted === "H"
                  ? "border-emerald-500/60 bg-emerald-500/10 shadow-sm shadow-emerald-500/20"
                  : "border-slate-800/80 bg-slate-950/40"
              }`}
            >
              <span className="text-[11px] font-medium text-slate-400 block truncate">1 - {teams.home}</span>
              <span className="text-xl sm:text-2xl font-black text-emerald-400">{result.home_win.probability}%</span>
              {result.predicted === "H" && (
                <span className="mt-1 inline-block rounded-md bg-emerald-500/20 px-1.5 py-0.5 text-[9px] font-bold text-emerald-300">
                  Pronóstico ML
                </span>
              )}
            </div>

            <div
              className={`rounded-xl border p-3 text-center transition-all ${
                result.predicted === "D"
                  ? "border-amber-500/60 bg-amber-500/10 shadow-sm shadow-amber-500/20"
                  : "border-slate-800/80 bg-slate-950/40"
              }`}
            >
              <span className="text-[11px] font-medium text-slate-400 block">X - Empate</span>
              <span className="text-xl sm:text-2xl font-black text-amber-400">{result.draw.probability}%</span>
              {result.predicted === "D" && (
                <span className="mt-1 inline-block rounded-md bg-amber-500/20 px-1.5 py-0.5 text-[9px] font-bold text-amber-300">
                  Pronóstico ML
                </span>
              )}
            </div>

            <div
              className={`rounded-xl border p-3 text-center transition-all ${
                result.predicted === "A"
                  ? "border-indigo-500/60 bg-indigo-500/10 shadow-sm shadow-indigo-500/20"
                  : "border-slate-800/80 bg-slate-950/40"
              }`}
            >
              <span className="text-[11px] font-medium text-slate-400 block truncate">2 - {teams.away}</span>
              <span className="text-xl sm:text-2xl font-black text-indigo-400">{result.away_win.probability}%</span>
              {result.predicted === "A" && (
                <span className="mt-1 inline-block rounded-md bg-indigo-500/20 px-1.5 py-0.5 text-[9px] font-bold text-indigo-300">
                  Pronóstico ML
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Grid: Goals Poisson & Over/Under */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Goals Expected (Poisson Model) */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 backdrop-blur-sm">
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <Flame className="h-4 w-4 text-amber-400" />
            <span>Estimación de Goles (Modelo Poisson)</span>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-3">
            <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-3 text-center">
              <span className="text-[11px] text-slate-400 block truncate">xG {teams.home}</span>
              <span className="text-xl font-bold text-white">{goals.home_expected}</span>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-3 text-center">
              <span className="text-[11px] text-slate-400 block truncate">xG {teams.away}</span>
              <span className="text-xl font-bold text-white">{goals.away_expected}</span>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-3 text-center">
              <span className="text-[11px] text-slate-400 block">Total xG</span>
              <span className="text-xl font-bold text-amber-400">{goals.total_expected}</span>
            </div>
          </div>

          {/* Most Likely Score */}
          {goals.most_likely_score && (
            <div className="mt-4 flex items-center justify-between rounded-xl border border-amber-500/20 bg-amber-500/5 p-3">
              <div>
                <span className="text-xs font-semibold text-amber-300">Marcador Más Probable</span>
                <p className="text-[11px] text-slate-400">Distribución bivariada de Poisson</p>
              </div>
              <div className="text-right">
                <span className="text-xl font-black text-white">{goals.most_likely_score}</span>
                <span className="text-xs text-amber-400 font-medium block">
                  ({goals.most_likely_score_probability}%)
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Over / Under Probabilities */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 backdrop-blur-sm">
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <BarChart3 className="h-4 w-4 text-emerald-400" />
            <span>Mercados Over / Under</span>
          </div>

          <div className="mt-4 space-y-2.5">
            {Object.entries(over_under || {}).map(([market, prob]) => {
              const safeProb = typeof prob === "number" ? prob : parseFloat(String(prob)) || 0;
              const label = market.replace("over_", "Más de ").replace("_", " ") + " Goles";
              return (
                <div key={market} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-300 font-medium">{label}</span>
                    <span className="font-bold text-white">{safeProb}%</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
                    <div
                      style={{ width: `${Math.min(100, Math.max(0, safeProb))}%` }}
                      className="h-full rounded-full bg-gradient-to-r from-teal-500 to-emerald-400 transition-all duration-500"
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Betting Market & Expected Value (+EV) Section */}
      <div className="rounded-2xl border border-emerald-500/30 bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-emerald-950/20 p-5 sm:p-6 shadow-xl backdrop-blur-sm">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="rounded-xl bg-emerald-500/20 p-2 text-emerald-400">
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Análisis del Mercado & Valor Esperado (+EV)</h3>
              <p className="text-xs text-slate-400">
                Eliminación de margen de la casa y dimensionamiento óptimo de apuestas con Criterio de Kelly
              </p>
            </div>
          </div>

          {market_analysis && (
            <div className="flex items-center gap-2 self-start sm:self-auto rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-1 text-xs">
              <span className="text-slate-400">Margen de la Casa:</span>
              <span className="font-bold text-amber-400">{market_analysis.margin_percentage}%</span>
            </div>
          )}
        </div>

        {/* Odds Input Form */}
        <form onSubmit={handleCalculate} className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-4 sm:items-end">
          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Cuota Local ({teams.home})
            </label>
            <input
              type="number"
              step="0.01"
              min="1.01"
              value={hOdds}
              onChange={(e) => setHOdds(e.target.value)}
              className="w-full rounded-xl border border-slate-800 bg-slate-950/80 px-3.5 py-2 text-sm font-semibold text-white focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              placeholder="Ej. 2.20"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Cuota Empate (X)
            </label>
            <input
              type="number"
              step="0.01"
              min="1.01"
              value={dOdds}
              onChange={(e) => setDOdds(e.target.value)}
              className="w-full rounded-xl border border-slate-800 bg-slate-950/80 px-3.5 py-2 text-sm font-semibold text-white focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              placeholder="Ej. 3.40"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Cuota Visitante ({teams.away})
            </label>
            <input
              type="number"
              step="0.01"
              min="1.01"
              value={aOdds}
              onChange={(e) => setAOdds(e.target.value)}
              className="w-full rounded-xl border border-slate-800 bg-slate-950/80 px-3.5 py-2 text-sm font-semibold text-white focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              placeholder="Ej. 3.30"
            />
          </div>

          <div>
            <button
              type="submit"
              className="w-full flex items-center justify-center gap-1.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 px-4 py-2.5 text-xs font-bold text-slate-950 shadow-md shadow-emerald-500/20 transition-all hover:brightness-110 active:scale-95"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Recalcular +EV</span>
            </button>
          </div>
        </form>

        {/* Best Bet Recommendation Banner */}
        {bestBet && bestBet.has_value && (
          <div className="mt-5 rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                    Oportunidad de Apuesta con Valor Encontrada (+EV)
                  </span>
                  <p className="text-sm font-extrabold text-white">
                    Apostar a <span className="text-emerald-300">{bestBet.label}</span> (Cuota {bestBet.odds})
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-slate-950/60 px-3 py-1.5 text-right border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Rentabilidad Esperada</span>
                  <span className="text-sm font-black text-emerald-400">+{bestBet.ev_pct}% EV</span>
                </div>
                <div className="rounded-lg bg-slate-950/60 px-3 py-1.5 text-right border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Stake Sugerido (Kelly 1/4)</span>
                  <span className="text-sm font-black text-emerald-300">{bestBet.suggested_stake_bankroll_pct}%</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Market Opportunities Cards */}
        {market_analysis && Array.isArray(market_analysis.opportunities) && (
          <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
            {market_analysis.opportunities.map((opp) => {
              const isPositive = opp.has_value;
              return (
                <div
                  key={opp.outcome}
                  className={`rounded-xl border p-4 transition-all ${
                    isPositive
                      ? "border-emerald-500/60 bg-emerald-500/10 shadow-md shadow-emerald-500/10"
                      : "border-slate-800 bg-slate-950/50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{opp.label}</span>
                    <span className="rounded-md bg-slate-800/80 px-2 py-0.5 text-xs font-semibold text-slate-300">
                      Cuota: {opp.odds}
                    </span>
                  </div>

                  <div className="mt-3 space-y-1 text-xs">
                    <div className="flex justify-between text-slate-400">
                      <span>Probabilidad Modelo:</span>
                      <span className="font-semibold text-white">{opp.model_prob_pct}%</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Probabilidad Justa Casa:</span>
                      <span className="font-semibold text-slate-300">{opp.fair_prob_pct}%</span>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center justify-between border-t border-slate-800/80 pt-2.5">
                    <span className="text-[11px] text-slate-400">Valor Esperado (+EV):</span>
                    <span
                      className={`text-xs font-extrabold ${
                        isPositive ? "text-emerald-400" : "text-rose-400"
                      }`}
                    >
                      {opp.ev_pct > 0 ? `+${opp.ev_pct}%` : `${opp.ev_pct}%`}
                    </span>
                  </div>

                  {isPositive && (
                    <div className="mt-1 flex items-center justify-between text-[11px]">
                      <span className="text-slate-400">Stake Kelly 1/4:</span>
                      <span className="font-bold text-emerald-300">
                        {opp.suggested_stake_bankroll_pct}% del bankroll
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Squad Comparison & Star Players */}
      {prediction.squad_analysis && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-800/80 pb-3.5">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">
                Duelo de Plantillas & Figuras Clave
              </h3>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="text-slate-400">
                Diferencial de Calidad:{" "}
                <span
                  className={`font-mono font-bold ${
                    prediction.squad_analysis.rating_diff >= 0
                      ? "text-emerald-400"
                      : "text-rose-400"
                  }`}
                >
                  {prediction.squad_analysis.rating_diff >= 0
                    ? `+${prediction.squad_analysis.rating_diff}`
                    : prediction.squad_analysis.rating_diff} pts
                </span>
              </span>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-6 sm:grid-cols-2">
            {/* Home Squad */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-400">
                  {teams.home}
                </span>
                <span className="text-[11px] font-mono text-emerald-300 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
                  ⭐ Media: {prediction.squad_analysis.home_avg_rating.toFixed(2)}
                </span>
              </div>
              <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
                {prediction.squad_analysis.home_squad.slice(0, 7).map((p) => (
                  <div
                    key={p.id}
                    className="flex items-center justify-between rounded-xl border border-slate-800/80 bg-slate-950/40 p-2 text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded px-1 py-0.5 text-[9px] font-extrabold border ${getPosBadge(
                          p.position
                        )}`}
                      >
                        {p.position}
                      </span>
                      <span className="font-semibold text-white truncate max-w-[120px]">
                        {p.name}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px]">
                      <span className="text-slate-400">{formatMarketVal(p.market_value_eur)}</span>
                      <span className="font-mono font-bold text-amber-400">⭐ {p.rating.toFixed(1)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Away Squad */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-indigo-400">
                  {teams.away}
                </span>
                <span className="text-[11px] font-mono text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded-md border border-indigo-500/20">
                  ⭐ Media: {prediction.squad_analysis.away_avg_rating.toFixed(2)}
                </span>
              </div>
              <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
                {prediction.squad_analysis.away_squad.slice(0, 7).map((p) => (
                  <div
                    key={p.id}
                    className="flex items-center justify-between rounded-xl border border-slate-800/80 bg-slate-950/40 p-2 text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded px-1 py-0.5 text-[9px] font-extrabold border ${getPosBadge(
                          p.position
                        )}`}
                      >
                        {p.position}
                      </span>
                      <span className="font-semibold text-white truncate max-w-[120px]">
                        {p.name}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px]">
                      <span className="text-slate-400">{formatMarketVal(p.market_value_eur)}</span>
                      <span className="font-mono font-bold text-amber-400">⭐ {p.rating.toFixed(1)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feature Importance / Key Factors (Explainability) */}
      {explanation && explanation.top_features && explanation.top_features.length > 0 && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 backdrop-blur-sm">
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <Layers className="h-4 w-4 text-indigo-400" />
            <span>Factores Clave que Determinaron la Predicción (Explicabilidad de IA)</span>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
            {explanation.top_features.slice(0, 6).map((item: any, idx: number) => {
              const featureName: string = Array.isArray(item) ? String(item[0] || "") : String(item?.name || "");
              const impact: number = Array.isArray(item) ? Number(item[1] || 0) : Number(item?.importance || 0);

              const cleanName = featureName
                .replace("elo_rating_home", "Elo Rating Local")
                .replace("elo_rating_away", "Elo Rating Visitante")
                .replace("home_attack_strength", "Poder Ofensivo Local")
                .replace("away_defense_strength", "Defensa Visitante")
                .replace("attack_vs_defense", "Diferencial Ataque/Defensa")
                .replace("days_rest_home", "Descanso Local (días)")
                .replace("days_rest_away", "Descanso Visitante (días)");

              return (
                <div key={idx} className="flex items-center justify-between rounded-xl border border-slate-800/80 bg-slate-950/40 p-3 text-xs">
                  <span className="text-slate-300 font-medium truncate max-w-[180px]">
                    {cleanName || `Factor ${idx + 1}`}
                  </span>
                  <span className="font-mono font-bold text-emerald-400">{Math.round(impact)} pts</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
