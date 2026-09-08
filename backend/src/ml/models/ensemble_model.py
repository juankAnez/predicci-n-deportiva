import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from sklearn.linear_model import LogisticRegression

from src.ml.models.base_model import BaseModel


class EnsembleModel(BaseModel):
    def __init__(self, version: str = "1.0.0", method: str = "weighted_average"):
        super().__init__("ensemble", version)
        self.method = method
        self.models: List[Tuple[BaseModel, float]] = []  # (model, weight)
        self.meta_learner = None

    def add_model(self, model: BaseModel, weight: float = 1.0):
        self.models.append((model, weight))

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        if self.method == "stacking":
            n_models = len(self.models)
            n_samples = X.shape[0]
            n_classes = len(np.unique(y))

            meta_features = np.zeros((n_samples, n_models * n_classes))
            for i, (model, _) in enumerate(self.models):
                if hasattr(model, "predict_proba"):
                    proba = model.predict_proba(X)
                    if proba.ndim == 2 and proba.shape[1] <= 3:
                        meta_features[:, i * n_classes:(i + 1) * n_classes] = proba
                    else:
                        meta_features[:, i] = proba.flatten()[:n_samples]

            self.meta_learner = LogisticRegression(multi_class="multinomial", max_iter=1000)
            self.meta_learner.fit(meta_features, y)
        self.is_trained = True
        return {"method": self.method, "n_models": len(self.models)}

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.method == "stacking" and self.meta_learner:
            meta_features = self._get_meta_features(X)
            return self.meta_learner.predict(meta_features)
        proba = self.predict_proba(X)
        return np.argmax(proba, axis=1)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.method == "stacking" and self.meta_learner:
            meta_features = self._get_meta_features(X)
            return self.meta_learner.predict_proba(meta_features)

        all_probas = []
        total_weight = sum(w for _, w in self.models)

        for model, weight in self.models:
            proba = model.predict_proba(X)
            if len(all_probas) > 0 and proba.shape != all_probas[0].shape:
                continue
            all_probas.append(proba * (weight / total_weight))

        if all_probas:
            return np.sum(all_probas, axis=0)
        return np.array([])

    def _get_meta_features(self, X: np.ndarray) -> np.ndarray:
        n_models = len(self.models)
        n_samples = X.shape[0]
        n_classes = 3
        meta_features = np.zeros((n_samples, n_models * n_classes))

        for i, (model, _) in enumerate(self.models):
            proba = model.predict_proba(X)
            if proba.ndim == 2 and proba.shape[1] == n_classes:
                meta_features[:, i * n_classes:(i + 1) * n_classes] = proba
            else:
                meta_features[:, i * n_classes] = proba.flatten()[:n_samples]

        return meta_features

    def get_weights(self) -> Dict[str, float]:
        return {m.model_name: w for m, w in self.models}

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        if self.meta_learner:
            return {f"model_{i}": float(c) for i, c in enumerate(self.meta_learner.coef_[0])}
        return None

    def save(self, path: str):
        import joblib
        joblib.dump({
            "models": self.models,
            "method": self.method,
            "meta_learner": self.meta_learner,
            "model_name": self.model_name,
            "version": self.version,
            "feature_names": self.feature_names,
            "is_trained": self.is_trained,
        }, path)

    def load(self, path: str):
        import joblib
        data = joblib.load(path)
        self.models = data.get("models", [])
        self.method = data.get("method", "weighted_average")
        self.meta_learner = data.get("meta_learner")
        self.model_name = data.get("model_name", "ensemble")
        self.version = data.get("version", "1.0.0")
        self.feature_names = data.get("feature_names", [])
        self.is_trained = data.get("is_trained", False)
