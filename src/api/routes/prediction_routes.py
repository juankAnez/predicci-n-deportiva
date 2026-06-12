from flask import Blueprint, jsonify, request

from src.application.services.prediction_service import PredictionService
from src.infrastructure.database.repositories import PredictionRepository

prediction_bp = Blueprint("predictions", __name__)
prediction_service = PredictionService()
prediction_repo = PredictionRepository()


@prediction_bp.route("/<int:match_id>", methods=["GET"])
def get_prediction(match_id: int):
    try:
        result = prediction_service.predict_match(match_id)
        return jsonify({"status": "success", "data": result})
    except ValueError as e:
        return jsonify({"status": "error", "error": str(e)}), 404
    except FileNotFoundError as e:
        return jsonify({"status": "error", "error": str(e)}), 503


@prediction_bp.route("/upcoming", methods=["GET"])
def get_upcoming_predictions():
    from src.infrastructure.database.repositories import MatchRepository
    match_repo = MatchRepository()
    upcoming = match_repo.get_upcoming(limit=20)
    results = []
    for match in upcoming:
        try:
            pred = prediction_repo.get_by_match(match.id)
            if pred:
                results.append({
                    "match_id": match.id,
                    "home_team_id": match.home_team_id,
                    "away_team_id": match.away_team_id,
                    "match_date": match.match_date.isoformat() if match.match_date else None,
                    "home_win": round(pred.home_win_probability * 100, 2),
                    "draw": round(pred.draw_probability * 100, 2),
                    "away_win": round(pred.away_win_probability * 100, 2),
                    "predicted": pred.predicted_result,
                    "confidence": round(pred.confidence_score, 1),
                })
        except Exception:
            results.append({
                "match_id": match.id,
                "home_team_id": match.home_team_id,
                "away_team_id": match.away_team_id,
                "match_date": match.match_date.isoformat() if match.match_date else None,
                "status": "pending",
            })
    return jsonify({"status": "success", "data": results})


@prediction_bp.route("/history", methods=["GET"])
def get_prediction_history():
    predictions = prediction_repo.get_latest_predictions(limit=50)
    return jsonify({
        "status": "success",
        "data": [
            {
                "match_id": p.match_id,
                "predicted": p.predicted_result,
                "home_win": round(p.home_win_probability * 100, 2),
                "draw": round(p.draw_probability * 100, 2),
                "away_win": round(p.away_win_probability * 100, 2),
                "confidence": round(p.confidence_score, 1),
                "date": p.prediction_date.isoformat() if p.prediction_date else None,
            }
            for p in predictions
        ],
    })
