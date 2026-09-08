import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { OverviewCards } from "./components/OverviewCards";
import { MatchList } from "./components/MatchList";
import { PredictionDetail } from "./components/PredictionDetail";
import { MatchSimulator } from "./components/MatchSimulator";
import { ModelsView } from "./components/ModelsView";
import { GuideView } from "./components/GuideView";
import { ErrorBoundary } from "./components/ErrorBoundary";
import {
  fetchOverview,
  fetchTeams,
  fetchMatches,
  fetchPrediction,
  simulateMatch,
  fetchModels,
  checkBackendHealth,
} from "./services/api";
import type {
  OverviewStats,
  Team,
  Match,
  PredictionResult,
  ModelRecord,
} from "./types/api";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"matches" | "simulator" | "models" | "guide">("matches");
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(true);

  // Data States
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [models, setModels] = useState<ModelRecord[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);

  // Pagination & Filters
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalMatches, setTotalMatches] = useState<number>(0);
  const [selectedLeague, setSelectedLeague] = useState<string | undefined>(undefined);
  const [statusFilter, setStatusFilter] = useState<"upcoming" | "finished">("upcoming");

  // Loaders
  const [loadingOverview, setLoadingOverview] = useState<boolean>(true);
  const [loadingMatches, setLoadingMatches] = useState<boolean>(true);
  const [loadingPrediction, setLoadingPrediction] = useState<boolean>(false);
  const [loadingModels] = useState<boolean>(false);

  // Odds State for Selected Match
  const [currentOdds, setCurrentOdds] = useState<{ h: number; d: number; a: number }>({
    h: 2.20,
    d: 3.40,
    a: 3.30,
  });

  // Initial Load
  useEffect(() => {
    const initializeData = async () => {
      const healthy = await checkBackendHealth();
      setIsBackendOnline(healthy);

      try {
        const [overviewData, teamsData, modelsData] = await Promise.all([
          fetchOverview().catch(() => null),
          fetchTeams().catch(() => []),
          fetchModels().catch(() => []),
        ]);

        if (overviewData) setOverview(overviewData);
        if (teamsData) setTeams(teamsData);
        if (modelsData) setModels(modelsData);
      } catch (err) {
        console.error("Error cargando datos iniciales:", err);
      } finally {
        setLoadingOverview(false);
      }
    };

    initializeData();
  }, []);

  // Fetch matches on page, league, or status filter change
  useEffect(() => {
    let isCancelled = false;

    const loadMatches = async () => {
      setLoadingMatches(true);
      try {
        const res = await fetchMatches(currentPage, 12, selectedLeague, undefined, statusFilter);
        if (isCancelled) return;

        setMatches(res.data);
        setTotalPages(res.pagination.pages);
        setTotalMatches(res.pagination.total);

        // Auto-select first match if available
        if (res.data.length > 0) {
          handleSelectMatch(res.data[0]);
        } else {
          setSelectedMatch(null);
          setPrediction(null);
        }
      } catch (err) {
        console.error("Error cargando partidos:", err);
      } finally {
        if (!isCancelled) setLoadingMatches(false);
      }
    };

    loadMatches();
    return () => {
      isCancelled = true;
    };
  }, [currentPage, selectedLeague, statusFilter]);

  // Handle Match Selection
  const handleSelectMatch = async (match: Match) => {
    setSelectedMatch(match);
    const oddsToUse = match.odds ? { h: match.odds.h, d: match.odds.d, a: match.odds.a } : currentOdds;
    setCurrentOdds(oddsToUse);
    setLoadingPrediction(true);
    try {
      const pred = await fetchPrediction(match.id, {
        h_odds: oddsToUse.h,
        d_odds: oddsToUse.d,
        a_odds: oddsToUse.a,
      });
      setPrediction(pred);
    } catch (err) {
      console.error("Error al obtener predicción:", err);
    } finally {
      setLoadingPrediction(false);
    }
  };

  // Recalculate Odds on Selected Match
  const handleRecalculateOdds = async (h: number, d: number, a: number) => {
    if (!selectedMatch) return;
    setCurrentOdds({ h, d, a });
    setLoadingPrediction(true);
    try {
      const pred = await fetchPrediction(selectedMatch.id, {
        h_odds: h,
        d_odds: d,
        a_odds: a,
      });
      setPrediction(pred);
    } catch (err) {
      console.error("Error recalculando cuotas:", err);
    } finally {
      setLoadingPrediction(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 selection:bg-teal-500 selection:text-slate-950">
      {/* Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isBackendOnline={isBackendOnline}
      />

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 space-y-6">
        {/* Crisp Header Title & Description (Immediate Context) */}
        <div className="rounded-2xl border border-slate-800/80 bg-[#070e1c] p-5 sm:p-6 shadow-xl">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <span className="inline-flex items-center gap-1.5 rounded-md bg-teal-500/10 px-2.5 py-1 text-xs font-bold text-teal-400 border border-teal-500/30 mb-2">
                Inteligencia Cuantitativa de Apuestas
              </span>
              <h1 className="text-xl sm:text-2xl font-black tracking-tight text-white">
                Pronósticos Basados en IA & Detección de Valor (+EV)
              </h1>
              <p className="mt-1 text-xs sm:text-sm text-slate-400 max-w-3xl">
                Ensamble probabilístico de 5 algoritmos entrenados con 89 variables estadísticas, ratings de más de 600 jugadores y Poisson bivariado para proyectar resultados en las 5 Grandes Ligas y Champions League.
              </p>
            </div>
            <div className="hidden lg:flex items-center gap-3">
              <div className="text-right text-xs">
                <span className="text-slate-400 block font-medium">Competiciones Calibradas</span>
                <strong className="text-teal-300">España · Inglaterra · Italia · Alemania · Francia · UCL</strong>
              </div>
            </div>
          </div>
        </div>

        {/* KPI Metric Cards */}
        <OverviewCards stats={overview} loading={loadingOverview} />

        {/* Tab Content */}
        <ErrorBoundary fallbackTitle="Error al cargar la sección">
          {activeTab === "matches" && (
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 items-start">
              {/* Left: Matches List (7 cols on lg) */}
              <div className="lg:col-span-7">
                <MatchList
                  matches={matches}
                  loading={loadingMatches}
                  currentPage={currentPage}
                  totalPages={totalPages}
                  totalMatches={totalMatches}
                  selectedLeague={selectedLeague}
                  onSelectLeague={(league) => {
                    setSelectedLeague(league);
                    setCurrentPage(1);
                  }}
                  statusFilter={statusFilter}
                  onSelectStatus={(status) => {
                    setStatusFilter(status);
                    setCurrentPage(1);
                  }}
                  onPageChange={(page) => setCurrentPage(page)}
                  onSelectMatch={handleSelectMatch}
                  selectedMatchId={selectedMatch?.id}
                />
              </div>

              {/* Right: Detailed Prediction & +EV Analysis (5 cols on lg) */}
              <div className="lg:col-span-5 lg:sticky lg:top-20">
                <PredictionDetail
                  prediction={prediction}
                  loading={loadingPrediction}
                  onRecalculateOdds={handleRecalculateOdds}
                  initialOdds={currentOdds}
                />
              </div>
            </div>
          )}

          {activeTab === "simulator" && (
            <MatchSimulator
              teams={teams}
              onSimulate={simulateMatch}
            />
          )}

          {activeTab === "models" && (
            <ModelsView
              models={models}
              loading={loadingModels}
            />
          )}

          {activeTab === "guide" && (
            <GuideView />
          )}
        </ErrorBoundary>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-slate-800/80 bg-[#050a14] py-6 text-center text-xs text-slate-400">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-1">
          <p className="font-semibold text-slate-300">
            SportPredict AI · Sistema Cuantitativo de Inferencia Deportiva
          </p>
          <p className="text-slate-400">
            Modelos calibrados para La Liga, Premier League, Serie A, Bundesliga, Ligue 1 y Champions League.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;
