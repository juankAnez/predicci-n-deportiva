from flask import Blueprint, jsonify, request

from src.infrastructure.database.repositories import PlayerRepository

player_bp = Blueprint("players", __name__)
player_repo = PlayerRepository()


@player_bp.route("", methods=["GET"])
def list_players():
    team_id = request.args.get("team_id", type=int)
    position = request.args.get("position")
    search = request.args.get("search")

    if search:
        players = player_repo.get_by_name(search)
    elif team_id:
        players = player_repo.get_by_team(team_id)
    elif position:
        players = player_repo.get_by_position(position)
    else:
        players = player_repo.get_all()

    return jsonify({
        "status": "success",
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "full_name": p.full_name,
                "team_id": p.team_id,
                "position": p.position,
                "age": p.age,
                "nationality": p.nationality,
                "market_value_eur": p.market_value_eur,
                "shirt_number": p.shirt_number,
            }
            for p in players
        ],
    })


@player_bp.route("/<int:player_id>", methods=["GET"])
def get_player(player_id: int):
    player = player_repo.get_by_id(player_id)
    if not player:
        return jsonify({"status": "error", "error": "Jugador no encontrado"}), 404

    return jsonify({
        "status": "success",
        "data": {
            "id": player.id,
            "name": player.name,
            "full_name": player.full_name,
            "team_id": player.team_id,
            "position": player.position,
            "position_detail": player.position_detail,
            "age": player.age,
            "date_of_birth": player.date_of_birth.isoformat() if player.date_of_birth else None,
            "nationality": player.nationality,
            "height_cm": player.height_cm,
            "weight_kg": player.weight_kg,
            "foot": player.foot,
            "market_value_eur": player.market_value_eur,
            "current_club": player.current_club,
            "shirt_number": player.shirt_number,
            "international_caps": player.international_caps,
            "international_goals": player.international_goals,
        },
    })


@player_bp.route("/team/<int:team_id>", methods=["GET"])
def get_team_players(team_id: int):
    """
    Obtiene la plantilla completa del club con sus estadísticas y ratings actuales.
    """
    from src.infrastructure.database.models import PlayerModel, PlayerStatsModel
    from src.infrastructure.database.connection import db_session

    db = db_session()
    try:
        players = db.query(PlayerModel).filter(PlayerModel.team_id == team_id).all()
        results = []
        for p in players:
            stat = db.query(PlayerStatsModel).filter(PlayerStatsModel.player_id == p.id).first()
            results.append({
                "id": p.id,
                "name": p.name,
                "full_name": p.full_name,
                "team_id": p.team_id,
                "position": p.position,
                "shirt_number": p.shirt_number,
                "age": p.age,
                "nationality": p.nationality,
                "market_value_eur": p.market_value_eur,
                "rating": stat.rating if stat and stat.rating else 7.2,
                "goals": stat.goals if stat else 0,
                "assists": stat.assists if stat else 0,
                "xg": stat.xg if stat else 0.0,
            })
        results.sort(key=lambda x: ({"GK": 0, "DF": 1, "MF": 2, "FW": 3}.get(x["position"], 4), -x["rating"]))
        return jsonify({"status": "success", "data": results})
    finally:
        db.close()


@player_bp.route("/<int:player_id>/stats", methods=["POST"])
def record_player_stats(player_id: int):
    """
    Registra las estadísticas y puntuación de un jugador tras un partido jugado.
    """
    from src.infrastructure.database.models import PlayerStatsModel, PlayerModel
    from src.infrastructure.database.connection import db_session

    payload = request.get_json() or {}
    match_id = payload.get("match_id", 1)
    team_id = payload.get("team_id")
    rating = payload.get("rating", 7.0)
    goals = payload.get("goals", 0)
    assists = payload.get("assists", 0)
    xg = payload.get("xg", 0.0)

    db = db_session()
    try:
        player = db.query(PlayerModel).filter(PlayerModel.id == player_id).first()
        if not player:
            return jsonify({"status": "error", "error": "Jugador no encontrado"}), 404

        stat = db.query(PlayerStatsModel).filter(
            PlayerStatsModel.player_id == player_id,
            PlayerStatsModel.match_id == match_id
        ).first()

        if stat:
            stat.rating = float(rating)
            stat.goals = int(goals)
            stat.assists = int(assists)
            stat.xg = float(xg)
        else:
            stat = PlayerStatsModel(
                match_id=int(match_id),
                player_id=player_id,
                team_id=team_id or player.team_id,
                position=player.position,
                rating=float(rating),
                goals=int(goals),
                assists=int(assists),
                xg=float(xg),
            )
            db.add(stat)

        db.commit()
        return jsonify({
            "status": "success",
            "message": f"Estadísticas actualizadas para {player.name}",
            "data": {
                "player_id": player_id,
                "rating": stat.rating,
                "goals": stat.goals,
                "assists": stat.assists,
                "xg": stat.xg,
            }
        })
    finally:
        db.close()

