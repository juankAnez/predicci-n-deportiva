from flask import Blueprint, jsonify, request

from src.application.services.prediction_service import PredictionService
from src.infrastructure.database.repositories import PredictionRepository

prediction_bp = Blueprint("predictions", __name__)
prediction_service = PredictionService()
prediction_repo = PredictionRepository()


def _parse_benched_ids(val):
    if not val:
        return []
    if isinstance(val, list):
        return [int(x) for x in val if str(x).isdigit()]
    if isinstance(val, str):
        return [int(x.strip()) for x in val.split(",") if x.strip().isdigit()]
    return []


@prediction_bp.route("/<int:match_id>", methods=["GET"])
def get_prediction(match_id: int):
    try:
        h_odds = request.args.get("h_odds", type=float)
        d_odds = request.args.get("d_odds", type=float)
        a_odds = request.args.get("a_odds", type=float)
        benched_home = _parse_benched_ids(request.args.get("benched_home"))
        benched_away = _parse_benched_ids(request.args.get("benched_away"))
        odds = None
        if h_odds and d_odds and a_odds:
            from src.domain.value_objects.betting_market import BettingOdds
            odds = BettingOdds(home_win=h_odds, draw=d_odds, away_win=a_odds)

        result = prediction_service.predict_match(
            match_id, odds=odds, benched_home=benched_home, benched_away=benched_away
        )
        return jsonify({"status": "success", "data": result})
    except ValueError as e:
        return jsonify({"status": "error", "error": str(e)}), 404
    except FileNotFoundError as e:
        return jsonify({"status": "error", "error": str(e)}), 503


@prediction_bp.route("/simulate", methods=["GET", "POST"])
def simulate_match():
    try:
        if request.method == "POST":
            payload = request.get_json() or {}
            home_team_id = int(payload.get("home_team_id", 0))
            away_team_id = int(payload.get("away_team_id", 0))
            h_odds = payload.get("h_odds")
            d_odds = payload.get("d_odds")
            a_odds = payload.get("a_odds")
            benched_home = _parse_benched_ids(payload.get("benched_home"))
            benched_away = _parse_benched_ids(payload.get("benched_away"))
        else:
            home_team_id = request.args.get("home_team_id", type=int, default=0)
            away_team_id = request.args.get("away_team_id", type=int, default=0)
            h_odds = request.args.get("h_odds", type=float)
            d_odds = request.args.get("d_odds", type=float)
            a_odds = request.args.get("a_odds", type=float)
            benched_home = _parse_benched_ids(request.args.get("benched_home"))
            benched_away = _parse_benched_ids(request.args.get("benched_away"))

        if not home_team_id or not away_team_id:
            return jsonify({"status": "error", "error": "home_team_id y away_team_id son requeridos"}), 400

        odds = None
        if h_odds and d_odds and a_odds:
            from src.domain.value_objects.betting_market import BettingOdds
            odds = BettingOdds(home_win=float(h_odds), draw=float(d_odds), away_win=float(a_odds))

        result = prediction_service.predict_teams(
            home_team_id,
            away_team_id,
            odds=odds,
            benched_home=benched_home,
            benched_away=benched_away,
        )
        return jsonify({"status": "success", "data": result})
    except ValueError as e:
        return jsonify({"status": "error", "error": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


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
