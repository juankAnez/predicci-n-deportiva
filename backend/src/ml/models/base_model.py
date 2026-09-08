from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class BaseModel(ABC):
    def __init__(self, model_name: str, version: str = "1.0.0"):
        self.model_name = model_name
        self.version = version
        self.model = None
        self.feature_names: List[str] = []
        self.is_trained = False

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        pass

    def save(self, path: str):
        import joblib
        joblib.dump({
            "model": self.model,
            "model_name": self.model_name,
            "version": self.version,
            "feature_names": self.feature_names,
            "is_trained": self.is_trained,
        }, path)

    def load(self, path: str):
        import joblib
        data = joblib.load(path)
        self.model = data["model"]
        self.model_name = data["model_name"]
        self.version = data["version"]
        self.feature_names = data["feature_names"]
        self.is_trained = data["is_trained"]

    def get_params(self) -> Dict[str, Any]:
        if self.model and hasattr(self.model, "get_params"):
            return self.model.get_params()
        return {}
