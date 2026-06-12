import numpy as np
from typing import Any, Dict, List, Optional, Tuple

from src.ml.models.base_model import BaseModel


class NeuralNetworkModel(BaseModel):
    def __init__(self, version: str = "1.0.0", task: str = "classification"):
        super().__init__("neural_network", version)
        self.task = task
        self.model = None
        self._use_tf = False

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        try:
            import tensorflow as tf
            from tensorflow import keras
            self._use_tf = True

            n_features = X.shape[1]
            n_classes = len(np.unique(y)) if self.task == "classification" else y.shape[1] if y.ndim > 1 else 1

            model = keras.Sequential([
                keras.layers.Dense(256, activation="relu", input_shape=(n_features,)),
                keras.layers.BatchNormalization(),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(128, activation="relu"),
                keras.layers.BatchNormalization(),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(64, activation="relu"),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(32, activation="relu"),
                keras.layers.Dropout(0.1),
            ])

            if self.task == "classification":
                model.add(keras.layers.Dense(n_classes, activation="softmax"))
                model.compile(
                    optimizer=keras.optimizers.Adam(learning_rate=0.001),
                    loss="sparse_categorical_crossentropy",
                    metrics=["accuracy"],
                )
            else:
                model.add(keras.layers.Dense(n_classes))
                model.compile(
                    optimizer=keras.optimizers.Adam(learning_rate=0.001),
                    loss="mse",
                    metrics=["mae"],
                )

            early_stop = keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=20, restore_best_weights=True
            )

            validation_split = kwargs.get("validation_split", 0.2)
            epochs = kwargs.get("epochs", 200)
            batch_size = kwargs.get("batch_size", 32)

            history = model.fit(
                X, y,
                validation_split=validation_split,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=[early_stop],
                verbose=0,
            )

            self.model = model
            self.is_trained = True

            return {
                "epochs_trained": len(history.history["loss"]),
                "final_loss": float(history.history["loss"][-1]),
                "final_val_loss": float(history.history["val_loss"][-1]),
            }

        except ImportError:
            print("TensorFlow no disponible. Usando MLP de scikit-learn.")
            from sklearn.neural_network import MLPClassifier, MLPRegressor

            if self.task == "classification":
                self.model = MLPClassifier(
                    hidden_layer_sizes=(256, 128, 64, 32),
                    activation="relu",
                    alpha=0.001,
                    batch_size=32,
                    learning_rate_init=0.001,
                    max_iter=200,
                    random_state=42,
                    early_stopping=True,
                )
            else:
                self.model = MLPRegressor(
                    hidden_layer_sizes=(256, 128, 64, 32),
                    activation="relu",
                    alpha=0.001,
                    batch_size=32,
                    learning_rate_init=0.001,
                    max_iter=200,
                    random_state=42,
                    early_stopping=True,
                )
            self.model.fit(X, y)
            self.is_trained = True
            return {"n_iter": self.model.n_iter_, "loss": float(self.model.loss_)}

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self._use_tf:
            preds = self.model.predict(X, verbose=0)
            if self.task == "classification":
                return np.argmax(preds, axis=1)
            return preds.flatten()
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self._use_tf and self.task == "classification":
            return self.model.predict(X, verbose=0)
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        return self.model.predict(X)

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        return None
