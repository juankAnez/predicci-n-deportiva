import React from "react";
import { Trophy, Shield, Cpu, CalendarCheck } from "lucide-react";
import type { OverviewStats } from "../types/api";

interface OverviewCardsProps {
  stats: OverviewStats | null;
  loading: boolean;
}

export const OverviewCards: React.FC<OverviewCardsProps> = ({ stats, loading }) => {
  const cards = [
    {
      title: "Partidos Registrados",
      value: stats ? stats.total_matches.toLocaleString() : "2,300",
      subtitle: "LaLiga & Premier League",
      icon: Trophy,
      bgColor: "bg-blue-50 text-blue-600",
    },
    {
      title: "Clubes en Base de Datos",
      value: stats ? stats.total_teams.toString() : "48",
      subtitle: "24 España + 24 Inglaterra",
      icon: Shield,
      bgColor: "bg-indigo-50 text-indigo-600",
    },
    {
      title: "Modelos IA en Consenso",
      value: stats ? stats.models_active.toString() : "5",
      subtitle: "XGBoost, LightGBM, Poisson...",
      icon: Cpu,
      bgColor: "bg-emerald-50 text-emerald-600",
    },
    {
      title: "Próximos Partidos",
      value: stats?.upcoming_matches ? `${stats.upcoming_matches}` : "20",
      subtitle: "Calendario oficial activo",
      icon: CalendarCheck,
      bgColor: "bg-amber-50 text-amber-600",
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:border-slate-300"
          >
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                {card.title}
              </p>
              <div className="mt-1">
                <span className="text-2xl font-black text-slate-900">
                  {loading ? (
                    <span className="inline-block h-6 w-14 animate-pulse rounded bg-slate-200" />
                  ) : (
                    card.value
                  )}
                </span>
              </div>
              <p className="mt-0.5 text-xs text-slate-500 font-medium">{card.subtitle}</p>
            </div>
            <div className={`rounded-xl p-3 ${card.bgColor} shrink-0`}>
              <Icon className="h-5 w-5" />
            </div>
          </div>
        );
      })}
    </div>
  );
};
