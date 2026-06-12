import pytest
import numpy as np

from src.ml.features.feature_pipeline import FeaturePipeline
from src.ml.evaluation.metrics import ModelEvaluator


class TestFeaturePipeline:
    def test_build_features_basic(self):
        pipeline = FeaturePipeline()
        data = {
            "is_neutral": [0],
            "competition_type": ["world_cup"],
            "fifa_ranking_home": [1],
            "fifa_ranking_away": [10],
            "elo_rating_home": [2000],
            "elo_rating_away": [1800],
            "match_importance": [90],
            "is_knockout": [1],
            "is_group": [0],
            "is_friendly": [0],
            "days_rest_home": [5],
            "days_rest_away": [4],
            "temperature": [25],
            "altitude": [500],
            "h2h_games_played": [5],
            "h2h_home_win_rate": [0.6],
            "h2h_avg_total_goals": [2.5],
        }
        import pandas as pd
        df = pd.DataFrame(data)
        features = pipeline.build_features(df)
        assert len(features) > 0
        assert "ranking_diff" in features.columns
        assert "elo_diff" in features.columns
        assert "days_rest_home" in features.columns

    def test_encode_categorical(self):
        pipeline = FeaturePipeline()
        import pandas as pd
        df = pd.DataFrame({"competition_type": ["world_cup", "friendly"]})
        encoded = pipeline.encode_categorical(df)
        assert encoded["competition_type"].dtype in (np.int32, np.int64, int)


class TestModelEvaluator:
    def test_classification_metrics(self):
        evaluator = ModelEvaluator()
        y_true = np.array([0, 1, 2, 0, 1])
        y_pred = np.array([0, 1, 1, 0, 2])
        y_proba = np.array([
            [0.7, 0.2, 0.1],
            [0.1, 0.8, 0.1],
            [0.2, 0.6, 0.2],
            [0.6, 0.3, 0.1],
            [0.1, 0.3, 0.6],
        ])
        metrics = evaluator.evaluate_classification(y_true, y_pred, y_proba)
        assert "accuracy" in metrics
        assert "f1_macro" in metrics
        assert "log_loss" in metrics
        assert "brier_score" in metrics
        assert 0 <= metrics["accuracy"] <= 1

    def test_regression_metrics(self):
        evaluator = ModelEvaluator()
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([1.1, 2.0, 2.8])
        metrics = evaluator.evaluate_regression(y_true, y_pred)
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "r2" in metrics
        assert metrics["mae"] < 0.2

    def test_confusion_matrix(self):
        evaluator = ModelEvaluator()
        y_true = np.array([0, 1, 2, 0, 1])
        y_pred = np.array([0, 1, 2, 1, 0])
        cm = evaluator.confusion_matrix(y_true, y_pred)
        assert len(cm) == 3
        assert len(cm[0]) == 3
