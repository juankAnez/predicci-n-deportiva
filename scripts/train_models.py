#!/usr/bin/env python
"""Train all ML models with current data"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
import pandas as pd
from datetime import datetime

from src.config import settings
from src.infrastructure.database.repositories import MatchRepository
from src.application.services.feature_service import FeatureService
from src.ml.training.trainer import ModelTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    print("=" * 60)
    print("  PREDICCIÓN DEPORTIVA - Entrenamiento de Modelos")
    print("=" * 60)

    print("\n[1/4] Cargando partidos históricos de la base de datos...")
    match_repo = MatchRepository()
    matches = match_repo.get_all()
    print(f"  -> {len(matches)} partidos encontrados")

    if not matches:
        print("  [ERROR] No hay partidos en la base de datos. Ejecute import_data.py primero.")
        sys.exit(1)

    print("\n[2/4] Generando variables y estadísticas rodantes (Features)...")
    feature_service = FeatureService()
    matches_df = feature_service.build_training_dataframe(matches)
    print(f"  -> {len(matches_df)} partidos con historial temporal completo")

    trainer = ModelTrainer()
    X, y_goals, y_result = trainer.prepare_data(matches_df)
    print(f"  -> {X.shape[1]} variables (features) por muestra")
    print(f"  -> {X.shape[0]} muestras listas para entrenamiento")

    print("\n[3/4] Entrenando conjunto de modelos (Poisson, XGBoost, LightGBM, RF, Ensemble)...")
    models = trainer.train_models(X, y_result, y_goals)
    print(f"  -> Modelos entrenados con éxito: {', '.join(models.keys())}")

    print("\n[4/4] Guardando modelos entrenados y versionando en BD...")
    trainer.save_models(models)

    print("\n" + "=" * 60)
    print("  [OK] ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
