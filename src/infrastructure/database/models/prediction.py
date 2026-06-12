from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, func, Index

from src.infrastructure.database.models.base import Base


class PredictionModel(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    model_version_id = Column(Integer, ForeignKey("model_versions.id"))
    prediction_date = Column(DateTime, default=func.now())

    home_win_probability = Column(Float)
    draw_probability = Column(Float)
    away_win_probability = Column(Float)
    predicted_result = Column(String(10))

    home_goals_expected = Column(Float)
    away_goals_expected = Column(Float)
    total_goals_expected = Column(Float)
    over_05_probability = Column(Float)
    over_15_probability = Column(Float)
    over_25_probability = Column(Float)
    over_35_probability = Column(Float)
    over_45_probability = Column(Float)
    btts_probability = Column(Float)

    exact_score_probabilities = Column(String)  # JSON
    most_likely_score = Column(String(10))
    most_likely_score_prob = Column(Float)

    predicted_home_corners = Column(Float)
    predicted_away_corners = Column(Float)
    predicted_home_shots_ot = Column(Float)
    predicted_away_shots_ot = Column(Float)
    predicted_home_shots = Column(Float)
    predicted_away_shots = Column(Float)
    predicted_home_fouls = Column(Float)
    predicted_away_fouls = Column(Float)
    predicted_home_yellow = Column(Float)
    predicted_away_yellow = Column(Float)
    predicted_home_red = Column(Float)
    predicted_away_red = Column(Float)
    predicted_home_possession = Column(Float)
    predicted_away_possession = Column(Float)
    predicted_home_offsides = Column(Float)
    predicted_away_offsides = Column(Float)
    predicted_home_passes_completed = Column(Float)
    predicted_away_passes_completed = Column(Float)
    predicted_home_passing_accuracy = Column(Float)
    predicted_away_passing_accuracy = Column(Float)
    predicted_home_recoveries = Column(Float)
    predicted_away_recoveries = Column(Float)
    predicted_home_interceptions = Column(Float)
    predicted_away_interceptions = Column(Float)

    confidence_score = Column(Float)
    model_agreement = Column(Float)
    prediction_std = Column(Float)

    shap_values = Column(String)  # JSON
    top_features = Column(String)  # JSON

    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_predictions_match", "match_id"),
        Index("idx_predictions_model", "model_version_id"),
    )
