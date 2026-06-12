import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
import xgboost as xgb

from src.ml.models.base_model import BaseModel


class XGBoostModel(BaseModel):
    def __init__(self, version: str = "1.0.0", params: Optional[Dict] = None):
        super().__init__("xgboost", version)
        self.params = params or {
            "n_estimators": 1000,
            "max_depth": 6,
            "learning_rate": 0.01,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "gamma": 0.1,
            "reg_lambda": 1.0,
            "reg_alpha": 0.1,
            "random_state": 42,
            "eval_metric": ["mlogloss"],
        }
        self.model = xgb.XGBClassifier(
            objective="multi:softprob",
            num_class=3,
            **self.params,
        )

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        eval_set = kwargs.get("eval_set")
        early_stopping = kwargs.get("early_stopping_rounds", 50)
        verbose = kwargs.get("verbose", False)

        fit_params = {
            "eval_set": eval_set or [(X, y)],
            "early_stopping_rounds": early_stopping,
            "verbose": verbose,
        }

        self.model.fit(X, y, **fit_params)
        self.is_trained = True

        result = self.model.evals_result() if hasattr(self.model, "evals_result") else {}
        return {
            "best_iteration": self.model.best_iteration if hasattr(self.model, "best_iteration") else None,
            "evals_result": result,
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        if not self.is_trained:
            return None
        importance = self.model.feature_importances_
        if self.feature_names:
            return dict(zip(self.feature_names, importance))
        return {f"feature_{i}": v for i, v in enumerate(importance)}
