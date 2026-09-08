import React, { useState } from "react";
import { Search, ChevronLeft, ChevronRight, Calendar, ArrowRight, Loader2 } from "lucide-react";
import type { Match } from "../types/api";

interface MatchListProps {
  matches: Match[];
  loading: boolean;
  currentPage: number;
  totalPages: number;
  totalMatches: number;
  selectedCompetition: number | undefined;
  onSelectCompetition: (compId: number | undefined) => void;
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
  selectedCompetition,
  onSelectCompetition,
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
    <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-4 sm:p-6 backdrop-blur-sm">
      {/* Filters Bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        {/* League Selector */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => onSelectCompetition(undefined)}
            className={`rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all ${
              selectedCompetition === undefined
                ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20"
                : "border border-slate-800 bg-slate-800/40 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            Todas las Ligas
          </button>
          <button
            onClick={() => onSelectCompetition(3)}
            className={`rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all ${
              selectedCompetition === 3
                ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20"
                : "border border-slate-800 bg-slate-800/40 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            🇪🇸 La Liga
          </button>
          <button
            onClick={() => onSelectCompetition(1)}
            className={`rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all ${
              selectedCompetition === 1
                ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20"
                : "border border-slate-800 bg-slate-800/40 text-slate-300 hover:bg-slate-800 hover:text-white"
            }`}
          >
            🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
          </button>
        </div>

        {/* Search Box */}
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Buscar por equipo..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-slate-800 bg-slate-950/60 py-1.5 pl-9 pr-4 text-xs sm:text-sm text-white placeholder-slate-500 focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
          />
        </div>
      </div>

      {/* Matches Grid / Table */}
      <div className="mt-5">
        {loading ? (
          <div className="flex h-64 flex-col items-center justify-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
            <p className="text-sm text-slate-400">Cargando partidos desde el backend...</p>
          </div>
        ) : filteredMatches.length === 0 ? (
          <div className="flex h-48 flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 py-8 text-center">
            <p className="text-sm font-medium text-slate-400">No se encontraron partidos con los filtros actuales.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
            {filteredMatches.map((match) => {
              const isSelected = match.id === selectedMatchId;
              const isLaLiga = match.competition_id === 3;

              return (
                <div
                  key={match.id}
                  onClick={() => onSelectMatch(match)}
                  className={`group relative cursor-pointer overflow-hidden rounded-xl border p-4 transition-all duration-200 hover:scale-[1.01] ${
                    isSelected
                      ? "border-emerald-500/80 bg-emerald-500/10 shadow-lg shadow-emerald-500/10"
                      : "border-slate-800/80 bg-slate-950/40 hover:border-slate-700 hover:bg-slate-900/60"
                  }`}
                >
                  {/* Card Header: League and Date */}
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span
                      className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 font-medium ${
                        isLaLiga
                          ? "border border-amber-500/30 bg-amber-500/10 text-amber-300"
                          : "border border-sky-500/30 bg-sky-500/10 text-sky-300"
                      }`}
                    >
                      {isLaLiga ? "🇪🇸 La Liga" : "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier"}
                    </span>
                    <div className="flex items-center gap-1 text-slate-400">
                      <Calendar className="h-3 w-3" />
                      <span>{match.date || "Fecha por definir"}</span>
                    </div>
                  </div>

                  {/* Teams and Scores */}
                  <div className="mt-3 flex items-center justify-between gap-2">
                    {/* Home Team */}
                    <div className="flex-1 text-left">
                      <p className="font-semibold text-white group-hover:text-emerald-300 transition-colors">
                        {match.home_team_name}
                      </p>
                      <span className="text-[11px] text-slate-500">Local</span>
                    </div>

                    {/* Result or VS badge */}
                    <div className="flex flex-col items-center justify-center px-3">
                      {match.home_score !== null && match.away_score !== null ? (
                        <div className="rounded-lg border border-slate-700/60 bg-slate-800/80 px-2.5 py-1 text-sm font-bold text-white shadow-inner">
                          {match.home_score} - {match.away_score}
                        </div>
                      ) : (
                        <span className="rounded-md bg-slate-800/60 px-2 py-0.5 text-xs font-semibold text-slate-400">
                          VS
                        </span>
                      )}
                    </div>

                    {/* Away Team */}
                    <div className="flex-1 text-right">
                      <p className="font-semibold text-white group-hover:text-emerald-300 transition-colors">
                        {match.away_team_name}
                      </p>
                      <span className="text-[11px] text-slate-500">Visitante</span>
                    </div>
                  </div>

                  {/* Card Footer: CTA */}
                  <div className="mt-3.5 flex items-center justify-between border-t border-slate-800/60 pt-2.5 text-xs">
                    <span className="text-slate-500 text-[11px]">Partido #{match.id}</span>
                    <span
                      className={`inline-flex items-center gap-1 font-medium transition-colors ${
                        isSelected ? "text-emerald-400 font-semibold" : "text-slate-400 group-hover:text-emerald-400"
                      }`}
                    >
                      <span>{isSelected ? "Seleccionado" : "Analizar con IA"}</span>
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
        <div className="mt-6 flex flex-col items-center justify-between gap-3 border-t border-slate-800/80 pt-4 sm:flex-row">
          <p className="text-xs text-slate-400">
            Mostrando página <span className="font-semibold text-white">{currentPage}</span> de{" "}
            <span className="font-semibold text-white">{totalPages}</span> ({totalMatches.toLocaleString()} partidos totales)
          </p>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="flex items-center gap-1 rounded-xl border border-slate-800 bg-slate-800/50 px-3 py-1.5 text-xs font-medium text-slate-300 transition-all hover:bg-slate-800 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Anterior</span>
            </button>

            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="flex items-center gap-1 rounded-xl border border-slate-800 bg-slate-800/50 px-3 py-1.5 text-xs font-medium text-slate-300 transition-all hover:bg-slate-800 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
            >
              <span>Siguiente</span>
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

