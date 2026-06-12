import numpy as np
from typing import Any, Dict, List, Optional
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from src.ml.models.base_model import BaseModel


class RandomForestModel(BaseModel):
    def __init__(self, version: str = "1.0.0", params: Optional[Dict] = None, task: str = "classification"):
        super().__init__("random_forest", version)
        self.task = task
        self.params = params or {
            "n_estimators": 500,
            "max_depth": 20,
            "min_samples_split": 10,
            "min_samples_leaf": 5,
            "max_features": "sqrt",
            "bootstrap": True,
            "random_state": 42,
            "n_jobs": -1,
        }
        if task == "classification":
            self.model = RandomForestClassifier(**self.params)
        else:
            self.model = RandomForestRegressor(**self.params)

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        self.model.fit(X, y)
        self.is_trained = True
        return {"n_features": X.shape[1], "oob_score": getattr(self.model, "oob_score_", None)}

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.task == "classification":
            return self.model.predict_proba(X)
        return self.model.predict(X)

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        if not self.is_trained:
            return None
        importance = self.model.feature_importances_
        if self.feature_names:
            return dict(zip(self.feature_names, importance))
        return {f"feature_{i}": v for i, v in enumerate(importance)}
