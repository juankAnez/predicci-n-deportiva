import React from "react";
import { Trophy, Users, Cpu, TrendingUp } from "lucide-react";
import type { OverviewStats } from "../types/api";

interface OverviewCardsProps {
  stats: OverviewStats | null;
  loading: boolean;
}

export const OverviewCards: React.FC<OverviewCardsProps> = ({ stats, loading }) => {
  const cards = [
    {
      title: "Partidos Analizados",
      value: stats ? stats.total_matches.toLocaleString() : "2,280",
      subtitle: "La Liga & Premier League",
      icon: Trophy,
      gradient: "from-emerald-500/20 via-emerald-500/5 to-transparent",
      iconColor: "text-emerald-400",
      borderColor: "border-emerald-500/20",
    },
    {
      title: "Clubes en Base de Datos",
      value: stats ? stats.total_teams.toString() : "48",
      subtitle: "Historial y métricas de racha",
      icon: Users,
      gradient: "from-teal-500/20 via-teal-500/5 to-transparent",
      iconColor: "text-teal-400",
      borderColor: "border-teal-500/20",
    },
    {
      title: "Modelos AI en Producción",
      value: stats ? stats.models_active.toString() : "6",
      subtitle: "Ensemble, Poisson, XGBoost, etc.",
      icon: Cpu,
      gradient: "from-cyan-500/20 via-cyan-500/5 to-transparent",
      iconColor: "text-cyan-400",
      borderColor: "border-cyan-500/20",
    },
    {
      title: "Ventaja Estadística (+EV)",
      value: "Kelly 1/4",
      subtitle: "Gestión óptima de bankroll",
      icon: TrendingUp,
      gradient: "from-indigo-500/20 via-indigo-500/5 to-transparent",
      iconColor: "text-indigo-400",
      borderColor: "border-indigo-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`relative overflow-hidden rounded-2xl border ${card.borderColor} bg-slate-900/60 p-5 backdrop-blur-sm transition-all hover:scale-[1.01] hover:border-slate-700`}
          >
            <div className={`absolute -right-4 -top-4 h-24 w-24 rounded-full bg-gradient-to-br ${card.gradient} blur-xl`} />
            <div className="relative flex items-center justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{card.title}</p>
                <div className="mt-1 flex items-baseline gap-2">
                  <span className="text-2xl font-extrabold tracking-tight text-white">
                    {loading ? (
                      <span className="inline-block h-7 w-16 animate-pulse rounded bg-slate-800" />
                    ) : (
                      card.value
                    )}
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-400">{card.subtitle}</p>
              </div>
              <div className={`rounded-xl border border-slate-800 bg-slate-800/50 p-3 ${card.iconColor}`}>
                <Icon className="h-6 w-6" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
