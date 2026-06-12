from typing import Any, Dict, List, Optional

from src.ml.explainability.shap_explainer import SHAPExplainer


class ExplainabilityService:
    def __init__(self):
        self.explainer = SHAPExplainer()

    def explain_prediction(self, shap_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "global_importance": shap_data.get("feature_importance", {}),
            "top_features": shap_data.get("top_features", []),
            "method": shap_data.get("method", "feature_importance"),
            "summary": self.explainer.format_explanation(shap_data),
            "base_value": shap_data.get("base_value", 0.0),
        }

    def get_feature_breakdown(self, top_features: List[Dict]) -> List[Dict[str, Any]]:
        return [
            {
                "name": f["name"],
                "importance": f["importance"],
                "direction": "positive" if f["importance"] > 0 else "negative",
            }
            for f in top_features
        ]
