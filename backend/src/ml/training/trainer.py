import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json
import joblib
from pathlib import Path

from src.config import settings
from src.ml.models.base_model import BaseModel
from src.ml.models.poisson_model import PoissonModel
from src.ml.models.xgboost_model import XGBoostModel
from src.ml.models.lightgbm_model import LightGBMModel
from src.ml.models.random_forest_model import RandomForestModel
from src.ml.models.neural_network_model import NeuralNetworkModel
from src.ml.models.ensemble_model import EnsembleModel
from src.ml.features.feature_pipeline import FeaturePipeline


class ModelTrainer:
    def __init__(self):
        self.feature_pipeline = FeaturePipeline()
        self.models_dir = Path(settings.ML_MODELS_DIR)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def prepare_data(self, matches_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
        features = self.feature_pipeline.build_features(matches_df)
        features = self.feature_pipeline.encode_categorical(features)

        y_result = matches_df["result"].map({"H": 0, "D": 1, "A": 2})
        y_goals = matches_df[["home_goals", "away_goals"]]

        return features, y_goals, y_result

    def train_models(self, X: pd.DataFrame, y_result: pd.Series,
                     y_goals: pd.DataFrame, **kwargs) -> Dict[str, BaseModel]:
        models = {}

        # Poisson
        print("Entrenando Poisson...")
        poisson = PoissonModel()
        poisson.feature_names = X.columns.tolist()
        poisson.train(X, y_goals)
        models["poisson"] = poisson

        # XGBoost
        print("Entrenando XGBoost...")
        xgb = XGBoostModel()
        xgb.feature_names = X.columns.tolist()
        xgb.train(X.values, y_result.values, **kwargs)
        models["xgboost"] = xgb

        # LightGBM
        print("Entrenando LightGBM...")
        lgb = LightGBMModel()
        lgb.feature_names = X.columns.tolist()
        lgb.train(X.values, y_goals.values)
        models["lightgbm"] = lgb

        # Random Forest (benchmark)
        print("Entrenando Random Forest...")
        rf = RandomForestModel()
        rf.feature_names = X.columns.tolist()
        rf.train(X.values, y_result.values)
        models["random_forest"] = rf

        # Neural Network (condicional)
        nn = NeuralNetworkModel()
        nn.feature_names = X.columns.tolist()
        try:
            nn.train(X.values, y_result.values, **kwargs.get("nn_params", {}))
            models["neural_network"] = nn
        except Exception as e:
            print(f"Neural Network no disponible: {e}")

        # Ensemble
        print("Creando Ensemble...")
        ensemble = EnsembleModel(method="weighted_average")
        ensemble.add_model(poisson, weight=0.15)
        ensemble.add_model(xgb, weight=0.35)
        ensemble.add_model(lgb, weight=0.25)
        ensemble.add_model(rf, weight=0.15)
        if "neural_network" in models:
            ensemble.add_model(models["neural_network"], weight=0.10)
        ensemble.feature_names = X.columns.tolist()
        ensemble.train(X.values, y_result.values)
        models["ensemble"] = ensemble

        return models

    def save_models(self, models: Dict[str, BaseModel], metadata: Optional[Dict] = None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for name, model in models.items():
            path = self.models_dir / f"{name}_{timestamp}.joblib"
            model.save(str(path))

            from src.infrastructure.database.connection import db_session
            from src.infrastructure.database.models import ModelVersionModel

            db = db_session()
            version = ModelVersionModel(
                model_name=name,
                version=timestamp,
                model_type=type(model).__name__,
                model_file_path=str(path),
                feature_count=len(model.feature_names) if model.feature_names else 0,
                feature_list=json.dumps(model.feature_names) if model.feature_names else None,
                status="active",
                is_ensemble=isinstance(model, EnsembleModel),
            )
            if metadata:
                version.metrics = json.dumps(metadata.get(name, {}))
            db.add(version)
            db.commit()
            db.close()

        print(f"Modelos guardados en {self.models_dir}")

    def load_best_model(self) -> BaseModel:
        from src.infrastructure.database.connection import db_session
        from src.infrastructure.database.models import ModelVersionModel

        db = db_session()
        best = (
            db.query(ModelVersionModel)
            .filter(
                ModelVersionModel.status == "active",
                ModelVersionModel.model_name == "ensemble",
            )
            .order_by(ModelVersionModel.training_date.desc())
            .first()
        )
        db.close()

        if best and best.model_file_path:
            path = Path(best.model_file_path)
            if path.exists():
                from src.ml.models.ensemble_model import EnsembleModel
                model = EnsembleModel()
                model.load(str(path))
                return model

        raise FileNotFoundError("No se encontró modelo ensemble entrenado")
