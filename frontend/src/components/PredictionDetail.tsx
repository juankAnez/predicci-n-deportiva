import React, { useState, useEffect } from "react";
import {
  TrendingUp,
  CheckCircle2,
  RotateCcw,
  Loader2,
  Layers,
  Users,
  Star,
  BrainCircuit,
  Target,
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
      return "bg-amber-50 text-amber-800 border-amber-200";
    case "DF":
      return "bg-sky-50 text-sky-800 border-sky-200";
    case "MF":
      return "bg-emerald-50 text-emerald-800 border-emerald-200";
    case "FW":
      return "bg-rose-50 text-rose-800 border-rose-200";
    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
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
      <div className="flex h-96 flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <p className="mt-3 text-sm font-bold text-slate-900">
          Procesando inferencia con Ensamble de IA...
        </p>
        <p className="text-xs text-slate-500">
          Evaluando 89 variables, ratings de plantillas y modelos de Poisson
        </p>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="flex h-96 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center shadow-sm">
        <div className="rounded-xl bg-blue-50 p-3 text-blue-600 mb-3">
          <BrainCircuit className="h-7 w-7" />
        </div>
        <h3 className="text-sm font-bold text-slate-900">Selecciona un partido para analizar</h3>
        <p className="mt-1 max-w-xs text-xs text-slate-500">
          Elige cualquier partido del listado o usa el Simulador Táctico para calcular probabilidades en tiempo real.
        </p>
      </div>
    );
  }

  const { result, goals, over_under, explanation, market_analysis, teams } = prediction;
  const bestBet = market_analysis?.best_bet;

  return (
    <div className="space-y-4">
      {/* Header Match Card */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-100 pb-3.5">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-blue-700">
              <BrainCircuit className="h-3.5 w-3.5 text-blue-600" />
              <span>Pronóstico Generado por Inteligencia Artificial</span>
            </div>
            <h2 className="mt-1 text-xl sm:text-2xl font-black text-slate-900">
              {teams.home} <span className="text-slate-400 font-normal text-lg">vs</span> {teams.away}
            </h2>
            <p className="text-xs text-slate-500 font-medium">
              Consenso de 5 Modelos Calibrados · Brier Score Optimizado
            </p>
          </div>

          <div className="rounded-xl border border-blue-200 bg-blue-50/70 px-4 py-2 text-right">
            <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 block">
              Pronóstico Principal
            </span>
            <span className="text-base font-black text-blue-950">
              {result.predicted === "H"
                ? `Victoria ${teams.home}`
                : result.predicted === "A"
                ? `Victoria ${teams.away}`
                : "Empate"}
            </span>
            <span className="text-xs text-blue-600 block font-semibold">
              Confianza: {result.confidence}%
            </span>
          </div>
        </div>

        {/* 1X2 Probabilities Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-slate-700">
            <span>Probabilidades 1X2 (Ensemble ML)</span>
            <span className="text-slate-500 font-normal">Suma calibrada al 100%</span>
          </div>

          {/* Progress Bar */}
          <div className="flex h-3.5 w-full overflow-hidden rounded-full bg-slate-100 p-0.5 border border-slate-200">
            <div
              style={{ width: `${result.home_win.probability}%` }}
              className="bg-blue-600 transition-all duration-500 rounded-l-full"
              title={`Victoria Local: ${result.home_win.probability}%`}
            />
            <div
              style={{ width: `${result.draw.probability}%` }}
              className="bg-amber-500 transition-all duration-500"
              title={`Empate: ${result.draw.probability}%`}
            />
            <div
              style={{ width: `${result.away_win.probability}%` }}
              className="bg-indigo-600 transition-all duration-500 rounded-r-full"
              title={`Victoria Visitante: ${result.away_win.probability}%`}
            />
          </div>

          {/* 3 Outcome Cards */}
          <div className="grid grid-cols-3 gap-2 pt-1">
            <div
              className={`rounded-xl border p-2.5 text-center transition-all ${
                result.predicted === "H"
                  ? "border-blue-500 bg-blue-50 text-blue-950 font-bold"
                  : "border-slate-200 bg-slate-50/70 text-slate-700"
              }`}
            >
              <span className="text-[11px] font-semibold text-slate-500 block">1 · {teams.home}</span>
              <span className="text-lg font-black text-slate-900">{result.home_win.probability}%</span>
            </div>

            <div
              className={`rounded-xl border p-2.5 text-center transition-all ${
                result.predicted === "D"
                  ? "border-amber-500 bg-amber-50 text-amber-950 font-bold"
                  : "border-slate-200 bg-slate-50/70 text-slate-700"
              }`}
            >
              <span className="text-[11px] font-semibold text-slate-500 block">X · Empate</span>
              <span className="text-lg font-black text-slate-900">{result.draw.probability}%</span>
            </div>

            <div
              className={`rounded-xl border p-2.5 text-center transition-all ${
                result.predicted === "A"
                  ? "border-indigo-500 bg-indigo-50 text-indigo-950 font-bold"
                  : "border-slate-200 bg-slate-50/70 text-slate-700"
              }`}
            >
              <span className="text-[11px] font-semibold text-slate-500 block">2 · {teams.away}</span>
              <span className="text-lg font-black text-slate-900">{result.away_win.probability}%</span>
            </div>
          </div>
        </div>

        {/* Goals Expected & Over/Under Line */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 border-t border-slate-100 pt-3.5">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
              <Target className="h-4 w-4 text-blue-600" />
              <span>Goles Esperados (Poisson)</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-xs text-slate-600">
              <span>{teams.home}: <strong className="text-slate-900">{goals.home_expected}</strong></span>
              <span>{teams.away}: <strong className="text-slate-900">{goals.away_expected}</strong></span>
              <span>Total: <strong className="text-slate-900">{goals.total_expected}</strong></span>
            </div>
            {goals.most_likely_score && (
              <div className="mt-2 text-[11px] font-semibold text-blue-700 bg-blue-50 border border-blue-200/60 rounded-md p-1.5 text-center">
                Marcador más probable: <strong>{goals.most_likely_score}</strong> ({goals.most_likely_score_probability}%)
              </div>
            )}
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
              <TrendingUp className="h-4 w-4 text-emerald-600" />
              <span>Probabilidades Over / Under</span>
            </div>
            <div className="mt-2 grid grid-cols-3 gap-1 text-center text-xs">
              <div className="rounded bg-white p-1 border border-slate-200">
                <span className="text-[10px] text-slate-500 block">+1.5 Goles</span>
                <strong className="text-slate-900">{over_under["over_1.5"] || 0}%</strong>
              </div>
              <div className="rounded bg-white p-1 border border-slate-200">
                <span className="text-[10px] text-slate-500 block">+2.5 Goles</span>
                <strong className="text-slate-900">{over_under["over_2.5"] || 0}%</strong>
              </div>
              <div className="rounded bg-white p-1 border border-slate-200">
                <span className="text-[10px] text-slate-500 block">+3.5 Goles</span>
                <strong className="text-slate-900">{over_under["over_3.5"] || 0}%</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Value Bet (+EV) Analysis & Odds Calculator */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-emerald-50 p-1.5 text-emerald-700 border border-emerald-200">
              <TrendingUp className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Calculadora de Valor Esperado (+EV) & Cuotas
              </h3>
              <p className="text-xs text-slate-500">
                Ingresa las cuotas de tu casa de apuestas para verificar si existe ventaja matemática
              </p>
            </div>
          </div>
        </div>

        {/* Odds Input Form */}
        <form onSubmit={handleCalculate} className="grid grid-cols-1 gap-2.5 sm:grid-cols-4 sm:items-end">
          <div>
            <label className="text-[11px] font-bold text-slate-600 block mb-1">
              Cuota 1 ({teams.home})
            </label>
            <input
              type="number"
              step="0.01"
              min="1.01"
              value={hOdds}
              onChange={(e) => setHOdds(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-bold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
            />
          </div>

          <div>
            <label className="text-[11px] font-bold text-slate-600 block mb-1">
              Cuota X (Empate)
            </label>
            <input
              type="number"
              step="0.01"
              min="1.01"
              value={dOdds}
              onChange={(e) => setDOdds(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-bold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
            />
          </div>

          <div>
            <label className="text-[11px] font-bold text-slate-600 block mb-1">
              Cuota 2 ({teams.away})
            </label>
            <input
              type="number"
              step="0.01"
              min="1.01"
              value={aOdds}
              onChange={(e) => setAOdds(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-bold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
            />
          </div>

          <div>
            <button
              type="submit"
              className="w-full flex items-center justify-center gap-1.5 rounded-lg bg-blue-600 px-3 py-2 text-xs font-bold text-white shadow-sm hover:bg-blue-700 transition-all"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Calcular +EV</span>
            </button>
          </div>
        </form>

        {/* Best Bet Recommendation Banner */}
        {bestBet && bestBet.has_value ? (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3.5">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
                <div>
                  <span className="text-xs font-bold text-emerald-900 block">
                    Oportunidad de Apuesta con Valor Detectada (+EV)
                  </span>
                  <p className="text-xs text-emerald-700 font-medium">
                    Apostar a <strong>{bestBet.label}</strong> a cuota <strong>{bestBet.odds}</strong> ofrece ventaja estadística frente al corredor.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="rounded-lg bg-emerald-600 px-2.5 py-1 text-xs font-black text-white">
                  +{bestBet.ev_pct}% EV
                </span>
                <span className="text-[11px] font-bold text-emerald-800 bg-white border border-emerald-200 px-2 py-1 rounded-lg">
                  Stake Kelly: {bestBet.suggested_stake_bankroll_pct}%
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
            No se detectó ventaja de valor (+EV) significativa en las cuotas actuales. El mercado está alineado con la predicción.
          </div>
        )}
      </div>

      {/* Squad Comparison & Star Players */}
      {prediction.squad_analysis && (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900">
                Duelo de Plantillas & Figuras Clave
              </h3>
            </div>
            <div className="text-xs font-semibold text-slate-600">
              Diferencial de Calidad:{" "}
              <strong
                className={
                  prediction.squad_analysis.rating_diff >= 0 ? "text-emerald-600" : "text-rose-600"
                }
              >
                {prediction.squad_analysis.rating_diff >= 0
                  ? `+${prediction.squad_analysis.rating_diff}`
                  : prediction.squad_analysis.rating_diff} pts
              </strong>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {/* Home Squad */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-900">{teams.home}</span>
                <span className="rounded-md bg-blue-50 border border-blue-200 px-2 py-0.5 text-[11px] font-bold text-blue-700">
                  Media: {prediction.squad_analysis.home_avg_rating.toFixed(2)}
                </span>
              </div>
              <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
                {prediction.squad_analysis.home_squad.slice(0, 6).map((p) => (
                  <div
                    key={p.id}
                    className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50/60 p-2 text-xs"
                  >
                    <div className="flex items-center gap-1.5">
                      <span className={`rounded px-1 py-0.5 text-[9px] font-bold border ${getPosBadge(p.position)}`}>
                        {p.position}
                      </span>
                      <span className="font-semibold text-slate-900 truncate max-w-[120px]">{p.name}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px]">
                      <span className="text-slate-500">{formatMarketVal(p.market_value_eur)}</span>
                      <span className="font-bold text-slate-900 flex items-center gap-0.5">
                        <Star className="h-3 w-3 text-amber-500 fill-amber-500" />
                        {p.rating.toFixed(1)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Away Squad */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-900">{teams.away}</span>
                <span className="rounded-md bg-indigo-50 border border-indigo-200 px-2 py-0.5 text-[11px] font-bold text-indigo-700">
                  Media: {prediction.squad_analysis.away_avg_rating.toFixed(2)}
                </span>
              </div>
              <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
                {prediction.squad_analysis.away_squad.slice(0, 6).map((p) => (
                  <div
                    key={p.id}
                    className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50/60 p-2 text-xs"
                  >
                    <div className="flex items-center gap-1.5">
                      <span className={`rounded px-1 py-0.5 text-[9px] font-bold border ${getPosBadge(p.position)}`}>
                        {p.position}
                      </span>
                      <span className="font-semibold text-slate-900 truncate max-w-[120px]">{p.name}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px]">
                      <span className="text-slate-500">{formatMarketVal(p.market_value_eur)}</span>
                      <span className="font-bold text-slate-900 flex items-center gap-0.5">
                        <Star className="h-3 w-3 text-amber-500 fill-amber-500" />
                        {p.rating.toFixed(1)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feature Importance (SHAP Explainability) */}
      {explanation && explanation.top_features && explanation.top_features.length > 0 && (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-900">
            <Layers className="h-4 w-4 text-indigo-600" />
            <span>Factores Clave Determinantes (Explicabilidad SHAP)</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
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
                <div
                  key={idx}
                  className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 p-2 text-xs"
                >
                  <span className="text-slate-700 font-medium truncate max-w-[160px]">
                    {cleanName || `Factor ${idx + 1}`}
                  </span>
                  <span className="font-bold text-blue-700 font-mono">+{Math.round(impact)} pts</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
