import React, { useState } from "react";
import {
  Search,
  ChevronLeft,
  ChevronRight,
  Calendar,
  Clock,
  ArrowRight,
  Loader2,
  History,
  CalendarDays,
  Globe,
  Shield,
  Trophy,
} from "lucide-react";
import type { Match } from "../types/api";

interface MatchListProps {
  matches: Match[];
  loading: boolean;
  currentPage: number;
  totalPages: number;
  totalMatches: number;
  selectedLeague: string | undefined;
  onSelectLeague: (league: string | undefined) => void;
  statusFilter: "upcoming" | "finished";
  onSelectStatus: (status: "upcoming" | "finished") => void;
  onPageChange: (newPage: number) => void;
  onSelectMatch: (match: Match) => void;
  selectedMatchId?: number;
}

export const MatchList: React.FC<MatchListProps> = ({
  matches,
  loading,
  currentPage,
  totalPages,
  totalMatches,
  selectedLeague,
  onSelectLeague,
  statusFilter,
  onSelectStatus,
  onPageChange,
  onSelectMatch,
  selectedMatchId,
}) => {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredMatches = matches.filter((m) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      m.home_team_name.toLowerCase().includes(q) ||
      m.away_team_name.toLowerCase().includes(q)
    );
  });

  const getCompetitionBadge = (compCode?: string, compId?: number) => {
    if (compId === 10 || compCode === "UCL") {
      return { name: "Champions League", style: "border-teal-500/30 bg-teal-500/10 text-teal-300" };
    }
    if (compId === 7 || compCode === "SA") {
      return { name: "Serie A", style: "border-blue-500/30 bg-blue-500/10 text-blue-300" };
    }
    if (compId === 8 || compCode === "BL") {
      return { name: "Bundesliga", style: "border-rose-500/30 bg-rose-500/10 text-rose-300" };
    }
    if (compId === 9 || compCode === "L1") {
      return { name: "Ligue 1", style: "border-indigo-500/30 bg-indigo-500/10 text-indigo-300" };
    }
    if (compId && [4, 5, 6, 13].includes(compId)) {
      return { name: "Premier League", style: "border-cyan-500/30 bg-cyan-500/10 text-cyan-300" };
    }
    return { name: "La Liga", style: "border-amber-500/30 bg-amber-500/10 text-amber-300" };
  };

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-[#070e1c] p-4 sm:p-5 shadow-lg space-y-4">
      {/* Top Status Tabs: Upcoming vs History */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/70 pb-3.5">
        <div className="flex items-center gap-1.5 rounded-xl bg-slate-900/90 p-1 border border-slate-800">
          <button
            onClick={() => onSelectStatus("upcoming")}
            className={`flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all ${
              statusFilter === "upcoming"
                ? "bg-slate-800 text-teal-300 shadow-sm border border-teal-500/30 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <CalendarDays className="h-4 w-4 text-teal-400" />
            <span>Próximos Partidos</span>
            <span
              className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                statusFilter === "upcoming"
                  ? "bg-teal-500/20 text-teal-300"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              {totalMatches > 0 && statusFilter === "upcoming" ? totalMatches : 36}
            </span>
          </button>

          <button
            onClick={() => onSelectStatus("finished")}
            className={`flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all ${
              statusFilter === "finished"
                ? "bg-slate-800 text-teal-300 shadow-sm border border-teal-500/30 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <History className="h-4 w-4 text-slate-400" />
            <span>Resultados Anteriores</span>
          </button>
        </div>

        <span className="text-xs text-slate-400 font-medium">
          {totalMatches.toLocaleString()}{" "}
          {statusFilter === "upcoming" ? "partidos activos" : "partidos en archivo"}
        </span>
      </div>

      {/* European Leagues Selector */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={() => onSelectLeague(undefined)}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
              selectedLeague === undefined
                ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                : "border border-slate-800 bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Globe className="h-3.5 w-3.5" />
            <span>Todas</span>
          </button>

          <button
            onClick={() => onSelectLeague("PD")}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
              selectedLeague === "PD"
                ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                : "border border-slate-800 bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Shield className="h-3.5 w-3.5 text-amber-400" />
            <span>La Liga</span>
          </button>

          <button
            onClick={() => onSelectLeague("PL")}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
              selectedLeague === "PL"
                ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                : "border border-slate-800 bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Shield className="h-3.5 w-3.5 text-cyan-400" />
            <span>Premier</span>
          </button>

          <button
            onClick={() => onSelectLeague("SA")}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
              selectedLeague === "SA"
                ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                : "border border-slate-800 bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Shield className="h-3.5 w-3.5 text-blue-400" />
            <span>Serie A</span>
          </button>

          <button
            onClick={() => onSelectLeague("BL")}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
              selectedLeague === "BL"
                ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                : "border border-slate-800 bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Shield className="h-3.5 w-3.5 text-rose-400" />
            <span>Bundesliga</span>
          </button>

          <button
            onClick={() => onSelectLeague("L1")}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
              selectedLeague === "L1"
                ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                : "border border-slate-800 bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Shield className="h-3.5 w-3.5 text-indigo-400" />
            <span>Ligue 1</span>
          </button>

          <button
            onClick={() => onSelectLeague("UCL")}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
              selectedLeague === "UCL"
                ? "bg-teal-500 text-slate-950 font-bold shadow-sm"
                : "border border-slate-800 bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Trophy className="h-3.5 w-3.5 text-teal-400" />
            <span>Champions</span>
          </button>
        </div>

        {/* Search Box */}
        <div className="relative w-full sm:w-56">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Buscar club..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-slate-800 bg-slate-900/90 py-1.5 pl-8 pr-3 text-xs text-white placeholder-slate-500 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500/20"
          />
        </div>
      </div>

      {/* Matches Grid */}
      <div className="mt-1">
        {loading ? (
          <div className="flex h-64 flex-col items-center justify-center gap-2">
            <Loader2 className="h-7 w-7 animate-spin text-teal-400" />
            <p className="text-xs text-slate-400">Cargando partidos...</p>
          </div>
        ) : filteredMatches.length === 0 ? (
          <div className="flex h-44 flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 py-8 text-center bg-slate-900/40">
            <p className="text-xs font-medium text-slate-400">
              No se encontraron partidos con los filtros seleccionados.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-2">
            {filteredMatches.map((match) => {
              const isSelected = match.id === selectedMatchId;
              const isUpcoming = match.home_score === null && match.away_score === null;
              const badge = getCompetitionBadge(match.league_code, match.competition_id);

              return (
                <div
                  key={match.id}
                  onClick={() => onSelectMatch(match)}
                  className={`group cursor-pointer rounded-xl border p-3.5 transition-all ${
                    isSelected
                      ? "border-teal-500 bg-teal-500/10 shadow-md shadow-teal-500/10 ring-1 ring-teal-500/30"
                      : "border-slate-800/80 bg-[#091120] hover:border-slate-700 hover:bg-[#0c162a]"
                  }`}
                >
                  {/* Header: Competition Badge & Date */}
                  <div className="flex items-center justify-between text-[11px] text-slate-400 border-b border-slate-800/60 pb-2">
                    <span
                      className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 font-bold border ${badge.style}`}
                    >
                      <Shield className="h-3 w-3" />
                      {badge.name}
                    </span>
                    <div className="flex items-center gap-1 text-slate-400">
                      <Calendar className="h-3 w-3 text-slate-500" />
                      <span>{match.date || "Por definir"}</span>
                      {match.time && (
                        <span className="flex items-center gap-0.5 text-slate-500 ml-1">
                          <Clock className="h-3 w-3" />
                          {match.time.slice(0, 5)}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Teams and Scores */}
                  <div className="mt-3 flex items-center justify-between gap-2">
                    {/* Home Team */}
                    <div className="flex-1 text-left">
                      <p className="text-sm font-bold text-white group-hover:text-teal-300 transition-colors">
                        {match.home_team_name}
                      </p>
                      <span className="text-[10px] text-slate-500 font-medium">Local</span>
                    </div>

                    {/* Score or VS Badge */}
                    <div className="flex flex-col items-center justify-center px-2">
                      {!isUpcoming ? (
                        <div className="rounded-lg border border-slate-700 bg-slate-800 px-2.5 py-1 text-xs font-bold text-white">
                          {match.home_score} - {match.away_score}
                        </div>
                      ) : (
                        <span className="rounded-md bg-slate-800/80 border border-slate-700 px-2 py-0.5 text-[10px] font-bold text-slate-300">
                          VS
                        </span>
                      )}
                    </div>

                    {/* Away Team */}
                    <div className="flex-1 text-right">
                      <p className="text-sm font-bold text-white group-hover:text-teal-300 transition-colors">
                        {match.away_team_name}
                      </p>
                      <span className="text-[10px] text-slate-500 font-medium">Visitante</span>
                    </div>
                  </div>

                  {/* Odds Preview */}
                  {isUpcoming && match.odds && (
                    <div className="mt-2.5 flex items-center justify-between rounded-lg bg-slate-900/90 border border-slate-800 px-2 py-1 text-[11px]">
                      <span className="text-slate-500 font-medium">Cuotas:</span>
                      <div className="flex items-center gap-2 font-mono">
                        <span className="text-slate-400">
                          1: <strong className="text-white">{match.odds.h.toFixed(2)}</strong>
                        </span>
                        <span className="text-slate-600">·</span>
                        <span className="text-slate-400">
                          X: <strong className="text-white">{match.odds.d.toFixed(2)}</strong>
                        </span>
                        <span className="text-slate-600">·</span>
                        <span className="text-slate-400">
                          2: <strong className="text-white">{match.odds.a.toFixed(2)}</strong>
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Card Footer */}
                  <div className="mt-2.5 flex items-center justify-between border-t border-slate-800/60 pt-2 text-xs">
                    <span className="text-slate-500 text-[10px]">
                      {match.stage || `ID #${match.id}`}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 text-xs font-semibold ${
                        isSelected ? "text-teal-400" : "text-slate-400 group-hover:text-teal-300"
                      }`}
                    >
                      <span>{isSelected ? "Seleccionado" : isUpcoming ? "Predecir con IA" : "Ver Análisis"}</span>
                      <ArrowRight className="h-3 w-3 transition-transform group-hover:translate-x-0.5" />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Pagination Footer */}
      {!loading && totalPages > 1 && (
        <div className="mt-4 flex flex-col items-center justify-between gap-3 border-t border-slate-800/80 pt-3 sm:flex-row">
          <p className="text-xs text-slate-400">
            Página <strong className="text-white">{currentPage}</strong> de{" "}
            <strong className="text-white">{totalPages}</strong> ({totalMatches.toLocaleString()} partidos)
          </p>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="flex items-center gap-1 rounded-lg border border-slate-800 bg-slate-900 px-3 py-1.5 text-xs font-semibold text-slate-300 transition-all hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-30"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              <span>Anterior</span>
            </button>

            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="flex items-center gap-1 rounded-lg border border-slate-800 bg-slate-900 px-3 py-1.5 text-xs font-semibold text-slate-300 transition-all hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-30"
            >
              <span>Siguiente</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
