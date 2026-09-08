import React, { useState, useEffect, useMemo } from "react";
import {
  Calculator,
  Sparkles,
  Loader2,
  Users,
  UserCheck,
  UserX,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import type { Team, PredictionResult, Player } from "../types/api";
import { fetchTeamPlayers } from "../services/api";
import { PredictionDetail } from "./PredictionDetail";

interface MatchSimulatorProps {
  teams: Team[];
  onSimulate: (
    homeTeamId: number,
    awayTeamId: number,
    odds?: { h_odds?: number; d_odds?: number; a_odds?: number },
    benchedHome?: number[],
    benchedAway?: number[]
  ) => Promise<PredictionResult>;
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

export const MatchSimulator: React.FC<MatchSimulatorProps> = ({ teams, onSimulate }) => {
  const [simLeague, setSimLeague] = useState<"ALL" | "PD" | "PL">("ALL");

  const availableTeams = useMemo(() => {
    if (simLeague === "PD") {
      return teams.filter(
        (t) => t.country === "Spain" || t.league_code === "PD" || (t.id <= 24 && !t.country)
      );
    }
    if (simLeague === "PL") {
      return teams.filter(
        (t) => t.country === "England" || t.league_code === "PL" || (t.id > 24 && !t.country)
      );
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

  // Player Squad & Lineup states
  const [homeSquad, setHomeSquad] = useState<Player[]>([]);
  const [awaySquad, setAwaySquad] = useState<Player[]>([]);
  const [benchedHome, setBenchedHome] = useState<number[]>([]);
  const [benchedAway, setBenchedAway] = useState<number[]>([]);
  const [loadingSquads, setLoadingSquads] = useState<boolean>(false);
  const [showLineups, setShowLineups] = useState<boolean>(true);

  // Load squads whenever selected teams change
  useEffect(() => {
    let isMounted = true;
    const loadSquads = async () => {
      if (!homeTeamId || !awayTeamId) return;
      setLoadingSquads(true);
      try {
        const [hPlayers, aPlayers] = await Promise.all([
          fetchTeamPlayers(homeTeamId).catch(() => []),
          fetchTeamPlayers(awayTeamId).catch(() => []),
        ]);
        if (isMounted) {
          setHomeSquad(hPlayers);
          setAwaySquad(aPlayers);
          setBenchedHome([]);
          setBenchedAway([]);
        }
      } catch (e) {
        console.error("Error cargando plantillas:", e);
      } finally {
        if (isMounted) setLoadingSquads(false);
      }
    };
    loadSquads();
    return () => {
      isMounted = false;
    };
  }, [homeTeamId, awayTeamId]);

  // Compute live active average ratings
  const homeActive = homeSquad.filter((p) => !benchedHome.includes(p.id));
  const awayActive = awaySquad.filter((p) => !benchedAway.includes(p.id));

  const homeAvgRating =
    homeActive.length > 0
      ? (homeActive.reduce((acc, p) => acc + (p.rating || 7.0), 0) / homeActive.length).toFixed(2)
      : "0.00";

  const awayAvgRating =
    awayActive.length > 0
      ? (awayActive.reduce((acc, p) => acc + (p.rating || 7.0), 0) / awayActive.length).toFixed(2)
      : "0.00";

  const ratingDiff = (parseFloat(homeAvgRating) - parseFloat(awayAvgRating)).toFixed(2);

  const toggleBenchHome = (id: number) => {
    setBenchedHome((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const toggleBenchAway = (id: number) => {
    setBenchedAway((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleSimulate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
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
      const res = await onSimulate(homeTeamId, awayTeamId, odds, benchedHome, benchedAway);
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
      const res = await onSimulate(
        homeTeamId,
        awayTeamId,
        { h_odds: h, d_odds: d, a_odds: a },
        benchedHome,
        benchedAway
      );
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
    const t = teams.find((item) =>
      (item?.name || "").toLowerCase().includes(nameQuery.toLowerCase())
    );
    return t ? t.id : undefined;
  };

  // Quick preset buttons for popular match-ups
  const handleSetPreset = (
    hName: string,
    aName: string,
    hO: string,
    dO: string,
    aO: string
  ) => {
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

  useEffect(() => {
    if (availableTeams && availableTeams.length >= 2) {
      if (!availableTeams.some((t) => t.id === homeTeamId)) {
        setHomeTeamId(availableTeams[0].id);
      }
      if (!availableTeams.some((t) => t.id === awayTeamId)) {
        setAwayTeamId(availableTeams[1].id);
      }
    }
  }, [availableTeams]);

  const homeTeamObj = teams.find((t) => t.id === homeTeamId);
  const awayTeamObj = teams.find((t) => t.id === awayTeamId);

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
              <h2 className="text-lg font-bold text-white">
                Simulador Táctico, Plantillas & Calculadora +EV
              </h2>
              <p className="text-xs text-slate-400">
                Elige cualquier club, gestiona bajas o titulares y calcula el impacto real en las probabilidades
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
                handleSetPreset("Liverpool", "Man City", "2.50", "3.50", "2.75");
              }}
              className="rounded-lg border border-slate-800 bg-slate-800/50 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              🏴󠁧󠁢󠁥󠁮󠁧󠁿 Liverpool vs City
            </button>
          </div>
        </div>

        {/* Simulation Form */}
        <form onSubmit={handleSimulate} className="mt-5 space-y-5">
          {/* League Filter Toggle */}
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
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                  🏠 Equipo Local ({availableTeams.length} opciones)
                </label>
                <span className="text-[11px] font-mono text-emerald-300 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
                  Rating: ⭐ {homeAvgRating}
                </span>
              </div>
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
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                  ✈️ Equipo Visitante ({availableTeams.length} opciones)
                </label>
                <span className="text-[11px] font-mono text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded-md border border-indigo-500/20">
                  Rating: ⭐ {awayAvgRating}
                </span>
              </div>
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

          {/* Lineup & Player Absences Manager */}
          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 sm:p-5">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-white">
                  Alineaciones & Gestión de Bajas Tácticas
                </h3>
                <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full border border-slate-700">
                  Haz clic en un jugador para simular su baja o ausencia
                </span>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-xs text-slate-300">
                  Diferencial Rating:{" "}
                  <span
                    className={`font-bold font-mono ${
                      parseFloat(ratingDiff) > 0
                        ? "text-emerald-400"
                        : parseFloat(ratingDiff) < 0
                        ? "text-rose-400"
                        : "text-slate-300"
                    }`}
                  >
                    {parseFloat(ratingDiff) > 0 ? `+${ratingDiff}` : ratingDiff}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setShowLineups(!showLineups)}
                  className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors"
                >
                  {showLineups ? (
                    <>
                      <span>Plegar</span> <ChevronUp className="h-3.5 w-3.5" />
                    </>
                  ) : (
                    <>
                      <span>Desplegar</span> <ChevronDown className="h-3.5 w-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>

            {loadingSquads ? (
              <div className="flex h-32 items-center justify-center gap-2 text-xs text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin text-emerald-400" />
                <span>Cargando plantillas y puntuaciones...</span>
              </div>
            ) : showLineups ? (
              <div className="mt-4 grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Home Team Squad */}
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-emerald-400">
                      Plantilla {homeTeamObj?.name} ({homeActive.length}/{homeSquad.length} disponibles)
                    </span>
                    {benchedHome.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setBenchedHome([])}
                        className="text-[10px] text-slate-400 hover:text-emerald-400 underline"
                      >
                        Restablecer todos
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-72 overflow-y-auto pr-1">
                    {homeSquad.map((p) => {
                      const isBenched = benchedHome.includes(p.id);
                      return (
                        <div
                          key={p.id}
                          onClick={() => toggleBenchHome(p.id)}
                          className={`cursor-pointer rounded-xl border p-2.5 transition-all text-xs select-none ${
                            isBenched
                              ? "border-rose-900/40 bg-rose-950/20 opacity-50 line-through"
                              : "border-slate-800 bg-slate-900/80 hover:border-emerald-500/50 hover:bg-slate-800/80"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <span
                                className={`rounded px-1 py-0.5 text-[9px] font-extrabold border ${getPosBadge(
                                  p.position
                                )}`}
                              >
                                {p.position}
                              </span>
                              <span className="font-bold text-white truncate max-w-[100px]">
                                {p.name}
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span className="font-mono font-bold text-amber-400">
                                {p.rating?.toFixed(1)}
                              </span>
                              {isBenched ? (
                                <UserX className="h-3 w-3 text-rose-400" />
                              ) : (
                                <UserCheck className="h-3 w-3 text-emerald-400" />
                              )}
                            </div>
                          </div>
                          <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400">
                            <span>Val: {formatMarketVal(p.market_value_eur)}</span>
                            <span>
                              {p.goals}G · {p.assists}A
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Away Team Squad */}
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-400">
                      Plantilla {awayTeamObj?.name} ({awayActive.length}/{awaySquad.length} disponibles)
                    </span>
                    {benchedAway.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setBenchedAway([])}
                        className="text-[10px] text-slate-400 hover:text-indigo-400 underline"
                      >
                        Restablecer todos
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-72 overflow-y-auto pr-1">
                    {awaySquad.map((p) => {
                      const isBenched = benchedAway.includes(p.id);
                      return (
                        <div
                          key={p.id}
                          onClick={() => toggleBenchAway(p.id)}
                          className={`cursor-pointer rounded-xl border p-2.5 transition-all text-xs select-none ${
                            isBenched
                              ? "border-rose-900/40 bg-rose-950/20 opacity-50 line-through"
                              : "border-slate-800 bg-slate-900/80 hover:border-indigo-500/50 hover:bg-slate-800/80"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <span
                                className={`rounded px-1 py-0.5 text-[9px] font-extrabold border ${getPosBadge(
                                  p.position
                                )}`}
                              >
                                {p.position}
                              </span>
                              <span className="font-bold text-white truncate max-w-[100px]">
                                {p.name}
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span className="font-mono font-bold text-amber-400">
                                {p.rating?.toFixed(1)}
                              </span>
                              {isBenched ? (
                                <UserX className="h-3 w-3 text-rose-400" />
                              ) : (
                                <UserCheck className="h-3 w-3 text-emerald-400" />
                              )}
                            </div>
                          </div>
                          <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400">
                            <span>Val: {formatMarketVal(p.market_value_eur)}</span>
                            <span>
                              {p.goals}G · {p.assists}A
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : null}
          </div>

          {/* Bookmaker Odds Inputs */}
          <div className="rounded-xl border border-slate-800/80 bg-slate-950/30 p-4">
            <span className="text-xs font-semibold text-slate-300 block mb-3">
              Cuotas de tu Casa de Apuestas (Decimal Odds):
            </span>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1 font-medium">
                  1 - Victoria Local
                </label>
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
                <label className="text-[11px] text-slate-400 block mb-1 font-medium">
                  X - Empate
                </label>
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
                <label className="text-[11px] text-slate-400 block mb-1 font-medium">
                  2 - Victoria Visitante
                </label>
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
                <span>Simulando enfrentamiento con Ensamble AI & Alineaciones...</span>
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
