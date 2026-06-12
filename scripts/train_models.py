#!/usr/bin/env python
"""Train all ML models with current data"""

import logging
import pandas as pd
from datetime import datetime

from src.config import settings
from src.infrastructure.database.repositories import MatchRepository
from src.ml.training.trainer import ModelTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    print("=" * 60)
    print("  PREDICCIÓN DEPORTIVA - Entrenamiento de Modelos")
    print("=" * 60)

    print("\n[1/4] Cargando datos históricos...")
    match_repo = MatchRepository()
    matches = match_repo.get_all()
    print(f"  → {len(matches)} partidos cargados")

    match_data = [
        {
            "home_team_id": m.home_team_id,
            "away_team_id": m.away_team_id,
            "home_goals": m.home_score or 0,
            "away_goals": m.away_score or 0,
            "match_date": m.match_date,
            "result": (
                "H" if (m.home_score or 0) > (m.away_score or 0)
                else "A" if (m.away_score or 0) > (m.home_score or 0)
                else "D"
            ) if m.home_score is not None else None,
        }
        for m in matches if m.home_score is not None
    ]
    print(f"  → {len(match_data)} partidos con resultado conocido")

    df = pd.DataFrame(match_data)

    print("\n[2/4] Generando features...")
    trainer = ModelTrainer()
    X, y_goals, y_result = trainer.prepare_data(df)
    print(f"  → {X.shape[1]} features generadas")
    print(f"  → {X.shape[0]} muestras")

    print("\n[3/4] Entrenando modelos...")
    models = trainer.train_models(X, y_result, y_goals)
    print(f"  → Modelos entrenados: {', '.join(models.keys())}")

    print("\n[4/4] Guardando modelos...")
    trainer.save_models(models)

    print("\n" + "=" * 60)
    print("  ✓ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
