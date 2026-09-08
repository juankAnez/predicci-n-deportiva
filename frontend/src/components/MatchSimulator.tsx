import React, { useState, useEffect, useMemo } from "react";
import {
  SlidersHorizontal,
  Loader2,
  Users,
  UserCheck,
  UserX,
  ChevronDown,
  ChevronUp,
  Globe,
  Shield,
  Zap,
  Star,
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
      setError("Por favor selecciona dos clubes diferentes para la simulación.");
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

  const findTeamId = (nameQuery: string) => {
    if (!teams || !Array.isArray(teams)) return undefined;
    const t = teams.find((item) =>
      (item?.name || "").toLowerCase().includes(nameQuery.toLowerCase())
    );
    return t ? t.id : undefined;
  };

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
      <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="rounded-xl bg-blue-50 p-2 text-blue-600 border border-blue-100">
              <SlidersHorizontal className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-bold text-slate-900">
                Simulador Táctico & Calculadora de Valor (+EV)
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                Enfrenta dos clubes cualesquiera, gestiona bajas tácticas y obtén inferencia en tiempo real
              </p>
            </div>
          </div>

          {/* Quick Presets */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-semibold text-slate-400 mr-1">Partidos Clásicos:</span>
            <button
              type="button"
              onClick={() => {
                setSimLeague("PD");
                handleSetPreset("Real Madrid", "Barcelona", "2.15", "3.60", "3.20");
              }}
              className="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-all"
            >
              <Zap className="h-3 w-3 text-amber-500" />
              <span>Madrid vs Barça</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setSimLeague("PL");
                handleSetPreset("Arsenal", "Man City", "2.40", "3.40", "2.90");
              }}
              className="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-all"
            >
              <Zap className="h-3 w-3 text-blue-500" />
              <span>Arsenal vs City</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setSimLeague("PL");
                handleSetPreset("Liverpool", "Man City", "2.50", "3.50", "2.75");
              }}
              className="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-all"
            >
              <Zap className="h-3 w-3 text-indigo-500" />
              <span>Liverpool vs City</span>
            </button>
          </div>
        </div>

        {/* Simulation Form */}
        <form onSubmit={handleSimulate} className="mt-5 space-y-5">
          {/* League Filter Toggle */}
          <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-slate-50 p-2 border border-slate-200">
            <span className="text-xs font-bold text-slate-600 pl-1">
              Competición para los clubes:
            </span>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => setSimLeague("ALL")}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
                  simLeague === "ALL"
                    ? "bg-slate-900 text-white shadow-sm"
                    : "text-slate-600 hover:bg-slate-200/60"
                }`}
              >
                <Globe className="h-3 w-3" />
                <span>Todas ({teams.length})</span>
              </button>
              <button
                type="button"
                onClick={() => setSimLeague("PD")}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
                  simLeague === "PD"
                    ? "bg-slate-900 text-white shadow-sm"
                    : "text-slate-600 hover:bg-slate-200/60"
                }`}
              >
                <Shield className="h-3 w-3 text-amber-500" />
                <span>LaLiga (24)</span>
              </button>
              <button
                type="button"
                onClick={() => setSimLeague("PL")}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
                  simLeague === "PL"
                    ? "bg-slate-900 text-white shadow-sm"
                    : "text-slate-600 hover:bg-slate-200/60"
                }`}
              >
                <Shield className="h-3 w-3 text-blue-500" />
                <span>Premier League (24)</span>
              </button>
            </div>
          </div>

          {/* Team Selectors */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {/* Home Team */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-blue-900 uppercase tracking-wider">
                  Club Local
                </label>
                <span className="text-[11px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-200">
                  Rating: {homeAvgRating}
                </span>
              </div>
              <select
                value={homeTeamId}
                onChange={(e) => setHomeTeamId(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs sm:text-sm font-semibold text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              >
                {availableTeams.map((t) => (
                  <option key={t.id} value={t.id} disabled={t.id === awayTeamId}>
                    {t.name} ({t.country || "Club"})
                  </option>
                ))}
              </select>
            </div>

            {/* Away Team */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-indigo-900 uppercase tracking-wider">
                  Club Visitante
                </label>
                <span className="text-[11px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-200">
                  Rating: {awayAvgRating}
                </span>
              </div>
              <select
                value={awayTeamId}
                onChange={(e) => setAwayTeamId(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs sm:text-sm font-semibold text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              >
                {availableTeams.map((t) => (
                  <option key={t.id} value={t.id} disabled={t.id === homeTeamId}>
                    {t.name} ({t.country || "Club"})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Lineup & Player Absences Manager */}
          <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Alineaciones & Simulación de Bajas
                </h3>
                <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full border border-slate-200 font-medium">
                  Haz clic en un jugador para simular su ausencia
                </span>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-xs text-slate-600">
                  Diferencial:{" "}
                  <strong
                    className={
                      parseFloat(ratingDiff) > 0
                        ? "text-emerald-600"
                        : parseFloat(ratingDiff) < 0
                        ? "text-rose-600"
                        : "text-slate-700"
                    }
                  >
                    {parseFloat(ratingDiff) > 0 ? `+${ratingDiff}` : ratingDiff} pts
                  </strong>
                </div>
                <button
                  type="button"
                  onClick={() => setShowLineups(!showLineups)}
                  className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-900 font-medium"
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
              <div className="flex h-28 items-center justify-center gap-2 text-xs text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                <span>Cargando plantillas...</span>
              </div>
            ) : showLineups ? (
              <div className="mt-4 grid grid-cols-1 gap-5 lg:grid-cols-2">
                {/* Home Team Squad */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-900">
                      {homeTeamObj?.name} ({homeActive.length}/{homeSquad.length} disponibles)
                    </span>
                    {benchedHome.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setBenchedHome([])}
                        className="text-[11px] text-blue-600 hover:underline font-medium"
                      >
                        Restablecer todos
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-64 overflow-y-auto pr-1">
                    {homeSquad.map((p) => {
                      const isBenched = benchedHome.includes(p.id);
                      return (
                        <div
                          key={p.id}
                          onClick={() => toggleBenchHome(p.id)}
                          className={`cursor-pointer rounded-xl border p-2 transition-all text-xs select-none ${
                            isBenched
                              ? "border-rose-200 bg-rose-50/50 opacity-60 line-through text-slate-400"
                              : "border-slate-200 bg-slate-50 hover:border-blue-400 hover:bg-blue-50/30 text-slate-900"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <span
                                className={`rounded px-1 py-0.5 text-[9px] font-bold border ${getPosBadge(
                                  p.position
                                )}`}
                              >
                                {p.position}
                              </span>
                              <span className="font-semibold truncate max-w-[100px]">{p.name}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span className="font-bold text-slate-700 flex items-center gap-0.5">
                                <Star className="h-2.5 w-2.5 text-amber-500 fill-amber-500" />
                                {p.rating?.toFixed(1)}
                              </span>
                              {isBenched ? (
                                <UserX className="h-3 w-3 text-rose-600" />
                              ) : (
                                <UserCheck className="h-3 w-3 text-emerald-600" />
                              )}
                            </div>
                          </div>
                          <div className="mt-1 flex items-center justify-between text-[10px] text-slate-500">
                            <span>{formatMarketVal(p.market_value_eur)}</span>
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
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-900">
                      {awayTeamObj?.name} ({awayActive.length}/{awaySquad.length} disponibles)
                    </span>
                    {benchedAway.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setBenchedAway([])}
                        className="text-[11px] text-indigo-600 hover:underline font-medium"
                      >
                        Restablecer todos
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-64 overflow-y-auto pr-1">
                    {awaySquad.map((p) => {
                      const isBenched = benchedAway.includes(p.id);
                      return (
                        <div
                          key={p.id}
                          onClick={() => toggleBenchAway(p.id)}
                          className={`cursor-pointer rounded-xl border p-2 transition-all text-xs select-none ${
                            isBenched
                              ? "border-rose-200 bg-rose-50/50 opacity-60 line-through text-slate-400"
                              : "border-slate-200 bg-slate-50 hover:border-indigo-400 hover:bg-indigo-50/30 text-slate-900"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <span
                                className={`rounded px-1 py-0.5 text-[9px] font-bold border ${getPosBadge(
                                  p.position
                                )}`}
                              >
                                {p.position}
                              </span>
                              <span className="font-semibold truncate max-w-[100px]">{p.name}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span className="font-bold text-slate-700 flex items-center gap-0.5">
                                <Star className="h-2.5 w-2.5 text-amber-500 fill-amber-500" />
                                {p.rating?.toFixed(1)}
                              </span>
                              {isBenched ? (
                                <UserX className="h-3 w-3 text-rose-600" />
                              ) : (
                                <UserCheck className="h-3 w-3 text-emerald-600" />
                              )}
                            </div>
                          </div>
                          <div className="mt-1 flex items-center justify-between text-[10px] text-slate-500">
                            <span>{formatMarketVal(p.market_value_eur)}</span>
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
          <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
            <span className="text-xs font-bold text-slate-700 block mb-2.5">
              Cuotas de tu Casa de Apuestas:
            </span>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div>
                <label className="text-[11px] text-slate-600 block mb-1 font-semibold">
                  1 · Victoria Local
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  value={hOdds}
                  onChange={(e) => setHOdds(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-bold text-slate-900 focus:border-blue-500 focus:outline-none"
                  placeholder="Ej. 2.10"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-600 block mb-1 font-semibold">
                  X · Empate
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  value={dOdds}
                  onChange={(e) => setDOdds(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-bold text-slate-900 focus:border-blue-500 focus:outline-none"
                  placeholder="Ej. 3.30"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-600 block mb-1 font-semibold">
                  2 · Victoria Visitante
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  value={aOdds}
                  onChange={(e) => setAOdds(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-bold text-slate-900 focus:border-blue-500 focus:outline-none"
                  placeholder="Ej. 3.50"
                />
              </div>
            </div>
          </div>

          {error && (
            <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700 font-medium">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 text-sm font-bold text-white shadow-sm hover:bg-blue-700 transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Simulando enfrentamiento con Ensamble de IA...</span>
              </>
            ) : (
              <>
                <SlidersHorizontal className="h-4 w-4" />
                <span>Calcular Predicción & Análisis +EV</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Simulator Output */}
      {simResult && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">Resultado de la Simulación</h3>
            <span className="text-xs text-blue-700 font-semibold bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full">
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
