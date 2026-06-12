import pytest
import numpy as np
import pandas as pd

from src.ml.models.poisson_model import PoissonModel
from src.ml.models.xgboost_model import XGBoostModel
from src.ml.models.lightgbm_model import LightGBMModel
from src.ml.models.random_forest_model import RandomForestModel


class TestPoissonModel:
    def test_initialization(self):
        model = PoissonModel()
        assert model.model_name == "poisson"
        assert model.is_trained is False

    def test_training(self):
        model = PoissonModel()
        X = pd.DataFrame({
            "team_home": ["A", "A", "B", "B"],
            "team_away": ["B", "C", "A", "C"],
        })
        y = pd.DataFrame({
            "home_goals": [2, 1, 0, 2],
            "away_goals": [1, 0, 3, 1],
        })
        result = model.train(X, y)
        assert model.is_trained is True
        assert "league_mean" in result
        assert result["league_mean"] > 0

    def test_predict(self):
        model = PoissonModel()
        X = pd.DataFrame({
            "team_home": ["A", "A"],
            "team_away": ["B", "C"],
        })
        y = pd.DataFrame({
            "home_goals": [2, 1],
            "away_goals": [1, 0],
        })
        model.train(X, y)
        pred = model.predict(X)
        assert pred.shape == (2, 2)
        assert pred[0, 0] > 0  # home goals expected positive

    def test_predict_proba(self):
        model = PoissonModel()
        X = pd.DataFrame({
            "team_home": ["A", "A"],
            "team_away": ["B", "C"],
        })
        y = pd.DataFrame({
            "home_goals": [2, 1],
            "away_goals": [1, 0],
        })
        model.train(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (2, 3)
        # Probabilities should sum to ~1 for each row
        for row in proba:
            assert abs(row.sum() - 1.0) < 0.1

    def test_predict_score_proba(self):
        model = PoissonModel()
        X = pd.DataFrame({
            "team_home": ["A", "A"],
            "team_away": ["B", "C"],
        })
        y = pd.DataFrame({
            "home_goals": [2, 1],
            "away_goals": [1, 0],
        })
        model.train(X, y)
        scores = model.predict_score_proba("A", "B")
        assert len(scores) > 0
        assert "0-0" in scores or "1-0" in scores or "2-1" in scores

    def test_predict_over_under(self):
        model = PoissonModel()
        X = pd.DataFrame({
            "team_home": ["A", "A"],
            "team_away": ["B", "C"],
        })
        y = pd.DataFrame({
            "home_goals": [2, 1],
            "away_goals": [1, 0],
        })
        model.train(X, y)
        ou = model.predict_over_under("A", "B")
        assert "over_2.5" in ou
        assert "under_2.5" in ou
        assert 0 <= ou["over_2.5"] <= 1

    def test_get_feature_importance(self):
        model = PoissonModel()
        X = pd.DataFrame({
            "team_home": ["A", "A"],
            "team_away": ["B", "C"],
        })
        y = pd.DataFrame({
            "home_goals": [2, 1],
            "away_goals": [1, 0],
        })
        model.train(X, y)
        importance = model.get_feature_importance()
        assert "home_advantage" in importance
        assert "league_mean" in importance


class TestXGBoostModel:
    def test_initialization(self):
        model = XGBoostModel()
        assert model.model_name == "xgboost"
        assert model.is_trained is False

    def test_train_and_predict(self):
        model = XGBoostModel(params={"n_estimators": 10, "max_depth": 2})
        X = np.random.rand(20, 5).astype(np.float32)
        y = np.random.randint(0, 3, 20)
        result = model.train(X, y)
        assert model.is_trained is True
        pred = model.predict(X)
        assert len(pred) == 20

    def test_predict_proba(self):
        model = XGBoostModel(params={"n_estimators": 10, "max_depth": 2})
        X = np.random.rand(20, 5).astype(np.float32)
        y = np.random.randint(0, 3, 20)
        model.train(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (20, 3)

    def test_feature_importance(self):
        model = XGBoostModel(params={"n_estimators": 10, "max_depth": 2})
        X = np.random.rand(20, 5).astype(np.float32)
        y = np.random.randint(0, 3, 20)
        model.feature_names = [f"feat_{i}" for i in range(5)]
        model.train(X, y)
        importance = model.get_feature_importance()
        assert importance is not None
        assert len(importance) == 5


class TestLightGBMModel:
    def test_initialization(self):
        model = LightGBMModel()
        assert model.model_name == "lightgbm"

    def test_train_and_predict(self):
        model = LightGBMModel(params={"n_estimators": 10, "num_leaves": 5, "verbose": -1})
        X = np.random.rand(20, 5).astype(np.float32)
        y = np.random.rand(20)
        model.train(X, y)
        pred = model.predict(X)
        assert len(pred) == 20


class TestRandomForestModel:
    def test_initialization(self):
        model = RandomForestModel(params={"n_estimators": 10, "max_depth": 3})
        assert model.model_name == "random_forest"

    def test_train_and_predict(self):
        model = RandomForestModel(params={"n_estimators": 10, "max_depth": 3})
        X = np.random.rand(20, 5).astype(np.float32)
        y = np.random.randint(0, 3, 20)
        model.train(X, y)
        pred = model.predict(X)
        assert len(pred) == 20
