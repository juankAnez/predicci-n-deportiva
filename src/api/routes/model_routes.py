from flask import Blueprint, jsonify, request

from src.infrastructure.database.models import ModelVersionModel
from src.infrastructure.database.connection import db_session
from src.ml.training.trainer import ModelTrainer

model_bp = Blueprint("models", __name__)


@model_bp.route("", methods=["GET"])
def list_models():
    db = db_session()
    models = db.query(ModelVersionModel).order_by(ModelVersionModel.training_date.desc()).all()
    db.close()

    return jsonify({
        "status": "success",
        "data": [
            {
                "id": m.id,
                "model_name": m.model_name,
                "version": m.version,
                "model_type": m.model_type,
                "status": m.status,
                "is_ensemble": m.is_ensemble,
                "feature_count": m.feature_count,
                "training_date": m.training_date.isoformat() if m.training_date else None,
                "f1_score": m.f1_score,
                "log_loss": m.log_loss,
                "accuracy": m.accuracy,
            }
            for m in models
        ],
    })


@model_bp.route("/<int:model_id>", methods=["GET"])
def get_model(model_id: int):
    db = db_session()
    model = db.query(ModelVersionModel).filter(ModelVersionModel.id == model_id).first()
    db.close()

    if not model:
        return jsonify({"status": "error", "error": "Modelo no encontrado"}), 404

    return jsonify({
        "status": "success",
        "data": {
            "id": model.id,
            "model_name": model.model_name,
            "version": model.version,
            "model_type": model.model_type,
            "parameters": model.parameters,
            "metrics": model.metrics,
            "training_date": model.training_date.isoformat() if model.training_date else None,
            "feature_count": model.feature_count,
            "status": model.status,
            "is_ensemble": model.is_ensemble,
            "accuracy": model.accuracy,
            "f1_score": model.f1_score,
            "log_loss": model.log_loss,
            "brier_score": model.brier_score,
            "roc_auc": model.roc_auc,
        },
    })


@model_bp.route("/metrics", methods=["GET"])
def model_metrics():
    db = db_session()
    active_models = db.query(ModelVersionModel).filter(
        ModelVersionModel.status == "active",
        ModelVersionModel.model_name != "ensemble",
    ).all()
    db.close()

    comparison = {}
    for m in active_models:
        if m.model_name not in comparison:
            comparison[m.model_name] = {
                "accuracy": m.accuracy,
                "f1_score": m.f1_score,
                "log_loss": m.log_loss,
                "brier_score": m.brier_score,
                "roc_auc": m.roc_auc,
                "training_date": m.training_date.isoformat() if m.training_date else None,
            }

    return jsonify({
        "status": "success",
        "data": comparison,
    })


@model_bp.route("/train", methods=["POST"])
def train_models():
    try:
        trainer = ModelTrainer()
        from src.infrastructure.database.repositories import MatchRepository
        import pandas as pd

        match_repo = MatchRepository()
        matches = match_repo.get_all()

        if not matches:
            return jsonify({"status": "error", "error": "No hay datos de partidos para entrenar"}), 400

        match_data = [
            {
                "home_team_id": m.home_team_id,
                "away_team_id": m.away_team_id,
                "home_goals": m.home_score or 0,
                "away_goals": m.away_score or 0,
                "match_date": m.match_date,
                "result": (
                    "H" if (m.home_score or 0) > (m.away_score or 0)
                    else "A" if (m.away_score or 0) > (m.home_score or 0)
                    else "D"
                ) if m.home_score is not None else None,
            }
            for m in matches if m.home_score is not None
        ]

        df = pd.DataFrame(match_data)
        X, y_goals, y_result = trainer.prepare_data(df)
        models = trainer.train_models(X, y_result, y_goals)
        trainer.save_models(models)

        return jsonify({
            "status": "success",
            "data": {
                "message": "Entrenamiento completado",
                "models": list(models.keys()),
                "n_samples": len(df),
            },
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
