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
      value: stats ? stats.total_matches.toLocaleString() : "2,340",
      subtitle: "Top 5 Ligas & Champions",
      icon: Trophy,
      bgColor: "bg-teal-500/10 text-teal-400 border border-teal-500/20",
    },
    {
      title: "Clubes en Base de Datos",
      value: stats ? stats.total_teams.toString() : "68",
      subtitle: "ESP · ENG · ITA · GER · FRA",
      icon: Shield,
      bgColor: "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20",
    },
    {
      title: "Modelos IA en Consenso",
      value: stats ? stats.models_active.toString() : "5",
      subtitle: "XGBoost, LightGBM, Poisson...",
      icon: Cpu,
      bgColor: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
    },
    {
      title: "Próximos Partidos",
      value: stats?.upcoming_matches ? `${stats.upcoming_matches}` : "36",
      subtitle: "Jornada europea oficial",
      icon: CalendarCheck,
      bgColor: "bg-amber-500/10 text-amber-400 border border-amber-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className="flex items-center justify-between rounded-xl border border-slate-800/80 bg-[#08101d] p-4 shadow-md transition-all hover:border-slate-700"
          >
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                {card.title}
              </p>
              <div className="mt-1">
                <span className="text-2xl font-black text-white">
                  {loading ? (
                    <span className="inline-block h-6 w-14 animate-pulse rounded bg-slate-800" />
                  ) : (
                    card.value
                  )}
                </span>
              </div>
              <p className="mt-0.5 text-xs text-slate-400 font-medium">{card.subtitle}</p>
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
