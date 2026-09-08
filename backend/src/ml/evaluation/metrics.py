import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, log_loss, brier_score_loss, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)


class ModelEvaluator:
    def evaluate_classification(self, y_true: np.ndarray, y_pred: np.ndarray,
                                y_proba: np.ndarray) -> Dict[str, float]:
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
            "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
            "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
            "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        }

        try:
            metrics["log_loss"] = float(log_loss(y_true, y_proba))
        except Exception:
            metrics["log_loss"] = 1.0

        try:
            if y_proba.shape[1] == 3:
                metrics["roc_auc_ovr"] = float(roc_auc_score(y_true, y_proba, multi_class="ovr"))
        except Exception:
            metrics["roc_auc_ovr"] = 0.5

        # Brier Score (para la clase positiva, local)
        try:
            brier = 0
            for i in range(3):
                y_bin = (y_true == i).astype(int)
                brier += brier_score_loss(y_bin, y_proba[:, i])
            metrics["brier_score"] = float(brier / 3)
        except Exception:
            metrics["brier_score"] = 0.25

        return metrics

    def evaluate_regression(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        metrics = {
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "mse": float(mean_squared_error(y_true, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        }
        try:
            metrics["r2"] = float(r2_score(y_true, y_pred))
        except Exception:
            metrics["r2"] = 0.0
        return metrics

    def confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray) -> List[List[int]]:
        cm = confusion_matrix(y_true, y_pred)
        return cm.tolist()
