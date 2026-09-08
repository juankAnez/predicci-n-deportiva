from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.config import settings
from src.ml.models.base_model import BaseModel


class SHAPExplainer:
    def __init__(self):
        self.explainers = {}

    def explain(self, model: BaseModel, X: np.ndarray,
                feature_names: List[str]) -> Dict[str, Any]:
        # Fast & robust feature importance aggregation from ensemble models
        if hasattr(model, "models") and model.models:
            combined_importance = {}
            total_w = 0.0
            for submodel, weight in model.models:
                imp = submodel.get_feature_importance()
                if imp:
                    total_w += weight
                    for k, v in imp.items():
                        combined_importance[k] = combined_importance.get(k, 0.0) + (float(v) * weight)

            if total_w > 0 and combined_importance:
                for k in combined_importance:
                    combined_importance[k] /= total_w
                sorted_features = sorted(combined_importance.items(), key=lambda x: x[1], reverse=True)
                return {
                    "shap_values": [],
                    "base_value": 0.33,
                    "feature_importance": combined_importance,
                    "top_features": [
                        {"name": name, "importance": round(float(imp), 4)}
                        for name, imp in sorted_features[:10]
                    ],
                    "method": "ensemble_feature_importance",
                }

        importance = model.get_feature_importance()
        if importance:
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            return {
                "shap_values": [],
                "base_value": 0.33,
                "feature_importance": importance,
                "top_features": [
                    {"name": name, "importance": round(float(imp), 4)}
                    for name, imp in sorted_features[:10]
                ],
                "method": "model_feature_importance",
            }

        return self._fallback_explanation(model, feature_names)

    def _fallback_explanation(self, model: BaseModel, feature_names: List[str],
                               error: Optional[str] = None) -> Dict[str, Any]:
        importance = model.get_feature_importance()
        if importance:
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            return {
                "shap_values": [],
                "base_value": 0.0,
                "feature_importance": importance,
                "top_features": [
                    {"name": name, "importance": round(imp, 4)}
                    for name, imp in sorted_features[:10]
                ],
                "method": "feature_importance",
                "error": error,
            }

        return {
            "shap_values": [],
            "base_value": 0.0,
            "feature_importance": {},
            "top_features": [],
            "method": "none",
            "error": error or "No SHAP disponible",
        }

    def format_explanation(self, explanation: Dict[str, Any]) -> str:
        lines = ["**Explicación de la predicción:**"]
        for feat in explanation.get("top_features", [])[:5]:
            lines.append(f"- {feat['name']}: {feat['importance']:.3f}")
        return "\n".join(lines)
