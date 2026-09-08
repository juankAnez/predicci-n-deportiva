from flask import Blueprint, jsonify, request

from src.infrastructure.database.repositories import RankingRepository

ranking_bp = Blueprint("rankings", __name__)
ranking_repo = RankingRepository()


@ranking_bp.route("/fifa", methods=["GET"])
def get_fifa_rankings():
    rankings = ranking_repo.get_latest_rankings(ranking_type="fifa")
    return jsonify({
        "status": "success",
        "data": [
            {
                "team_id": r.team_id,
                "rank": r.rank,
                "previous_rank": r.previous_rank,
                "points": r.points,
                "rank_date": r.rank_date.isoformat() if r.rank_date else None,
            }
            for r in rankings
        ],
    })


@ranking_bp.route("/elo", methods=["GET"])
def get_elo_rankings():
    rankings = ranking_repo.get_latest_rankings(ranking_type="elo")
    return jsonify({
        "status": "success",
        "data": [
            {
                "team_id": r.team_id,
                "rank": r.rank,
                "points": r.points,
                "rank_date": r.rank_date.isoformat() if r.rank_date else None,
            }
            for r in rankings
        ],
    })


@ranking_bp.route("/<int:team_id>/history", methods=["GET"])
def get_team_ranking_history(team_id: int):
    ranking_type = request.args.get("type", "fifa")
    history = ranking_repo.get_team_ranking_history(team_id, ranking_type=ranking_type)
    return jsonify({
        "status": "success",
        "data": [
            {
                "rank": r.rank,
                "points": r.points,
                "date": r.rank_date.isoformat() if r.rank_date else None,
            }
            for r in history
        ],
    })
