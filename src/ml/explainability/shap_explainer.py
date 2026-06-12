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
        try:
            import shap
            if hasattr(model.model, "predict_proba"):
                pred_fn = model.model.predict_proba
            else:
                pred_fn = model.model.predict

            if isinstance(X, pd.DataFrame):
                X_array = X.values
            else:
                X_array = X
                X = pd.DataFrame(X, columns=feature_names)

            if len(X_array.shape) == 1:
                X_array = X_array.reshape(1, -1)
                X = pd.DataFrame(X_array, columns=feature_names)

            if hasattr(model.model, "feature_importances_") or hasattr(model.model, "estimators_"):
                explainer = shap.TreeExplainer(model.model)
                shap_values = explainer.shap_values(X_array)

                if isinstance(shap_values, list):
                    shap_summary = []
                    for i, sv in enumerate(shap_values):
                        if len(sv.shape) > 1:
                            feature_contrib = {
                                str(feature_names[j]): float(sv[0, j])
                                for j in range(min(len(feature_names), sv.shape[1]))
                            }
                            shap_summary.append(feature_contrib)
                        else:
                            shap_summary.append({f"class_{i}": float(np.sum(sv))})
                else:
                    if len(shap_values.shape) == 2:
                        feature_contrib = {
                            str(feature_names[j]): float(shap_values[0, j])
                            for j in range(min(len(feature_names), shap_values.shape[1]))
                        }
                        shap_summary = [feature_contrib]
                    else:
                        shap_summary = [{"shap_value": float(np.sum(shap_values[0]))}]

                base_value = float(explainer.expected_value) if not isinstance(explainer.expected_value, list) else float(explainer.expected_value[0])

                feature_importance = {}
                if isinstance(shap_values, list):
                    for sv in shap_values:
                        for j in range(min(len(feature_names), sv.shape[1])):
                            name = feature_names[j]
                            feature_importance[name] = feature_importance.get(name, 0) + float(np.abs(sv[:, j]).mean())
                else:
                    for j in range(min(len(feature_names), shap_values.shape[1])):
                        feature_importance[str(feature_names[j])] = float(np.abs(shap_values[:, j]).mean())

                sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)

                return {
                    "shap_values": shap_summary,
                    "base_value": base_value,
                    "feature_importance": feature_importance,
                    "top_features": [
                        {"name": name, "importance": round(imp, 4)}
                        for name, imp in sorted_features[:10]
                    ],
                    "method": "shap_tree",
                }

        except ImportError:
            return self._fallback_explanation(model, feature_names)
        except Exception as e:
            return self._fallback_explanation(model, feature_names, error=str(e))

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
