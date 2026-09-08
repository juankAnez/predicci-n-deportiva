from datetime import date
from flask import Blueprint, jsonify, request

from src.infrastructure.database.repositories import MatchRepository, TeamRepository

match_bp = Blueprint("matches", __name__)
match_repo = MatchRepository()
team_repo = TeamRepository()


@match_bp.route("", methods=["GET"])
def list_matches():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    team_id = request.args.get("team_id", type=int)
    competition_id = request.args.get("competition_id", type=int)
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    status = request.args.get("status")

    matches = match_repo.get_all()

    if team_id:
        matches = [m for m in matches if m.home_team_id == team_id or m.away_team_id == team_id]
    if competition_id:
        matches = [m for m in matches if m.competition_id == competition_id]
    if date_from:
        matches = [m for m in matches if m.match_date and m.match_date >= date.fromisoformat(date_from)]
    if date_to:
        matches = [m for m in matches if m.match_date and m.match_date <= date.fromisoformat(date_to)]
    if status == "upcoming":
        matches = [m for m in matches if not m.is_finished and m.match_date and m.match_date >= date.today()]

    matches.sort(key=lambda m: m.match_date or date.min, reverse=True)
    total = len(matches)
    start = (page - 1) * per_page
    matches_page = matches[start:start + per_page]

    return jsonify({
        "status": "success",
        "data": [
            {
                "id": m.id,
                "date": m.match_date.isoformat() if m.match_date else None,
                "home_team_id": m.home_team_id,
                "away_team_id": m.away_team_id,
                "home_score": m.home_score,
                "away_score": m.away_score,
                "stage": m.stage,
                "competition_id": m.competition_id,
                "is_finished": m.is_finished,
            }
            for m in matches_page
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
    })


@match_bp.route("/<int:match_id>", methods=["GET"])
def get_match(match_id: int):
    match = match_repo.get_by_id(match_id)
    if not match:
        return jsonify({"status": "error", "error": "Partido no encontrado"}), 404

    home_team = team_repo.get_by_id(match.home_team_id) if match.home_team_id else None
    away_team = team_repo.get_by_id(match.away_team_id) if match.away_team_id else None

    return jsonify({
        "status": "success",
        "data": {
            "id": match.id,
            "date": match.match_date.isoformat() if match.match_date else None,
            "time": str(match.match_time) if match.match_time else None,
            "home_team": {
                "id": match.home_team_id,
                "name": home_team.name if home_team else None,
                "code": home_team.code if home_team else None,
            },
            "away_team": {
                "id": match.away_team_id,
                "name": away_team.name if away_team else None,
                "code": away_team.code if away_team else None,
            },
            "home_score": match.home_score,
            "away_score": match.away_score,
            "stage": match.stage,
            "competition_id": match.competition_id,
            "venue": match.venue,
            "city": match.city,
            "country": match.country,
            "stadium": match.stadium,
            "attendance": match.attendance,
            "temperature": match.temperature,
            "humidity": match.humidity,
            "home_xg": match.home_xg,
            "away_xg": match.away_xg,
            "is_finished": match.is_finished,
        },
    })


@match_bp.route("/h2h", methods=["GET"])
def get_h2h():
    team1 = request.args.get("team1", type=int)
    team2 = request.args.get("team2", type=int)
    if not team1 or not team2:
        return jsonify({"status": "error", "error": "Se requieren team1 y team2"}), 400

    h2h = match_repo.get_h2h(team1, team2)
    return jsonify({
        "status": "success",
        "data": [
            {
                "id": m.id,
                "date": m.match_date.isoformat() if m.match_date else None,
                "home_team_id": m.home_team_id,
                "away_team_id": m.away_team_id,
                "home_score": m.home_score,
                "away_score": m.away_score,
                "competition_id": m.competition_id,
                "stage": m.stage,
            }
            for m in h2h
        ],
    })
