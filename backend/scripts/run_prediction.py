#!/usr/bin/env python
"""Run prediction for a specific match with Betting Market (+EV) analysis"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.application.services.prediction_service import PredictionService
from src.infrastructure.database.repositories import MatchRepository, TeamRepository
from src.domain.value_objects.betting_market import BettingOdds


def main():
    if len(sys.argv) < 2:
        print("Uso: python run_prediction.py <match_id> [odds_local odds_empate odds_visitante]")
        print("Ejemplo: python run_prediction.py 1 2.20 3.40 3.30")
        sys.exit(1)

    match_id = int(sys.argv[1])

    # Parse optional market odds
    odds = None
    if len(sys.argv) >= 5:
        try:
            h_odds = float(sys.argv[2])
            d_odds = float(sys.argv[3])
            a_odds = float(sys.argv[4])
            odds = BettingOdds(home_win=h_odds, draw=d_odds, away_win=a_odds)
        except ValueError:
            print("[AVISO] Cuotas inválidas, continuando sin análisis de mercado.")

    print("=" * 60)
    print(f"  PREDICCIÓN DEPORTIVA & ANÁLISIS DE MERCADO")
    print("=" * 60)

    match_repo = MatchRepository()
    team_repo = TeamRepository()
    match = match_repo.get_by_id(match_id)

    if not match:
        print(f"\n[ERROR] Partido #{match_id} no encontrado en la base de datos.")
        sys.exit(1)

    home_team = team_repo.get_by_id(match.home_team_id)
    away_team = team_repo.get_by_id(match.away_team_id)
    home_name = home_team.name if home_team else f"Team_{match.home_team_id}"
    away_name = away_team.name if away_team else f"Team_{match.away_team_id}"

    print(f"\n  Partido #{match_id}: {home_name} vs {away_name}")
    print(f"  Fecha: {match.match_date} | Temporada: {match.season}")

    try:
        service = PredictionService()
        result = service.predict_match(match_id, odds=odds)

        res = result["result"]
        print(f"\n[1] Probabilidades Calculadas (Ensemble ML):")
        print(f"    Victoria {home_name} (1): {res['home_win']['probability']}%")
        print(f"    Empate (X):               {res['draw']['probability']}%")
        print(f"    Victoria {away_name} (2): {res['away_win']['probability']}%")
        print(f"    -> Pronóstico más probable: {res['predicted']} (Confianza: {res['confidence']}%)")

        goals = result["goals"]
        print(f"\n[2] Estimación de Goles (Modelo Poisson):")
        print(f"    Goles esperados {home_name}: {goals['home_expected']}")
        print(f"    Goles esperados {away_name}: {goals['away_expected']}")
        print(f"    Goles totales esperados:      {goals['total_expected']}")
        print(f"    Marcador más probable:        {goals['most_likely_score']} ({goals['most_likely_score_probability']}%)")

        print(f"\n[3] Mercados Over/Under:")
        for k, v in result["over_under"].items():
            print(f"    {k.upper()}: {v}%")

        # Top features
        top_f = result["explanation"].get("top_features", [])
        if top_f:
            print(f"\n[4] Factores Clave de la Predicción:")
            for f in top_f[:5]:
                print(f"    * {f['name']}: {f['importance']:.4f}")

        # Market analysis if odds were provided
        market = result.get("market_analysis")
        if market:
            print(f"\n" + "=" * 60)
            print(f"  ANÁLISIS DEL MERCADO DE APUESTAS & VALOR (+EV)")
            print("=" * 60)
            print(f"  Margen de la casa: {market['margin_percentage']}%")
            print(f"\n  Comparativa de Probabilidades & Rentabilidad Esperada:")
            for opp in market["opportunities"]:
                ev_str = f"+{opp['ev_pct']}%" if opp['ev_pct'] > 0 else f"{opp['ev_pct']}%"
                val_indicator = "[+VALOR]" if opp["has_value"] else "       "
                print(f"    {opp['label']:<10} | Cuota: {opp['odds']:<5} | Modelo: {opp['model_prob_pct']}% | Mercado Justo: {opp['fair_prob_pct']}% | EV: {ev_str:<7} {val_indicator}")

            best = market["best_bet"]
            if best:
                print(f"\n  -> MEJOR OPORTUNIDAD: Apostar a {best['label']} (Cuota {best['odds']})")
                print(f"     Ventaja esperada (+EV): +{best['ev_pct']}%")
                print(f"     Stake sugerido (Kelly 1/4): {best['suggested_stake_bankroll_pct']}% del bankroll")
            else:
                print(f"\n  -> No se detectó valor suficiente (+EV) en las cuotas actuales.")

        print("\n" + "=" * 60)
        print("  [OK] Predicción generada correctamente.")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] al generar predicción: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
