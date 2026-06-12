import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.config import settings
from src.domain.entities import Prediction
from src.infrastructure.database.repositories import (
    MatchRepository, PredictionRepository
)
from src.application.services.feature_service import FeatureService
from src.ml.models.base_model import BaseModel
from src.ml.models.poisson_model import PoissonModel
from src.ml.models.ensemble_model import EnsembleModel
from src.ml.explainability.shap_explainer import SHAPExplainer

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self):
        self.feature_service = FeatureService()
        self.match_repo = MatchRepository()
        self.prediction_repo = PredictionRepository()
        self.explainer = SHAPExplainer()
        self.model: Optional[EnsembleModel] = None

    def _load_models(self) -> EnsembleModel:
        if self.model is not None:
            return self.model

        models_dir = Path(settings.ML_MODELS_DIR)
        if not models_dir.exists():
            raise FileNotFoundError(
                "No hay modelos entrenados. Ejecute train_models.py primero."
            )

        ensemble = EnsembleModel()
        for model_class, name, weight in [
            (PoissonModel, "poisson", 0.15),
        ]:
            model_path = self._find_latest_model(name)
            if model_path:
                model = model_class()
                model.load(str(model_path))
                ensemble.add_model(model, weight)

        if not ensemble.models:
            raise FileNotFoundError(
                "No se encontraron modelos entrenados en el directorio."
            )

        self.model = ensemble
        return ensemble

    def _find_latest_model(self, model_name: str) -> Optional[Path]:
        models_dir = Path(settings.ML_MODELS_DIR)
        pattern = f"{model_name}_*.joblib"
        files = list(models_dir.glob(pattern))
        if files:
            return sorted(files)[-1]
        return None

    def predict_match(self, match_id: int) -> Dict[str, Any]:
        match = self.match_repo.get_by_id(match_id)
        if not match:
            raise ValueError(f"Match {match_id} no encontrado")

        features = self.feature_service.generate_features_for_match(
            match.home_team_id, match.away_team_id,
            match.match_date, match.competition_id, match.stage
        )

        ensemble = self._load_models()
        if isinstance(features, pd.DataFrame):
            X = features.values.astype(np.float32)
        else:
            X = features.astype(np.float32)

        if X.ndim == 1:
            X = X.reshape(1, -1)

        proba = ensemble.predict_proba(X)[0]
        pred_class = np.argmax(proba)
        result_map = {0: "H", 1: "D", 2: "A"}

        poisson_model = None
        for m, _ in ensemble.models:
            if isinstance(m, PoissonModel):
                poisson_model = m
                break

        home_team_name = self.match_repo.get_by_id(match_id).home_team_name or f"Team_{match.home_team_id}"
        away_team_name = self.match_repo.get_by_id(match_id).away_team_name or f"Team_{match.away_team_id}"

        score_probs = {}
        home_goals_exp = 0.0
        away_goals_exp = 0.0
        if poisson_model:
            score_probs = poisson_model.predict_score_proba(
                str(match.home_team_id), str(match.away_team_id)
            )
            exp = poisson_model.predict(pd.DataFrame([{
                "team_home": str(match.home_team_id),
                "team_away": str(match.away_team_id),
            }]))[0]
            home_goals_exp = float(exp[0])
            away_goals_exp = float(exp[1])

        over_under = {}
        if poisson_model:
            over_under = poisson_model.predict_over_under(
                str(match.home_team_id), str(match.away_team_id)
            )

        explanation = self.explainer.explain(ensemble, X, features.columns.tolist())

        prediction = Prediction(
            match_id=match_id,
            home_win_probability=float(proba[0]),
            draw_probability=float(proba[1]),
            away_win_probability=float(proba[2]),
            predicted_result=result_map[pred_class],
            home_goals_expected=home_goals_exp,
            away_goals_expected=away_goals_exp,
            total_goals_expected=home_goals_exp + away_goals_exp,
            over_05_probability=over_under.get("over_0.5", 0.0),
            over_15_probability=over_under.get("over_1.5", 0.0),
            over_25_probability=over_under.get("over_2.5", 0.0),
            over_35_probability=over_under.get("over_3.5", 0.0),
            over_45_probability=over_under.get("over_4.5", 0.0),
            exact_score_probabilities=dict(list(score_probs.items())[:10]),
            most_likely_score=list(score_probs.keys())[0] if score_probs else None,
            most_likely_score_prob=list(score_probs.values())[0] if score_probs else 0.0,
            confidence_score=float(np.max(proba) * 100),
            model_agreement=float(np.max(proba)),
            prediction_std=float(np.std(proba)),
            shap_values=explanation.get("shap_values"),
            top_features=explanation.get("top_features"),
        )

        try:
            self.prediction_repo.create(prediction)
        except Exception as e:
            logger.error(f"Error guardando predicción: {e}")

        return self._format_response(prediction, explanation, match_id)

    def _format_response(self, prediction: Prediction, explanation: Dict[str, Any],
                          match_id: int) -> Dict[str, Any]:
        return {
            "match_id": match_id,
            "prediction_date": datetime.now().isoformat(),
            "result": {
                "home_win": {
                    "probability": round(prediction.home_win_probability * 100, 2),
                    "label": "Victoria Local",
                },
                "draw": {
                    "probability": round(prediction.draw_probability * 100, 2),
                    "label": "Empate",
                },
                "away_win": {
                    "probability": round(prediction.away_win_probability * 100, 2),
                    "label": "Victoria Visitante",
                },
                "predicted": prediction.predicted_result,
                "confidence": round(prediction.confidence_score, 1),
            },
            "goals": {
                "home_expected": round(prediction.home_goals_expected, 2),
                "away_expected": round(prediction.away_goals_expected, 2),
                "total_expected": round(prediction.total_goals_expected, 2),
                "most_likely_score": prediction.most_likely_score,
                "most_likely_score_probability": round(prediction.most_likely_score_prob * 100, 2),
                "exact_scores": prediction.exact_score_probabilities,
            },
            "over_under": {
                "over_0.5": round(prediction.over_05_probability * 100, 2),
                "over_1.5": round(prediction.over_15_probability * 100, 2),
                "over_2.5": round(prediction.over_25_probability * 100, 2),
                "over_3.5": round(prediction.over_35_probability * 100, 2),
                "over_4.5": round(prediction.over_45_probability * 100, 2),
            },
            "explanation": {
                "top_features": explanation.get("top_features", []),
                "method": explanation.get("method", "none"),
                "summary": self.explainer.format_explanation(explanation),
            },
            "model_info": {
                "models_used": 5,
                "agreement": round(prediction.model_agreement * 100, 1),
                "std_dev": round(prediction.prediction_std, 4),
            },
        }
