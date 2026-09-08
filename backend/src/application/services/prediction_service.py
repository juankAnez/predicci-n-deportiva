import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.config import settings
from src.domain.entities import Prediction
from src.domain.value_objects.betting_market import BettingOdds
from src.infrastructure.database.repositories import (
    MatchRepository, PredictionRepository, TeamRepository
)
from src.application.services.feature_service import FeatureService
from src.ml.models.base_model import BaseModel
from src.ml.models.poisson_model import PoissonModel
from src.ml.models.xgboost_model import XGBoostModel
from src.ml.models.random_forest_model import RandomForestModel
from src.ml.models.ensemble_model import EnsembleModel
from src.ml.explainability.shap_explainer import SHAPExplainer

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self):
        self.feature_service = FeatureService()
        self.match_repo = MatchRepository()
        self.team_repo = TeamRepository()
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

        # Check if saved ensemble exists
        ensemble_path = self._find_latest_model("ensemble")
        if ensemble_path:
            try:
                ensemble = EnsembleModel()
                ensemble.load(str(ensemble_path))
                self.model = ensemble
                return ensemble
            except Exception as e:
                logger.warning(f"Error cargando ensemble guardado: {e}")

        ensemble = EnsembleModel(method="weighted_average")
        available = [
            (PoissonModel, "poisson", 0.20),
            (XGBoostModel, "xgboost", 0.40),
            (RandomForestModel, "random_forest", 0.40),
        ]
        for model_cls, name, weight in available:
            model_path = self._find_latest_model(name)
            if model_path:
                try:
                    m = model_cls()
                    m.load(str(model_path))
                    ensemble.add_model(m, weight)
                except Exception as ex:
                    logger.warning(f"Error cargando {name}: {ex}")

        if not ensemble.models:
            raise FileNotFoundError(
                "No se encontraron modelos entrenados en el directorio. Ejecute train_models.py primero."
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

    def predict_match(self, match_id: int, odds: Optional[BettingOdds] = None) -> Dict[str, Any]:
        match = self.match_repo.get_by_id(match_id)
        if not match:
            raise ValueError(f"Match {match_id} no encontrado")

        features = self.feature_service.generate_features_for_match(
            match.home_team_id, match.away_team_id,
            match.match_date, match.competition_id, match.stage
        )

        ensemble = self._load_models()
        if ensemble.feature_names and isinstance(features, pd.DataFrame):
            for col in ensemble.feature_names:
                if col not in features.columns:
                    features[col] = 0.0
            features = features[ensemble.feature_names]

        if isinstance(features, pd.DataFrame):
            features = features.fillna(0.0)
            X = features.values.astype(np.float32)
        else:
            X = features.astype(np.float32)

        X = np.nan_to_num(X, nan=0.0)

        if X.ndim == 1:
            X = X.reshape(1, -1)

        proba = ensemble.predict_proba(X)[0]
        # Normalize proba to sum to 1.0
        p_sum = float(np.sum(proba))
        if p_sum > 0:
            proba = proba / p_sum
        else:
            proba = np.array([0.45, 0.25, 0.30])

        pred_class = int(np.argmax(proba))
        result_map = {0: "H", 1: "D", 2: "A"}

        poisson_model = None
        for m, _ in ensemble.models:
            if isinstance(m, PoissonModel):
                poisson_model = m
                break

        home_team = self.team_repo.get_by_id(match.home_team_id)
        away_team = self.team_repo.get_by_id(match.away_team_id)
        home_team_name = home_team.name if home_team else f"Team_{match.home_team_id}"
        away_team_name = away_team.name if away_team else f"Team_{match.away_team_id}"

        score_probs = {}
        home_goals_exp = 0.0
        away_goals_exp = 0.0
        if poisson_model:
            score_probs = poisson_model.predict_score_proba(
                match.home_team_id, match.away_team_id
            )
            exp = poisson_model.predict(pd.DataFrame([{
                "team_home": match.home_team_id,
                "team_away": match.away_team_id,
            }]))[0]
            home_goals_exp = float(exp[0])
            away_goals_exp = float(exp[1])

        over_under = {}
        if poisson_model:
            over_under = poisson_model.predict_over_under(
                match.home_team_id, match.away_team_id
            )

        explanation = self.explainer.explain(ensemble, X, features.columns.tolist())

        market_analysis = None
        if odds:
            model_probs_map = {
                "H": float(proba[0]),
                "D": float(proba[1]),
                "A": float(proba[2]),
            }
            market_analysis = odds.analyze_value(model_probs_map)

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

        resp = self._format_response(prediction, explanation, match_id)
        resp["teams"] = {
            "home": home_team_name,
            "away": away_team_name,
        }
        resp["market_analysis"] = market_analysis
        return resp

    def predict_teams(self, home_team_id: int, away_team_id: int,
                      odds: Optional[BettingOdds] = None,
                      match_date: Optional[date] = None) -> Dict[str, Any]:
        match_date = match_date or date.today()
        features = self.feature_service.generate_features_for_match(
            home_team_id, away_team_id, match_date
        )

        ensemble = self._load_models()
        if ensemble.feature_names and isinstance(features, pd.DataFrame):
            for col in ensemble.feature_names:
                if col not in features.columns:
                    features[col] = 0.0
            features = features[ensemble.feature_names]

        if isinstance(features, pd.DataFrame):
            features = features.fillna(0.0)
            X = features.values.astype(np.float32)
        else:
            X = features.astype(np.float32)

        X = np.nan_to_num(X, nan=0.0)
        if X.ndim == 1:
            X = X.reshape(1, -1)

        proba = ensemble.predict_proba(X)[0]
        p_sum = float(np.sum(proba))
        if p_sum > 0:
            proba = proba / p_sum
        else:
            proba = np.array([0.45, 0.25, 0.30])

        pred_class = int(np.argmax(proba))
        result_map = {0: "H", 1: "D", 2: "A"}

        poisson_model = None
        for m, _ in ensemble.models:
            if isinstance(m, PoissonModel):
                poisson_model = m
                break

        home_team = self.team_repo.get_by_id(home_team_id)
        away_team = self.team_repo.get_by_id(away_team_id)
        home_team_name = home_team.name if home_team else f"Team_{home_team_id}"
        away_team_name = away_team.name if away_team else f"Team_{away_team_id}"

        score_probs = {}
        home_goals_exp = 0.0
        away_goals_exp = 0.0
        if poisson_model:
            score_probs = poisson_model.predict_score_proba(home_team_id, away_team_id)
            exp = poisson_model.predict(pd.DataFrame([{
                "team_home": home_team_id,
                "team_away": away_team_id,
            }]))[0]
            home_goals_exp = float(exp[0])
            away_goals_exp = float(exp[1])

        over_under = {}
        if poisson_model:
            over_under = poisson_model.predict_over_under(home_team_id, away_team_id)

        explanation = self.explainer.explain(ensemble, X, features.columns.tolist())

        market_analysis = None
        if odds:
            model_probs_map = {
                "H": float(proba[0]),
                "D": float(proba[1]),
                "A": float(proba[2]),
            }
            market_analysis = odds.analyze_value(model_probs_map)

        prediction = Prediction(
            match_id=0,
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

        resp = self._format_response(prediction, explanation, 0)
        resp["teams"] = {
            "home": home_team_name,
            "away": away_team_name,
        }
        resp["market_analysis"] = market_analysis
        return resp

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
