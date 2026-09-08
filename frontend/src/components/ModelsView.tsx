import React from "react";
import { Cpu, CheckCircle2, Layers, Zap, Brain, Activity, Clock } from "lucide-react";
import type { ModelRecord } from "../types/api";

interface ModelsViewProps {
  models: ModelRecord[];
  loading: boolean;
}

export const ModelsView: React.FC<ModelsViewProps> = ({ models, loading }) => {
  const modelDescriptions: Record<string, { desc: string; icon: any; color: string; badge: string }> = {
    ensemble: {
      desc: "Combina de forma adaptativa las probabilidades de todos los submodelos para maximizar la robustez predictiva y minimizar la varianza de error.",
      icon: Brain,
      color: "emerald",
      badge: "Meta-Modelo Principal",
    },
    poisson: {
      desc: "Calcula la distribución estadística bivariada de goles esperados (xG) para local y visitante, matrices de marcadores exactos y mercados Over/Under.",
      icon: Activity,
      color: "amber",
      badge: "Distribución de Goles",
    },
    xgboost: {
      desc: "Algoritmo de Gradient Boosted Decision Trees entrenado sobre 89 variables estadísticas para capturar relaciones no lineales complejas.",
      icon: Zap,
      color: "cyan",
      badge: "Gradiente Impulsado",
    },
    random_forest: {
      desc: "Bosque de múltiples árboles de decisión aleatorizados con validación cruzada para evitar sobreajuste y estabilizar predicciones.",
      icon: Layers,
      color: "teal",
      badge: "Bagging & Varianza",
    },
    lightgbm: {
      desc: "Implementación ultra-optimizada por histogramas de árboles de decisión orientada a predicción de alta velocidad.",
      icon: Cpu,
      color: "indigo",
      badge: "Histogram Boost",
    },
    neural_network: {
      desc: "Perceptrón Multicapa (MLP) con regularización L2 y Dropout para detectar patrones latentes entre rachas y ratings Elo.",
      icon: Brain,
      color: "purple",
      badge: "Deep Learning MLP",
    },
  };

  // Deduplicate models by model_name keeping latest version
  const uniqueModels = React.useMemo(() => {
    if (!models || !Array.isArray(models)) return [];
    const map = new Map<string, ModelRecord>();
    for (const m of models) {
      if (m && m.model_name && !map.has(m.model_name)) {
        map.set(m.model_name, m);
      }
    }
    return Array.from(map.values());
  }, [models]);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-emerald-500/20 p-2 text-emerald-400">
            <Cpu className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Arquitectura de Modelos de Inteligencia Artificial</h2>
            <p className="text-xs text-slate-400">
              6 modelos entrenados y calibrados con 2,280 partidos reales de La Liga y Premier League
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-56 animate-pulse rounded-2xl border border-slate-800 bg-slate-900/40 p-5" />
          ))}
        </div>
      ) : uniqueModels.length === 0 ? (
        <div className="flex h-48 flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 py-8 text-center">
          <p className="text-sm font-medium text-slate-400">No se encontraron modelos registrados.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {uniqueModels.map((model) => {
            const info = modelDescriptions[model.model_name] || {
              desc: "Modelo estadístico para predicción de resultados deportivos.",
              icon: Cpu,
              color: "emerald",
              badge: model.model_type,
            };
            const Icon = info.icon;

            return (
              <div
                key={model.id}
                className="group relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/50 p-5 backdrop-blur-sm transition-all hover:border-slate-700 hover:bg-slate-900/80"
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <div className="rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-emerald-400">
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white capitalize text-sm">
                        {model.model_name.replace("_", " ")}
                      </h3>
                      <span className="text-[11px] text-slate-400">{model.model_type}</span>
                    </div>
                  </div>

                  <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-300">
                    <CheckCircle2 className="h-2.5 w-2.5" />
                    <span>Activo</span>
                  </span>
                </div>

                {/* Description */}
                <p className="mt-3.5 text-xs text-slate-300 leading-relaxed min-h-[50px]">{info.desc}</p>

                {/* Specs */}
                <div className="mt-4 grid grid-cols-2 gap-2 border-t border-slate-800/80 pt-3 text-xs">
                  <div className="rounded-lg bg-slate-950/40 p-2">
                    <span className="text-[10px] text-slate-400 block">Variables Analizadas</span>
                    <span className="font-mono font-bold text-white">{model.feature_count} features</span>
                  </div>
                  <div className="rounded-lg bg-slate-950/40 p-2">
                    <span className="text-[10px] text-slate-400 block">Especialidad</span>
                    <span className="font-semibold text-emerald-400 truncate block text-[11px]">
                      {info.badge}
                    </span>
                  </div>
                </div>

                {/* Footer */}
                <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    <span>Versión: {model.version}</span>
                  </span>
                  <span className="font-mono text-emerald-400/80 text-[10px]">.joblib</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

