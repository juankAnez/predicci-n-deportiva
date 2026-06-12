#!/usr/bin/env python
"""Run prediction for a specific match"""

import sys
import json
from datetime import datetime

from src.application.services.prediction_service import PredictionService
from src.infrastructure.database.repositories import MatchRepository


def main():
    if len(sys.argv) < 2:
        print("Uso: python run_prediction.py <match_id>")
        sys.exit(1)

    match_id = int(sys.argv[1])

    print("=" * 60)
    print(f"  GENERANDO PREDICCIÓN - Partido #{match_id}")
    print("=" * 60)

    match_repo = MatchRepository()
    match = match_repo.get_by_id(match_id)

    if not match:
        print(f"\n✗ Partido #{match_id} no encontrado")
        sys.exit(1)

    print(f"\n  Equipos: {match.home_team_id} vs {match.away_team_id}")
    print(f"  Fecha: {match.match_date}")

    try:
        service = PredictionService()
        result = service.predict_match(match_id)

        print(f"\n  Resultado:")
        print(f"    Local: {result['result']['home_win']['probability']}%")
        print(f"    Empate: {result['result']['draw']['probability']}%")
        print(f"    Visitante: {result['result']['away_win']['probability']}%")
        print(f"    Predicción: {result['result']['predicted']} (confianza: {result['result']['confidence']}%)")

        print(f"\n  Goles:")
        print(f"    Esperados Local: {result['goals']['home_expected']}")
        print(f"    Esperados Visitante: {result['goals']['away_expected']}")
        print(f"    Marcador más probable: {result['goals']['most_likely_score']}")

        print(f"\n  Over/Under:")
        for k, v in result['over_under'].items():
            print(f"    {k}: {v}%")

        print(f"\n  Top Features:")
        for f in result['explanation']['top_features'][:5]:
            print(f"    {f['name']}: {f['importance']:.4f}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
