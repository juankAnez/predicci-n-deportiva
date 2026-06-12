from flask import Blueprint, jsonify, request

from src.infrastructure.database.repositories import TeamStatsRepository, MatchRepository

stats_bp = Blueprint("stats", __name__)
stats_repo = TeamStatsRepository()
match_repo = MatchRepository()


@stats_bp.route("/match/<int:match_id>", methods=["GET"])
def get_match_stats(match_id: int):
    stats = stats_repo.get_by_match(match_id)
    if not stats:
        return jsonify({"status": "error", "error": "Estadísticas no encontradas"}), 404

    return jsonify({
        "status": "success",
        "data": [
            {
                "team_id": s.team_id,
                "is_home": s.is_home,
                "goals": s.goals,
                "xg": s.xg,
                "xga": s.xga,
                "shots_total": s.shots_total,
                "shots_on_target": s.shots_on_target,
                "corners": s.corners,
                "fouls": s.fouls,
                "yellow_cards": s.yellow_cards,
                "red_cards": s.red_cards,
                "possession": s.possession,
                "passes_total": s.passes_total,
                "passes_completed": s.passes_completed,
                "passing_accuracy": s.passing_accuracy,
                "offsides": s.offsides,
                "tackles": s.tackles,
                "interceptions": s.interceptions,
                "recoveries": s.recoveries,
                "ppda": s.ppda,
                "territorial_possession": s.territorial_possession,
                "shot_conversion_rate": s.shot_conversion_rate,
            }
            for s in stats
        ],
    })


@stats_bp.route("/team/<int:team_id>", methods=["GET"])
def get_team_stats(team_id: int):
    limit = request.args.get("limit", 10, type=int)
    stats = stats_repo.get_team_stats_since(team_id, limit=limit)
    return jsonify({
        "status": "success",
        "data": [
            {
                "match_id": s.match_id,
                "is_home": s.is_home,
                "goals": s.goals,
                "xg": s.xg,
                "shots_on_target": s.shots_on_target,
                "possession": s.possession,
                "passing_accuracy": s.passing_accuracy,
                "ppda": s.ppda,
            }
            for s in stats
        ],
    })
