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
