import React, { useState } from "react";
import { Calculator, Sparkles, Loader2 } from "lucide-react";
import type { Team, PredictionResult } from "../types/api";
import { PredictionDetail } from "./PredictionDetail";

interface MatchSimulatorProps {
  teams: Team[];
  onSimulate: (
    homeTeamId: number,
    awayTeamId: number,
    odds?: { h_odds?: number; d_odds?: number; a_odds?: number }
  ) => Promise<PredictionResult>;
}

export const MatchSimulator: React.FC<MatchSimulatorProps> = ({ teams, onSimulate }) => {
  const [simLeague, setSimLeague] = useState<"ALL" | "PD" | "PL">("ALL");

  const availableTeams = React.useMemo(() => {
    if (simLeague === "PD") {
      return teams.filter((t) => t.country === "Spain" || t.league_code === "PD" || (t.id <= 24 && !t.country));
    }
    if (simLeague === "PL") {
      return teams.filter((t) => t.country === "England" || t.league_code === "PL" || (t.id > 24 && !t.country));
    }
    return teams;
  }, [teams, simLeague]);

  const [homeTeamId, setHomeTeamId] = useState<number>(availableTeams[0]?.id || 1);
  const [awayTeamId, setAwayTeamId] = useState<number>(availableTeams[1]?.id || 2);
  const [hOdds, setHOdds] = useState<string>("2.10");
  const [dOdds, setDOdds] = useState<string>("3.30");
  const [aOdds, setAOdds] = useState<string>("3.50");
  const [simResult, setSimResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (homeTeamId === awayTeamId) {
      setError("Por favor selecciona dos equipos diferentes para el enfrentamiento.");
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const h = parseFloat(hOdds);
      const d = parseFloat(dOdds);
      const a = parseFloat(aOdds);
      const odds = !isNaN(h) && !isNaN(d) && !isNaN(a) ? { h_odds: h, d_odds: d, a_odds: a } : undefined;
      const res = await onSimulate(homeTeamId, awayTeamId, odds);
      setSimResult(res);
    } catch (err: any) {
      setError(err.message || "Error al simular enfrentamiento");
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculateOdds = async (h: number, d: number, a: number) => {
    setHOdds(h.toString());
    setDOdds(d.toString());
    setAOdds(a.toString());
    setLoading(true);
    try {
      const res = await onSimulate(homeTeamId, awayTeamId, { h_odds: h, d_odds: d, a_odds: a });
      setSimResult(res);
    } catch (err: any) {
      setError(err.message || "Error al recalcular cuotas");
    } finally {
      setLoading(false);
    }
  };

  // Helper to find team IDs by name
  const findTeamId = (nameQuery: string) => {
    if (!teams || !Array.isArray(teams)) return undefined;
    const t = teams.find((item) => (item?.name || "").toLowerCase().includes(nameQuery.toLowerCase()));
    return t ? t.id : undefined;
  };

  // Quick preset buttons for popular match-ups
  const handleSetPreset = (hName: string, aName: string, hO: string, dO: string, aO: string) => {
    const hId = findTeamId(hName);
    const aId = findTeamId(aName);
    if (hId && aId) {
      setHomeTeamId(hId);
      setAwayTeamId(aId);
      setHOdds(hO);
      setDOdds(dO);
      setAOdds(aO);
    }
  };

  React.useEffect(() => {
    if (availableTeams && availableTeams.length >= 2) {
      if (!availableTeams.some((t) => t.id === homeTeamId)) {
        setHomeTeamId(availableTeams[0].id);
      }
      if (!availableTeams.some((t) => t.id === awayTeamId)) {
        setAwayTeamId(availableTeams[1].id);
      }
    }
  }, [availableTeams]);

  return (
    <div className="space-y-6">
      {/* Simulator Control Panel */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 sm:p-6 backdrop-blur-md">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="rounded-xl bg-emerald-500/20 p-2 text-emerald-400">
              <Calculator className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Simulador de Enfrentamiento & Calculadora +EV</h2>
              <p className="text-xs text-slate-400">
                Elige cualquier par de clubes e ingresa las cuotas ofrecidas por tu casa de apuestas
              </p>
            </div>
          </div>

          {/* Quick Presets */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs text-slate-500 mr-1">Clásicos:</span>
            <button
              type="button"
              onClick={() => {
                setSimLeague("PD");
                handleSetPreset("Real Madrid", "Barcelona", "2.15", "3.60", "3.20");
              }}
              className="rounded-lg border border-slate-800 bg-slate-800/50 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              🇪🇸 Madrid vs Barça
            </button>
            <button
              type="button"
              onClick={() => {
                setSimLeague("PL");
                handleSetPreset("Arsenal", "Man City", "2.40", "3.40", "2.90");
              }}
              className="rounded-lg border border-slate-800 bg-slate-800/50 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              🏴󠁧󠁢󠁥󠁮󠁧󠁿 Arsenal vs City
            </button>
            <button
              type="button"
              onClick={() => {
                setSimLeague("PL");
                handleSetPreset("Tottenham", "Arsenal", "2.90", "3.60", "2.35");
              }}
              className="rounded-lg border border-slate-800 bg-slate-800/50 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              🏴󠁧󠁢󠁥󠁮󠁧󠁿 Spurs vs Arsenal
            </button>
          </div>
        </div>

        {/* Simulation Form */}
        <form onSubmit={handleSimulate} className="mt-5 space-y-5">
          {/* League Filter Toggle for Simulator */}
          <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-slate-950/60 p-2 border border-slate-800/80">
            <span className="text-xs font-semibold text-slate-400 pl-1">
              Filtrar equipos por competición:
            </span>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => setSimLeague("ALL")}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
                  simLeague === "ALL"
                    ? "bg-emerald-500 text-slate-950 font-bold"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >
                Todas las Ligas ({teams.length})
              </button>
              <button
                type="button"
                onClick={() => setSimLeague("PD")}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
                  simLeague === "PD"
                    ? "bg-amber-500 text-slate-950 font-bold"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >
                🇪🇸 La Liga (24)
              </button>
              <button
                type="button"
                onClick={() => setSimLeague("PL")}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
                  simLeague === "PL"
                    ? "bg-sky-500 text-slate-950 font-bold"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >
                🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (24)
              </button>
            </div>
          </div>

          {/* Team Selectors */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {/* Home Team */}
            <div className="rounded-xl border border-slate-800/80 bg-slate-950/50 p-4">
              <label className="text-xs font-bold text-emerald-400 uppercase tracking-wider block mb-1.5">
                🏠 Equipo Local ({availableTeams.length} opciones)
              </label>
              <select
                value={homeTeamId}
                onChange={(e) => setHomeTeamId(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3.5 py-2.5 text-sm font-semibold text-white focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              >
                {availableTeams.map((t) => (
                  <option key={t.id} value={t.id} disabled={t.id === awayTeamId}>
                    {t.country === "England" ? "🏴󠁧󠁢󠁥󠁮󠁧󠁿 " : "🇪🇸 "}
                    {t.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Away Team */}
            <div className="rounded-xl border border-slate-800/80 bg-slate-950/50 p-4">
              <label className="text-xs font-bold text-indigo-400 uppercase tracking-wider block mb-1.5">
                ✈️ Equipo Visitante ({availableTeams.length} opciones)
              </label>
              <select
                value={awayTeamId}
                onChange={(e) => setAwayTeamId(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3.5 py-2.5 text-sm font-semibold text-white focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              >
                {availableTeams.map((t) => (
                  <option key={t.id} value={t.id} disabled={t.id === homeTeamId}>
                    {t.country === "England" ? "🏴󠁧󠁢󠁥󠁮󠁧󠁿 " : "🇪🇸 "}
                    {t.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Bookmaker Odds Inputs */}
          <div className="rounded-xl border border-slate-800/80 bg-slate-950/30 p-4">
            <span className="text-xs font-semibold text-slate-300 block mb-3">
              Cuotas de tu Casa de Apuestas (Decimal Odds):
            </span>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1 font-medium">1 - Victoria Local</label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  value={hOdds}
                  onChange={(e) => setHOdds(e.target.value)}
                  className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm font-semibold text-white focus:border-emerald-500 focus:outline-none"
                  placeholder="Ej. 2.10"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1 font-medium">X - Empate</label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  value={dOdds}
                  onChange={(e) => setDOdds(e.target.value)}
                  className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm font-semibold text-white focus:border-emerald-500 focus:outline-none"
                  placeholder="Ej. 3.30"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1 font-medium">2 - Victoria Visitante</label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  value={aOdds}
                  onChange={(e) => setAOdds(e.target.value)}
                  className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm font-semibold text-white focus:border-emerald-500 focus:outline-none"
                  placeholder="Ej. 3.50"
                />
              </div>
            </div>
          </div>

          {error && (
            <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 py-3 text-sm font-extrabold text-slate-950 shadow-lg shadow-emerald-500/25 transition-all hover:brightness-110 active:scale-[0.99] disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Simulando enfrentamiento con Ensamble AI...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span>Simular Enfrentamiento & Calcular Valor (+EV)</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Simulator Output: Renders full PredictionDetail if simulated */}
      {simResult && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white">Resultado de la Simulación</h3>
            <span className="text-xs text-emerald-400 font-semibold bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 rounded-full">
              Inferencia en Tiempo Real
            </span>
          </div>
          <PredictionDetail
            prediction={simResult}
            loading={loading}
            onRecalculateOdds={handleRecalculateOdds}
            initialOdds={{
              h: parseFloat(hOdds),
              d: parseFloat(dOdds),
              a: parseFloat(aOdds),
            }}
          />
        </div>
      )}
    </div>
  );
};
