import React from "react";
import { BookOpen, TrendingUp, ShieldAlert, CheckCircle2, Award, DollarSign, BrainCircuit } from "lucide-react";

export const GuideView: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-blue-50 p-2.5 text-blue-600 border border-blue-100">
            <BookOpen className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              Guía de Estrategia: Valor Esperado (+EV) & Criterio de Kelly
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 font-medium">
              Cómo los profesionales cuantitativos emplean la probabilidad estadística para batir el mercado
            </p>
          </div>
        </div>
      </div>

      {/* Grid of Key Concepts */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
        {/* Concept 1: Overround */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm">
          <div className="flex items-center gap-2 text-amber-600">
            <ShieldAlert className="h-5 w-5" />
            <h3 className="font-bold text-sm sm:text-base text-slate-900">
              1. La Trampa del Margen de la Casa (Overround)
            </h3>
          </div>
          <p className="mt-2.5 text-xs sm:text-sm text-slate-600 leading-relaxed">
            Las casas de apuestas nunca ofrecen cuotas justas. Si sumas las probabilidades implícitas de las cuotas de un partido (1 / Cuota), la suma no da 100%, sino entre <strong>104% y 108%</strong>.
          </p>
          <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-800 font-mono">
            Margen = (1 / Cuota_1 + 1 / Cuota_X + 1 / Cuota_2) - 1
          </div>
          <p className="mt-2.5 text-xs text-slate-500">
            Ese excedente es la comisión matemática que garantiza que la casa siempre gane, a menos que identifiques discrepancias donde la cuota esté mal fijada.
          </p>
        </div>

        {/* Concept 2: Expected Value */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm">
          <div className="flex items-center gap-2 text-emerald-600">
            <TrendingUp className="h-5 w-5" />
            <h3 className="font-bold text-sm sm:text-base text-slate-900">
              2. ¿Qué es una Apuesta con Valor Positivo (+EV)?
            </h3>
          </div>
          <p className="mt-2.5 text-xs sm:text-sm text-slate-600 leading-relaxed">
            Una apuesta tiene <strong>+EV</strong> cuando la probabilidad real calculada por nuestros modelos de IA es mayor que la probabilidad implícita en la cuota de la casa de apuestas.
          </p>
          <div className="mt-3 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-900 font-mono font-bold">
            EV = (Probabilidad_Modelo × Cuota_Casa) - 1
          </div>
          <p className="mt-2.5 text-xs text-slate-500">
            Si el resultado es mayor a 0 (ej. +8.5%), la matemática garantiza rentabilidad a largo plazo por la ley de los grandes números.
          </p>
        </div>

        {/* Concept 3: Kelly Criterion */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm">
          <div className="flex items-center gap-2 text-indigo-600">
            <DollarSign className="h-5 w-5" />
            <h3 className="font-bold text-sm sm:text-base text-slate-900">
              3. Criterio de Kelly (Gestión de Capital)
            </h3>
          </div>
          <p className="mt-2.5 text-xs sm:text-sm text-slate-600 leading-relaxed">
            El mayor error es apostar cantidades emocionales o improvisadas. El Criterio de Kelly calcula científicamente el porcentaje exacto de la banca a arriesgar en cada evento.
          </p>
          <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-800 font-mono">
            f* = 0.25 × [(b × p - q) / b]
          </div>
          <p className="mt-2.5 text-xs text-slate-500">
            El sistema aplica <strong>Kelly 1/4 (Fraccional)</strong>, la variante conservadora recomendada por inversores cuantitativos para proteger el capital contra la varianza natural.
          </p>
        </div>

        {/* Concept 4: AI Ensemble */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm">
          <div className="flex items-center gap-2 text-blue-600">
            <BrainCircuit className="h-5 w-5" />
            <h3 className="font-bold text-sm sm:text-base text-slate-900">
              4. Ensamble Multimodelo de 5 Algoritmos
            </h3>
          </div>
          <p className="mt-2.5 text-xs sm:text-sm text-slate-600 leading-relaxed">
            Ningún modelo individual es infalible. Por eso combinamos 5 motores especializados:
          </p>
          <ul className="mt-3 space-y-1.5 text-xs text-slate-700">
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-blue-600 shrink-0" />
              <span><strong>Poisson Bivariado:</strong> Modela la distribución de goles y Over/Under.</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-blue-600 shrink-0" />
              <span><strong>XGBoost & LightGBM:</strong> Detectan sinergias complejas entre 89 variables.</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-blue-600 shrink-0" />
              <span><strong>Elo Dinámico & Plantillas:</strong> Ajusta la fuerza de cada club según sus 11 titulares.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Rules of Thumb */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm space-y-3">
        <div className="flex items-center gap-2 text-slate-900">
          <Award className="h-5 w-5 text-amber-500" />
          <h3 className="font-bold text-sm sm:text-base">Reglas Clave para Usar el Sistema</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5">
            <strong className="text-slate-900 block mb-1">1. Solo Apuesta con +EV</strong>
            <p className="text-slate-600">
              Si el sistema indica EV negativo, la cuota ofrecida no compensa matemáticamente el riesgo, incluso si el club es favorito.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5">
            <strong className="text-slate-900 block mb-1">2. Respeta el Stake Sugerido</strong>
            <p className="text-slate-600">
              Nunca sobrepases el porcentaje de banca calculado por Kelly (usualmente entre el 1% y 3.5%).
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5">
            <strong className="text-slate-900 block mb-1">3. Piensa a Largo Plazo</strong>
            <p className="text-slate-600">
              La ventaja probabilística (+EV) se materializa a lo largo de decenas de partidos, no en una sola jugada.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
