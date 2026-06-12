from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Prediction:
    id: Optional[int] = None
    match_id: Optional[int] = None
    model_version_id: Optional[int] = None
    prediction_date: Optional[datetime] = None

    # Result probabilities
    home_win_probability: float = 0.0
    draw_probability: float = 0.0
    away_win_probability: float = 0.0
    predicted_result: Optional[str] = None

    # Goals
    home_goals_expected: float = 0.0
    away_goals_expected: float = 0.0
    total_goals_expected: float = 0.0
    over_05_probability: float = 0.0
    over_15_probability: float = 0.0
    over_25_probability: float = 0.0
    over_35_probability: float = 0.0
    over_45_probability: float = 0.0
    btts_probability: float = 0.0

    # Score
    exact_score_probabilities: Optional[Dict[str, float]] = None
    most_likely_score: Optional[str] = None
    most_likely_score_prob: float = 0.0

    # Advanced stats
    predicted_home_corners: float = 0.0
    predicted_away_corners: float = 0.0
    predicted_home_shots_ot: float = 0.0
    predicted_away_shots_ot: float = 0.0
    predicted_home_shots: float = 0.0
    predicted_away_shots: float = 0.0
    predicted_home_fouls: float = 0.0
    predicted_away_fouls: float = 0.0
    predicted_home_yellow: float = 0.0
    predicted_away_yellow: float = 0.0
    predicted_home_red: float = 0.0
    predicted_away_red: float = 0.0
    predicted_home_possession: float = 0.0
    predicted_away_possession: float = 0.0
    predicted_home_offsides: float = 0.0
    predicted_away_offsides: float = 0.0
    predicted_home_passes_completed: float = 0.0
    predicted_away_passes_completed: float = 0.0
    predicted_home_passing_accuracy: float = 0.0
    predicted_away_passing_accuracy: float = 0.0
    predicted_home_recoveries: float = 0.0
    predicted_away_recoveries: float = 0.0
    predicted_home_interceptions: float = 0.0
    predicted_away_interceptions: float = 0.0

    # Confidence
    confidence_score: float = 0.0
    model_agreement: float = 0.0
    prediction_std: float = 0.0

    # Explainability
    shap_values: Optional[Dict[str, Any]] = None
    top_features: Optional[List[Dict[str, Any]]] = None
