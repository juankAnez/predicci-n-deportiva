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

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-6 shadow-sm space-y-5">
      {/* Top Status Tabs: Upcoming vs History */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div className="flex items-center gap-1.5 rounded-xl bg-slate-100 p-1 border border-slate-200/60">
          <button
            onClick={() => onSelectStatus("upcoming")}
            className={`flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all ${
              statusFilter === "upcoming"
                ? "bg-white text-slate-900 shadow-sm border border-slate-200/80"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <CalendarDays className="h-4 w-4 text-blue-600" />
            <span>Próximos Partidos</span>
            <span
              className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                statusFilter === "upcoming"
                  ? "bg-blue-50 text-blue-700"
                  : "bg-slate-200 text-slate-600"
              }`}
            >
              20
            </span>
          </button>

          <button
            onClick={() => onSelectStatus("finished")}
            className={`flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all ${
              statusFilter === "finished"
                ? "bg-white text-slate-900 shadow-sm border border-slate-200/80"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <History className="h-4 w-4 text-slate-600" />
            <span>Historial de Resultados</span>
          </button>
        </div>

        <span className="text-xs text-slate-500 font-medium">
          {totalMatches.toLocaleString()}{" "}
          {statusFilter === "upcoming" ? "partidos por jugar" : "partidos registrados"}
        </span>
      </div>

      {/* Filters Bar: League and Search */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        {/* League Selector */}
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={() => onSelectLeague(undefined)}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
              selectedLeague === undefined
                ? "bg-slate-900 text-white shadow-sm"
                : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 hover:text-slate-900"
            }`}
          >
            <Globe className="h-3.5 w-3.5" />
            <span>Todas</span>
          </button>
          <button
            onClick={() => onSelectLeague("PD")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
              selectedLeague === "PD"
                ? "bg-slate-900 text-white shadow-sm"
                : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 hover:text-slate-900"
            }`}
          >
            <Shield className="h-3.5 w-3.5 text-amber-500" />
            <span>LaLiga EA Sports</span>
          </button>
          <button
            onClick={() => onSelectLeague("PL")}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
              selectedLeague === "PL"
                ? "bg-slate-900 text-white shadow-sm"
                : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 hover:text-slate-900"
            }`}
          >
            <Shield className="h-3.5 w-3.5 text-blue-500" />
            <span>Premier League</span>
          </button>
        </div>

        {/* Search Box */}
        <div className="relative w-full sm:w-60">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar club..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-slate-200 bg-slate-50 py-1.5 pl-8 pr-3 text-xs text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
      </div>

      {/* Matches Grid */}
      <div className="mt-2">
        {loading ? (
          <div className="flex h-64 flex-col items-center justify-center gap-2">
            <Loader2 className="h-7 w-7 animate-spin text-blue-600" />
            <p className="text-xs text-slate-500">Cargando partidos...</p>
          </div>
        ) : filteredMatches.length === 0 ? (
          <div className="flex h-44 flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 py-8 text-center bg-slate-50/50">
            <p className="text-xs font-medium text-slate-500">
              No se encontraron partidos con los filtros actuales.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-2">
            {filteredMatches.map((match) => {
              const isSelected = match.id === selectedMatchId;
              const isLaLiga =
                match.league_code === "PD" ||
                match.league === "La Liga" ||
                match.competition_id <= 3;
              const isUpcoming = match.home_score === null && match.away_score === null;

              return (
                <div
                  key={match.id}
                  onClick={() => onSelectMatch(match)}
                  className={`group cursor-pointer rounded-xl border p-4 transition-all ${
                    isSelected
                      ? "border-blue-600 bg-blue-50/40 shadow-sm ring-2 ring-blue-500/20"
                      : "border-slate-200 bg-white hover:border-blue-300 hover:shadow-sm"
                  }`}
                >
                  {/* Header: League & Date */}
                  <div className="flex items-center justify-between text-[11px] text-slate-500 border-b border-slate-100 pb-2">
                    <span
                      className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 font-bold ${
                        isLaLiga
                          ? "bg-amber-50 text-amber-800 border border-amber-200/60"
                          : "bg-blue-50 text-blue-800 border border-blue-200/60"
                      }`}
                    >
                      <Shield className="h-3 w-3" />
                      {isLaLiga ? "LaLiga" : "Premier League"}
                    </span>
                    <div className="flex items-center gap-1 text-slate-500">
                      <Calendar className="h-3 w-3 text-slate-400" />
                      <span>{match.date || "Por definir"}</span>
                      {match.time && (
                        <span className="flex items-center gap-0.5 text-slate-400 ml-1">
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
                      <p className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                        {match.home_team_name}
                      </p>
                      <span className="text-[11px] text-slate-400 font-medium">Local</span>
                    </div>

                    {/* Result or VS badge */}
                    <div className="flex flex-col items-center justify-center px-2">
                      {!isUpcoming ? (
                        <div className="rounded-lg border border-slate-200 bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-900">
                          {match.home_score} - {match.away_score}
                        </div>
                      ) : (
                        <span className="rounded-md bg-slate-100 border border-slate-200 px-2 py-0.5 text-[11px] font-bold text-slate-600">
                          VS
                        </span>
                      )}
                    </div>

                    {/* Away Team */}
                    <div className="flex-1 text-right">
                      <p className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                        {match.away_team_name}
                      </p>
                      <span className="text-[11px] text-slate-400 font-medium">Visitante</span>
                    </div>
                  </div>

                  {/* Odds Preview (if upcoming) */}
                  {isUpcoming && match.odds && (
                    <div className="mt-3 flex items-center justify-between rounded-lg bg-slate-50 border border-slate-200/80 px-2.5 py-1.5 text-[11px]">
                      <span className="text-slate-500 font-medium">Cuotas de Mercado:</span>
                      <div className="flex items-center gap-2 font-mono">
                        <span className="text-slate-600">
                          1: <strong className="text-slate-900">{match.odds.h.toFixed(2)}</strong>
                        </span>
                        <span className="text-slate-300">·</span>
                        <span className="text-slate-600">
                          X: <strong className="text-slate-900">{match.odds.d.toFixed(2)}</strong>
                        </span>
                        <span className="text-slate-300">·</span>
                        <span className="text-slate-600">
                          2: <strong className="text-slate-900">{match.odds.a.toFixed(2)}</strong>
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Card Footer */}
                  <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-2 text-xs">
                    <span className="text-slate-400 text-[11px]">
                      {match.stage || `Partido #${match.id}`}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 text-xs font-semibold ${
                        isSelected ? "text-blue-600" : "text-slate-500 group-hover:text-blue-600"
                      }`}
                    >
                      <span>{isSelected ? "Seleccionado" : isUpcoming ? "Analizar con IA" : "Ver Análisis"}</span>
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
        <div className="mt-5 flex flex-col items-center justify-between gap-3 border-t border-slate-100 pt-4 sm:flex-row">
          <p className="text-xs text-slate-500">
            Página <strong className="text-slate-900">{currentPage}</strong> de{" "}
            <strong className="text-slate-900">{totalPages}</strong> ({totalMatches.toLocaleString()} partidos)
          </p>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition-all hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              <span>Anterior</span>
            </button>

            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition-all hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
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
