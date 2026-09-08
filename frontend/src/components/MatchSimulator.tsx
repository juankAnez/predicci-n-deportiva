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
  Trophy,
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
      return "bg-slate-800 text-slate-300 border-slate-700";
  }
};

const formatMarketVal = (eur: number) => {
  if (!eur) return "—";
  if (eur >= 1_000_000) return `€${(eur / 1_000_000).toFixed(0)}M`;
  return `€${(eur / 1_000).toFixed(0)}K`;
};

export type SimLeagueCode =
  | "ALL"
  | "PD"
  | "PL"
  | "SA"
  | "BL"
  | "L1"
  | "UCL"
  | "UEL"
  | "CDR"
  | "FAC"
  | "CI"
  | "DFB"
  | "CDF";

const UCL_IDS = new Set([14, 7, 18, 12, 44, 26, 28, 30, 49, 50, 51, 54, 57, 58, 59, 60, 62, 63, 64, 67]);
const UEL_IDS = new Set([15, 10, 19, 35, 41, 38, 53, 55, 56, 61, 65, 66, 68]);

export const MatchSimulator: React.FC<MatchSimulatorProps> = ({ teams, onSimulate }) => {
  const [simLeague, setSimLeague] = useState<SimLeagueCode>("PD");

  const getFilteredTeams = (code: SimLeagueCode, allTeams: Team[]) => {
    if (code === "PD" || code === "CDR") {
      return allTeams.filter((t) => t.country === "Spain");
    }
    if (code === "PL" || code === "FAC") {
      return allTeams.filter((t) => t.country === "England");
    }
    if (code === "SA" || code === "CI") {
      return allTeams.filter((t) => t.country === "Italy");
    }
    if (code === "BL" || code === "DFB") {
      return allTeams.filter((t) => t.country === "Germany");
    }
    if (code === "L1" || code === "CDF") {
      return allTeams.filter((t) => t.country === "France");
    }
    if (code === "UCL") {
      return allTeams.filter((t) => UCL_IDS.has(t.id) || t.is_ucl);
    }
    if (code === "UEL") {
      return allTeams.filter((t) => UEL_IDS.has(t.id) || t.is_uel);
    }
    return allTeams;
  };

  const availableTeams = useMemo(() => {
    return getFilteredTeams(simLeague, teams);
  }, [teams, simLeague]);

  const handleSelectSimLeague = (code: SimLeagueCode) => {
    setSimLeague(code);
    const filtered = getFilteredTeams(code, teams);
    if (filtered.length >= 2) {
      setHomeTeamId(filtered[0].id);
      setAwayTeamId(filtered[1].id);
      setSimResult(null);
    }
  };

  const [homeTeamId, setHomeTeamId] = useState<number>(14);
  const [awayTeamId, setAwayTeamId] = useState<number>(7);
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
    aO: string,
    leagueCode?: SimLeagueCode
  ) => {
    if (leagueCode) {
      setSimLeague(leagueCode);
    }
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
      if (!availableTeams.some((t) => t.id === awayTeamId) || homeTeamId === awayTeamId) {
        const nextAway = availableTeams.find((t) => t.id !== homeTeamId) || availableTeams[1];
        setAwayTeamId(nextAway.id);
      }
    }
  }, [availableTeams]);

  const homeTeamObj = teams.find((t) => t.id === homeTeamId);
  const awayTeamObj = teams.find((t) => t.id === awayTeamId);

  return (
    <div className="space-y-6">
      {/* Simulator Control Panel */}
      <div className="rounded-2xl border border-slate-800/80 bg-[#070e1c] p-5 sm:p-6 shadow-lg">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800/70 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="rounded-xl bg-teal-500/10 p-2 text-teal-400 border border-teal-500/20">
              <SlidersHorizontal className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-bold text-white">
                Simulador Táctico Europeo & Calculadora +EV
              </h2>
              <p className="text-xs text-slate-400 font-medium">
                Enfrenta clubes de las 5 Grandes Ligas, Champions y Copas, gestiona bajas y obtén inferencia en tiempo real
              </p>
            </div>
          </div>

          {/* Quick Presets */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-semibold text-slate-500 mr-1">Clásicos:</span>
            <button
              type="button"
              onClick={() => handleSetPreset("Real Madrid", "Barcelona", "2.15", "3.60", "3.20", "PD")}
              className="flex items-center gap-1 rounded-lg border border-slate-800 bg-[#091120] px-2.5 py-1 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              <Zap className="h-3 w-3 text-amber-400" />
              <span>Madrid vs Barça</span>
            </button>
            <button
              type="button"
              onClick={() => handleSetPreset("Arsenal", "Man City", "2.40", "3.40", "2.90", "PL")}
              className="flex items-center gap-1 rounded-lg border border-slate-800 bg-[#091120] px-2.5 py-1 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              <Zap className="h-3 w-3 text-cyan-400" />
              <span>Arsenal vs City</span>
            </button>
            <button
              type="button"
              onClick={() => handleSetPreset("Inter de Milan", "AC Milan", "2.10", "3.40", "3.50", "SA")}
              className="flex items-center gap-1 rounded-lg border border-slate-800 bg-[#091120] px-2.5 py-1 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              <Zap className="h-3 w-3 text-blue-400" />
              <span>Inter vs Milan</span>
            </button>
            <button
              type="button"
              onClick={() => handleSetPreset("Bayern Munich", "Dortmund", "1.75", "4.20", "4.50", "BL")}
              className="flex items-center gap-1 rounded-lg border border-slate-800 bg-[#091120] px-2.5 py-1 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              <Zap className="h-3 w-3 text-rose-400" />
              <span>Bayern vs BVB</span>
            </button>
            <button
              type="button"
              onClick={() => handleSetPreset("Paris", "Marsella", "1.50", "4.50", "6.20", "L1")}
              className="flex items-center gap-1 rounded-lg border border-slate-800 bg-[#091120] px-2.5 py-1 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              <Zap className="h-3 w-3 text-indigo-400" />
              <span>PSG vs OM</span>
            </button>
            <button
              type="button"
              onClick={() => handleSetPreset("Real Madrid", "Bayern Munich", "2.25", "3.60", "3.00", "UCL")}
              className="flex items-center gap-1 rounded-lg border border-slate-800 bg-[#091120] px-2.5 py-1 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              <Trophy className="h-3 w-3 text-teal-400" />
              <span>Madrid vs Bayern (UCL)</span>
            </button>
            <button
              type="button"
              onClick={() => handleSetPreset("Tottenham", "Roma", "2.00", "3.40", "3.70", "UEL")}
              className="flex items-center gap-1 rounded-lg border border-slate-800 bg-[#091120] px-2.5 py-1 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
            >
              <Trophy className="h-3 w-3 text-amber-400" />
              <span>Spurs vs Roma (UEL)</span>
            </button>
          </div>
        </div>

        {/* Simulation Form */}
        <form onSubmit={handleSimulate} className="mt-5 space-y-4">
          {/* League & Cup Filter Toggle */}
          <div className="space-y-2 rounded-xl bg-slate-900/80 p-3 border border-slate-800">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-xs font-bold text-slate-400 pl-1">
                Ligas Nacionales:
              </span>
              <div className="flex flex-wrap items-center gap-1">
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("PD")}
                  className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
                    simLeague === "PD"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Shield className="h-3 w-3 text-amber-400" />
                  <span>La Liga</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("PL")}
                  className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
                    simLeague === "PL"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Shield className="h-3 w-3 text-cyan-400" />
                  <span>Premier</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("SA")}
                  className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
                    simLeague === "SA"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Shield className="h-3 w-3 text-blue-400" />
                  <span>Serie A</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("BL")}
                  className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
                    simLeague === "BL"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Shield className="h-3 w-3 text-rose-400" />
                  <span>Bundesliga</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("L1")}
                  className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
                    simLeague === "L1"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Shield className="h-3 w-3 text-indigo-400" />
                  <span>Ligue 1</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("ALL")}
                  className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
                    simLeague === "ALL"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Globe className="h-3 w-3" />
                  <span>Inter-Liga ({teams.length})</span>
                </button>
              </div>
            </div>

            {/* Tournaments and Cups Row */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-800/60">
              <span className="text-xs font-bold text-slate-400 pl-1">
                Torneos & Copas:
              </span>
              <div className="flex flex-wrap items-center gap-1">
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("UCL")}
                  className={`flex items-center gap-1 rounded-lg px-2 py-0.5 text-xs font-semibold transition-all ${
                    simLeague === "UCL"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Trophy className="h-3 w-3 text-teal-400" />
                  <span>Champions</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("UEL")}
                  className={`flex items-center gap-1 rounded-lg px-2 py-0.5 text-xs font-semibold transition-all ${
                    simLeague === "UEL"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Trophy className="h-3 w-3 text-amber-400" />
                  <span>Europa League</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("CDR")}
                  className={`flex items-center gap-1 rounded-lg px-2 py-0.5 text-xs font-semibold transition-all ${
                    simLeague === "CDR"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Shield className="h-3 w-3 text-rose-400" />
                  <span>Copa del Rey</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("FAC")}
                  className={`flex items-center gap-1 rounded-lg px-2 py-0.5 text-xs font-semibold transition-all ${
                    simLeague === "FAC"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Shield className="h-3 w-3 text-sky-400" />
                  <span>FA Cup</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("CI")}
                  className={`flex items-center gap-1 rounded-lg px-2 py-0.5 text-xs font-semibold transition-all ${
                    simLeague === "CI"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Shield className="h-3 w-3 text-emerald-400" />
                  <span>Coppa Italia</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("DFB")}
                  className={`flex items-center gap-1 rounded-lg px-2 py-0.5 text-xs font-semibold transition-all ${
                    simLeague === "DFB"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Shield className="h-3 w-3 text-yellow-400" />
                  <span>DFB-Pokal</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectSimLeague("CDF")}
                  className={`flex items-center gap-1 rounded-lg px-2 py-0.5 text-xs font-semibold transition-all ${
                    simLeague === "CDF"
                      ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Shield className="h-3 w-3 text-blue-400" />
                  <span>Coupe de France</span>
                </button>
              </div>
            </div>
          </div>

          {/* Team Selectors */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {/* Home Team */}
            <div className="rounded-xl border border-slate-800 bg-[#091120] p-4">
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-teal-400 uppercase tracking-wider">
                  Club Local
                </label>
                <span className="text-[11px] font-bold text-teal-300 bg-teal-500/10 px-2 py-0.5 rounded-md border border-teal-500/20">
                  Rating: {homeAvgRating}
                </span>
              </div>
              <select
                value={homeTeamId}
                onChange={(e) => setHomeTeamId(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-xs sm:text-sm font-semibold text-white focus:border-teal-500 focus:outline-none"
              >
                {availableTeams.map((t) => (
                  <option key={t.id} value={t.id} disabled={t.id === awayTeamId}>
                    {t.name} ({t.code ? `${t.code} · ` : ""}{t.country || "Club"})
                  </option>
                ))}
              </select>
            </div>

            {/* Away Team */}
            <div className="rounded-xl border border-slate-800 bg-[#091120] p-4">
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
                  Club Visitante
                </label>
                <span className="text-[11px] font-bold text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded-md border border-cyan-500/20">
                  Rating: {awayAvgRating}
                </span>
              </div>
              <select
                value={awayTeamId}
                onChange={(e) => setAwayTeamId(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-xs sm:text-sm font-semibold text-white focus:border-teal-500 focus:outline-none"
              >
                {availableTeams.map((t) => (
                  <option key={t.id} value={t.id} disabled={t.id === homeTeamId}>
                    {t.name} ({t.code ? `${t.code} · ` : ""}{t.country || "Club"})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Lineup & Player Absences Manager */}
          <div className="rounded-2xl border border-slate-800/80 bg-[#070e1c] p-4 sm:p-5">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-800/70 pb-3">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-teal-400" />
                <h3 className="text-sm font-bold text-white">
                  Alineaciones & Simulación de Bajas
                </h3>
                <span className="text-[10px] bg-slate-900 text-slate-400 px-2 py-0.5 rounded-full border border-slate-800 font-medium">
                  Haz clic en un jugador para simular su ausencia
                </span>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-xs text-slate-400">
                  Diferencial:{" "}
                  <strong
                    className={
                      parseFloat(ratingDiff) > 0
                        ? "text-teal-400"
                        : parseFloat(ratingDiff) < 0
                        ? "text-rose-400"
                        : "text-slate-300"
                    }
                  >
                    {parseFloat(ratingDiff) > 0 ? `+${ratingDiff}` : ratingDiff} pts
                  </strong>
                </div>
                <button
                  type="button"
                  onClick={() => setShowLineups(!showLineups)}
                  className="flex items-center gap-1 text-xs text-slate-400 hover:text-white font-medium"
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
              <div className="flex h-28 items-center justify-center gap-2 text-xs text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin text-teal-400" />
                <span>Cargando plantillas...</span>
              </div>
            ) : showLineups ? (
              <div className="mt-4 grid grid-cols-1 gap-5 lg:grid-cols-2">
                {/* Home Team Squad */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-white">
                      {homeTeamObj?.name} ({homeActive.length}/{homeSquad.length} disponibles)
                    </span>
                    {benchedHome.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setBenchedHome([])}
                        className="text-[11px] text-teal-400 hover:underline font-medium"
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
                              ? "border-rose-900/40 bg-rose-950/20 opacity-50 line-through text-slate-500"
                              : "border-slate-800 bg-[#091120] hover:border-teal-500/50 text-white"
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
                              <span className="font-bold text-slate-300 flex items-center gap-0.5">
                                <Star className="h-2.5 w-2.5 text-amber-400 fill-amber-400" />
                                {p.rating?.toFixed(1)}
                              </span>
                              {isBenched ? (
                                <UserX className="h-3 w-3 text-rose-400" />
                              ) : (
                                <UserCheck className="h-3 w-3 text-teal-400" />
                              )}
                            </div>
                          </div>
                          <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400">
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
                    <span className="font-bold text-white">
                      {awayTeamObj?.name} ({awayActive.length}/{awaySquad.length} disponibles)
                    </span>
                    {benchedAway.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setBenchedAway([])}
                        className="text-[11px] text-cyan-400 hover:underline font-medium"
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
                              ? "border-rose-900/40 bg-rose-950/20 opacity-50 line-through text-slate-500"
                              : "border-slate-800 bg-[#091120] hover:border-cyan-500/50 text-white"
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
                              <span className="font-bold text-slate-300 flex items-center gap-0.5">
                                <Star className="h-2.5 w-2.5 text-amber-400 fill-amber-400" />
                                {p.rating?.toFixed(1)}
                              </span>
                              {isBenched ? (
                                <UserX className="h-3 w-3 text-rose-400" />
                              ) : (
                                <UserCheck className="h-3 w-3 text-teal-400" />
                              )}
                            </div>
                          </div>
                          <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400">
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
          <div className="rounded-xl border border-slate-800 bg-[#091120] p-4">
            <span className="text-xs font-bold text-slate-300 block mb-2.5">
              Cuotas de tu Casa de Apuestas:
            </span>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1 font-semibold">
                  1 · Victoria Local
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  value={hOdds}
                  onChange={(e) => setHOdds(e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-900/90 px-3 py-1.5 text-xs font-bold text-white focus:border-teal-500 focus:outline-none"
                  placeholder="Ej. 2.10"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1 font-semibold">
                  X · Empate
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  value={dOdds}
                  onChange={(e) => setDOdds(e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-900/90 px-3 py-1.5 text-xs font-bold text-white focus:border-teal-500 focus:outline-none"
                  placeholder="Ej. 3.30"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1 font-semibold">
                  2 · Victoria Visitante
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="1.01"
                  value={aOdds}
                  onChange={(e) => setAOdds(e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-900/90 px-3 py-1.5 text-xs font-bold text-white focus:border-teal-500 focus:outline-none"
                  placeholder="Ej. 3.50"
                />
              </div>
            </div>
          </div>

          {error && (
            <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300 font-medium">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-teal-500 py-3 text-sm font-black text-slate-950 shadow-lg shadow-teal-500/20 hover:bg-teal-400 transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Simulando con Ensamble de IA...</span>
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
            <h3 className="text-base font-bold text-white">Resultado de la Simulación</h3>
            <span className="text-xs text-teal-300 font-semibold bg-teal-500/10 border border-teal-500/20 px-2.5 py-0.5 rounded-full">
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
