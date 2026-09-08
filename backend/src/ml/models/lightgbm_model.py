import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
import lightgbm as lgb
from sklearn.multioutput import MultiOutputRegressor

from src.ml.models.base_model import BaseModel


class LightGBMModel(BaseModel):
    def __init__(self, version: str = "1.0.0", params: Optional[Dict] = None):
        super().__init__("lightgbm", version)
        self.params = params or {
            "n_estimators": 1000,
            "max_depth": -1,
            "num_leaves": 31,
            "learning_rate": 0.01,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_lambda": 0.1,
            "reg_alpha": 0.1,
            "min_child_samples": 20,
            "random_state": 42,
            "verbose": -1,
        }
        self.model = lgb.LGBMRegressor(**self.params)

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        if y.ndim > 1 and y.shape[1] > 1:
            self.model = MultiOutputRegressor(lgb.LGBMRegressor(**self.params))
            self.model.fit(X, y)
        else:
            self.model.fit(X, y)
        self.is_trained = True
        return {"n_features": X.shape[1], "n_targets": y.shape[1] if y.ndim > 1 else 1}

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        exp_goals = self.model.predict(X)
        if exp_goals.ndim > 1 and exp_goals.shape[1] >= 2:
            from scipy.stats import poisson
            results = []
            for row in exp_goals:
                eh, ea = max(float(row[0]), 0.1), max(float(row[1]), 0.1)
                hp = np.array([poisson.pmf(g, eh) for g in range(11)])
                ap = np.array([poisson.pmf(g, ea) for g in range(11)])
                mat = np.outer(hp, ap)
                hw = float(np.sum(np.tril(mat, k=-1)))
                dr = float(np.sum(np.diag(mat)))
                aw = float(np.sum(np.triu(mat, k=1)))
                tot = hw + dr + aw
                results.append([hw / tot, dr / tot, aw / tot] if tot > 0 else [0.45, 0.25, 0.30])
            return np.array(results)
        return exp_goals

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        if not self.is_trained:
            return None
        if hasattr(self.model, "estimators_"):
            importances = []
            for est in self.model.estimators_:
                importances.append(est.feature_importances_)
            importance = np.mean(importances, axis=0)
        else:
            importance = self.model.feature_importances_

        if self.feature_names:
            return dict(zip(self.feature_names, importance))
        return {f"feature_{i}": v for i, v in enumerate(importance)}
