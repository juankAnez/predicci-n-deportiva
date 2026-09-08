import React from "react";
import { Cpu, CheckCircle2, Layers, Zap, BrainCircuit, Activity, Clock } from "lucide-react";
import type { ModelRecord } from "../types/api";

interface ModelsViewProps {
  models: ModelRecord[];
  loading: boolean;
}

export const ModelsView: React.FC<ModelsViewProps> = ({ models, loading }) => {
  const modelDescriptions: Record<
    string,
    { desc: string; icon: React.ComponentType<{ className?: string }>; bgColor: string; textColor: string; badge: string }
  > = {
    ensemble: {
      desc: "Combina de forma adaptativa las probabilidades de todos los submodelos para maximizar la robustez predictiva y minimizar la varianza.",
      icon: BrainCircuit,
      bgColor: "bg-teal-500/10 border border-teal-500/20",
      textColor: "text-teal-400",
      badge: "Ensamble Principal (Ponderado)",
    },
    poisson: {
      desc: "Calcula la distribución estadística bivariada de goles esperados (xG) para local y visitante, matrices de marcadores exactos y mercados Over/Under.",
      icon: Activity,
      bgColor: "bg-amber-500/10 border border-amber-500/20",
      textColor: "text-amber-400",
      badge: "Distribución de Goles",
    },
    xgboost: {
      desc: "Algoritmo de Gradient Boosted Decision Trees entrenado sobre 89 variables estadísticas para capturar relaciones no lineales complejas.",
      icon: Zap,
      bgColor: "bg-cyan-500/10 border border-cyan-500/20",
      textColor: "text-cyan-400",
      badge: "Gradiente Impulsado (35% peso)",
    },
    random_forest: {
      desc: "Bosque de múltiples árboles de decisión aleatorizados con validación cruzada para evitar sobreajuste y estabilizar predicciones.",
      icon: Layers,
      bgColor: "bg-emerald-500/10 border border-emerald-500/20",
      textColor: "text-emerald-400",
      badge: "Bagging & Varianza",
    },
    lightgbm: {
      desc: "Implementación ultra-optimizada por histogramas de árboles de decisión orientada a predicción de alta velocidad.",
      icon: Cpu,
      bgColor: "bg-sky-500/10 border border-sky-500/20",
      textColor: "text-sky-400",
      badge: "Histogram Boost (25% peso)",
    },
    neural_network: {
      desc: "Perceptrón Multicapa (MLP) con regularización L2 y Dropout para detectar patrones latentes entre rachas y ratings Elo.",
      icon: BrainCircuit,
      bgColor: "bg-purple-500/10 border border-purple-500/20",
      textColor: "text-purple-400",
      badge: "Red Neuronal MLP",
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
      {/* Header Panel */}
      <div className="rounded-2xl border border-slate-800/80 bg-[#070e1c] p-5 sm:p-6 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-teal-500/10 p-2.5 text-teal-400 border border-teal-500/20">
            <Cpu className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">
              Arquitectura de Modelos de Inteligencia Artificial
            </h2>
            <p className="text-xs text-slate-400 font-medium">
              5 modelos estadísticos y de Machine Learning calibrados con validación temporal estricta
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div
              key={i}
              className="h-48 animate-pulse rounded-2xl border border-slate-800/60 bg-[#070e1c] p-5"
            />
          ))}
        </div>
      ) : uniqueModels.length === 0 ? (
        <div className="flex h-44 flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 bg-[#070e1c] py-8 text-center">
          <p className="text-xs font-medium text-slate-400">No se encontraron modelos registrados.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {uniqueModels.map((model) => {
            const info = modelDescriptions[model.model_name] || {
              desc: "Modelo cuantitativo para predicción de resultados deportivos.",
              icon: Cpu,
              bgColor: "bg-teal-500/10 border border-teal-500/20",
              textColor: "text-teal-400",
              badge: model.model_type,
            };
            const Icon = info.icon;

            return (
              <div
                key={model.id}
                className="rounded-2xl border border-slate-800/80 bg-[#070e1c] p-5 shadow-lg transition-all hover:border-slate-700 hover:shadow-cyan-950/20"
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <div className={`rounded-xl p-2.5 ${info.bgColor} ${info.textColor}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white capitalize text-sm">
                        {model.model_name.replace("_", " ")}
                      </h3>
                      <span className="text-[11px] text-slate-400 font-medium">
                        {model.model_type}
                      </span>
                    </div>
                  </div>

                  <span className="inline-flex items-center gap-1 rounded-full border border-teal-500/30 bg-teal-500/10 px-2 py-0.5 text-[10px] font-bold text-teal-400">
                    <CheckCircle2 className="h-3 w-3 text-teal-400" />
                    <span>Activo</span>
                  </span>
                </div>

                {/* Description */}
                <p className="mt-3 text-xs text-slate-400 leading-relaxed min-h-[48px]">
                  {info.desc}
                </p>

                {/* Specs */}
                <div className="mt-4 grid grid-cols-2 gap-2 border-t border-slate-800/80 pt-3 text-xs">
                  <div className="rounded-lg bg-[#091120] p-2.5 border border-slate-800/60">
                    <span className="text-[10px] text-slate-400 font-bold uppercase block tracking-wider">
                      Variables
                    </span>
                    <span className="font-mono font-bold text-white text-xs">
                      {model.feature_count} features
                    </span>
                  </div>
                  <div className="rounded-lg bg-[#091120] p-2.5 border border-slate-800/60">
                    <span className="text-[10px] text-slate-400 font-bold uppercase block tracking-wider">
                      Especialidad
                    </span>
                    <span className="font-bold text-slate-200 truncate block text-[11px]">
                      {info.badge}
                    </span>
                  </div>
                </div>

                {/* Footer */}
                <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3 text-slate-400" />
                    <span>Versión: {model.version}</span>
                  </span>
                  <span className="font-mono text-slate-400 font-semibold text-[10px] bg-slate-800/50 px-1.5 py-0.5 rounded border border-slate-700/50">
                    .joblib
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
