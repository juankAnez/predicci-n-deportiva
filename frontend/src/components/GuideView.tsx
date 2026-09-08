import React from "react";
import { BookOpen, TrendingUp, ShieldAlert, CheckCircle2, Award, DollarSign, Brain } from "lucide-react";

export const GuideView: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Hero Header */}
      <div className="rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-emerald-950/30 p-6 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-emerald-500/20 p-2.5 text-emerald-400">
            <BookOpen className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-white sm:text-2xl">
              Guía de Estrategia: Valor Esperado (+EV) & Criterio de Kelly
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Cómo los profesionales usan la estadística y el machine learning para batir el mercado deportivo
            </p>
          </div>
        </div>
      </div>

      {/* Grid of Key Concepts */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Concept 1: Overround */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
          <div className="flex items-center gap-2.5 text-amber-400">
            <ShieldAlert className="h-5 w-5" />
            <h3 className="font-bold text-base text-white">1. La Trampa del Margen de la Casa (Overround)</h3>
          </div>
          <p className="mt-3 text-xs sm:text-sm text-slate-300 leading-relaxed">
            Las casas de apuestas nunca ofrecen cuotas justas. Si sumas las probabilidades implícitas de las cuotas de un partido (1 / Cuota), la suma no da 100%, sino entre <strong>104% y 110%</strong>.
          </p>
          <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/60 p-3.5 text-xs text-slate-400 font-mono">
            Margen = (1/Cuota_1 + 1/Cuota_X + 1/Cuota_2) - 1
          </div>
          <p className="mt-3 text-xs text-slate-400">
            Ese excedente del 4% al 10% es la comisión matemática que garantiza que la casa siempre gane a largo plazo, a menos que identifiques apuestas con valor real.
          </p>
        </div>

        {/* Concept 2: Expected Value */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
          <div className="flex items-center gap-2.5 text-emerald-400">
            <TrendingUp className="h-5 w-5" />
            <h3 className="font-bold text-base text-white">2. ¿Qué es una Apuesta con Valor Positivo (+EV)?</h3>
          </div>
          <p className="mt-3 text-xs sm:text-sm text-slate-300 leading-relaxed">
            Una apuesta tiene <strong>+EV</strong> cuando la probabilidad calculada por nuestros modelos de IA es mayor que la probabilidad que la casa de apuestas le asigna a esa cuota.
          </p>
          <div className="mt-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3.5 text-xs text-emerald-300 font-mono">
            EV = (Probabilidad_Modelo × Cuota_Casa) - 1
          </div>
          <p className="mt-3 text-xs text-slate-400">
            Si el resultado de la fórmula es mayor a 0 (ej. +11.45%), la apuesta es matemáticamente rentable a largo plazo, independientemente de lo que suceda en un solo partido.
          </p>
        </div>

        {/* Concept 3: Kelly Criterion */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
          <div className="flex items-center gap-2.5 text-teal-400">
            <DollarSign className="h-5 w-5" />
            <h3 className="font-bold text-base text-white">3. Criterio de Kelly (Gestión de Bankroll)</h3>
          </div>
          <p className="mt-3 text-xs sm:text-sm text-slate-300 leading-relaxed">
            El mayor error del apostador novato es apostar cantidades al azar o doblar apuestas tras perder. El Criterio de Kelly calcula científicamente el porcentaje exacto de tu dinero que debes arriesgar.
          </p>
          <div className="mt-4 rounded-xl border border-teal-500/30 bg-teal-500/10 p-3.5 text-xs text-teal-300 font-mono">
            f* = (b × p - q) / b
          </div>
          <p className="mt-3 text-xs text-slate-400">
            Nuestro sistema utiliza <strong>Kelly 1/4 (Fraccional)</strong>, la variante conservadora recomendada por inversores cuantitativos para proteger el capital contra rachas negativas de varianza.
          </p>
        </div>

        {/* Concept 4: AI Ensemble */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
          <div className="flex items-center gap-2.5 text-cyan-400">
            <Brain className="h-5 w-5" />
            <h3 className="font-bold text-base text-white">4. El Ensamble Multimodelo</h3>
          </div>
          <p className="mt-3 text-xs sm:text-sm text-slate-300 leading-relaxed">
            Ningún modelo individual es infalible. Por eso utilizamos un Ensamble de 6 algoritmos:
          </p>
          <ul className="mt-3 space-y-1.5 text-xs text-slate-300">
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
              <span><strong>Poisson:</strong> Modela la distribución de goles e intensidad de ataque.</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
              <span><strong>XGBoost & LightGBM:</strong> Detectan sinergias complejas entre 89 variables.</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
              <span><strong>Elo Dinámico:</strong> Ajusta la fuerza real de cada club tras cada partido.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Rules of Thumb */}
      <div className="rounded-2xl border border-emerald-500/40 bg-emerald-500/10 p-6 backdrop-blur-sm">
        <div className="flex items-center gap-2 text-emerald-400">
          <Award className="h-5 w-5" />
          <h3 className="font-bold text-base text-white">Reglas de Oro para Usar Este Sistema</h3>
        </div>
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
            <span className="font-bold text-white block mb-1">1. Solo Apuesta con +EV</span>
            <p className="text-slate-400">
              Si el sistema muestra EV negativo (-), no apuestes, incluso si crees que el favorito va a ganar. La cuota no compensa el riesgo.
            </p>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
            <span className="font-bold text-white block mb-1">2. Respeta el Stake Kelly</span>
            <p className="text-slate-400">
              Nunca sobrepases el porcentaje de bankroll recomendado por el sistema (usualmente entre 1% y 3%).
            </p>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
            <span className="font-bold text-white block mb-1">3. Piensa en Volumen</span>
            <p className="text-slate-400">
              La ley de los grandes números requiere de 100 a 500 apuestas para que la ventaja matemática (+EV) se materialice sobre la varianza.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
