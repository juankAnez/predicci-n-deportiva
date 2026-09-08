from typing import List, Optional

from src.domain.entities import Prediction
from src.infrastructure.database.models import PredictionModel
from src.infrastructure.database.repositories.base import BaseRepository
import json


class PredictionRepository(BaseRepository[Prediction]):
    model_class = PredictionModel

    def to_domain(self, model: PredictionModel) -> Prediction:
        return Prediction(
            id=model.id,
            match_id=model.match_id,
            model_version_id=model.model_version_id,
            prediction_date=model.prediction_date,
            home_win_probability=model.home_win_probability or 0.0,
            draw_probability=model.draw_probability or 0.0,
            away_win_probability=model.away_win_probability or 0.0,
            predicted_result=model.predicted_result,
            home_goals_expected=model.home_goals_expected or 0.0,
            away_goals_expected=model.away_goals_expected or 0.0,
            total_goals_expected=model.total_goals_expected or 0.0,
            over_05_probability=model.over_05_probability or 0.0,
            over_15_probability=model.over_15_probability or 0.0,
            over_25_probability=model.over_25_probability or 0.0,
            over_35_probability=model.over_35_probability or 0.0,
            over_45_probability=model.over_45_probability or 0.0,
            btts_probability=model.btts_probability or 0.0,
            exact_score_probabilities=json.loads(model.exact_score_probabilities) if model.exact_score_probabilities else None,
            most_likely_score=model.most_likely_score,
            most_likely_score_prob=model.most_likely_score_prob or 0.0,
            predicted_home_corners=model.predicted_home_corners or 0.0,
            predicted_away_corners=model.predicted_away_corners or 0.0,
            predicted_home_shots_ot=model.predicted_home_shots_ot or 0.0,
            predicted_away_shots_ot=model.predicted_away_shots_ot or 0.0,
            predicted_home_shots=model.predicted_home_shots or 0.0,
            predicted_away_shots=model.predicted_away_shots or 0.0,
            predicted_home_fouls=model.predicted_home_fouls or 0.0,
            predicted_away_fouls=model.predicted_away_fouls or 0.0,
            predicted_home_yellow=model.predicted_home_yellow or 0.0,
            predicted_away_yellow=model.predicted_away_yellow or 0.0,
            predicted_home_red=model.predicted_home_red or 0.0,
            predicted_away_red=model.predicted_away_red or 0.0,
            predicted_home_possession=model.predicted_home_possession or 0.0,
            predicted_away_possession=model.predicted_away_possession or 0.0,
            predicted_home_offsides=model.predicted_home_offsides or 0.0,
            predicted_away_offsides=model.predicted_away_offsides or 0.0,
            predicted_home_passes_completed=model.predicted_home_passes_completed or 0.0,
            predicted_away_passes_completed=model.predicted_away_passes_completed or 0.0,
            predicted_home_passing_accuracy=model.predicted_home_passing_accuracy or 0.0,
            predicted_away_passing_accuracy=model.predicted_away_passing_accuracy or 0.0,
            predicted_home_recoveries=model.predicted_home_recoveries or 0.0,
            predicted_away_recoveries=model.predicted_away_recoveries or 0.0,
            predicted_home_interceptions=model.predicted_home_interceptions or 0.0,
            predicted_away_interceptions=model.predicted_away_interceptions or 0.0,
            confidence_score=model.confidence_score or 0.0,
            model_agreement=model.model_agreement or 0.0,
            prediction_std=model.prediction_std or 0.0,
            shap_values=json.loads(model.shap_values) if model.shap_values else None,
            top_features=json.loads(model.top_features) if model.top_features else None,
        )

    def to_model(self, domain: Prediction) -> PredictionModel:
        return PredictionModel(
            match_id=domain.match_id,
            model_version_id=domain.model_version_id,
            home_win_probability=domain.home_win_probability,
            draw_probability=domain.draw_probability,
            away_win_probability=domain.away_win_probability,
            predicted_result=domain.predicted_result,
            home_goals_expected=domain.home_goals_expected,
            away_goals_expected=domain.away_goals_expected,
            total_goals_expected=domain.total_goals_expected,
            over_05_probability=domain.over_05_probability,
            over_15_probability=domain.over_15_probability,
            over_25_probability=domain.over_25_probability,
            over_35_probability=domain.over_35_probability,
            over_45_probability=domain.over_45_probability,
            btts_probability=domain.btts_probability,
            exact_score_probabilities=json.dumps(domain.exact_score_probabilities) if domain.exact_score_probabilities else None,
            most_likely_score=domain.most_likely_score,
            most_likely_score_prob=domain.most_likely_score_prob,
            predicted_home_corners=domain.predicted_home_corners,
            predicted_away_corners=domain.predicted_away_corners,
            predicted_home_shots_ot=domain.predicted_home_shots_ot,
            predicted_away_shots_ot=domain.predicted_away_shots_ot,
            predicted_home_shots=domain.predicted_home_shots,
            predicted_away_shots=domain.predicted_away_shots,
            predicted_home_fouls=domain.predicted_home_fouls,
            predicted_away_fouls=domain.predicted_away_fouls,
            predicted_home_yellow=domain.predicted_home_yellow,
            predicted_away_yellow=domain.predicted_away_yellow,
            predicted_home_red=domain.predicted_home_red,
            predicted_away_red=domain.predicted_away_red,
            predicted_home_possession=domain.predicted_home_possession,
            predicted_away_possession=domain.predicted_away_possession,
            predicted_home_offsides=domain.predicted_home_offsides,
            predicted_away_offsides=domain.predicted_away_offsides,
            predicted_home_passes_completed=domain.predicted_home_passes_completed,
            predicted_away_passes_completed=domain.predicted_away_passes_completed,
            predicted_home_passing_accuracy=domain.predicted_home_passing_accuracy,
            predicted_away_passing_accuracy=domain.predicted_away_passing_accuracy,
            predicted_home_recoveries=domain.predicted_home_recoveries,
            predicted_away_recoveries=domain.predicted_away_recoveries,
            predicted_home_interceptions=domain.predicted_home_interceptions,
            predicted_away_interceptions=domain.predicted_away_interceptions,
            confidence_score=domain.confidence_score,
            model_agreement=domain.model_agreement,
            prediction_std=domain.prediction_std,
            shap_values=json.dumps(domain.shap_values) if domain.shap_values else None,
            top_features=json.dumps(domain.top_features) if domain.top_features else None,
        )

    def get_by_match(self, match_id: int) -> Optional[Prediction]:
        model = (
            self.db.query(PredictionModel)
            .filter(PredictionModel.match_id == match_id)
            .order_by(PredictionModel.prediction_date.desc())
            .first()
        )
        return self.to_domain(model) if model else None

    def get_latest_predictions(self, limit: int = 20) -> List[Prediction]:
        models = (
            self.db.query(PredictionModel)
            .order_by(PredictionModel.prediction_date.desc())
            .limit(limit)
            .all()
        )
        return [self.to_domain(m) for m in models]
