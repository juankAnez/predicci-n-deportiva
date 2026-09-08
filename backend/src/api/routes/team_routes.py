from flask import Blueprint, jsonify, request

from src.infrastructure.database.repositories import TeamRepository, RankingRepository

team_bp = Blueprint("teams", __name__)
team_repo = TeamRepository()
ranking_repo = RankingRepository()


@team_bp.route("", methods=["GET"])
def list_teams():
    confederation = request.args.get("confederation")
    search = request.args.get("search")
    league = request.args.get("league")
    country = request.args.get("country")

    if search:
        teams = team_repo.search(search)
    elif confederation:
        teams = team_repo.get_by_confederation(confederation)
    else:
        teams = team_repo.get_all()

    if league:
        l_upper = league.strip().upper()
        if l_upper in ("PL", "PREMIER", "PREMIER LEAGUE", "ENG_PL", "ENGLAND"):
            teams = [t for t in teams if t.country == "England"]
        elif l_upper in ("PD", "LIGA", "LA LIGA", "ESP_L1", "SPAIN"):
            teams = [t for t in teams if t.country == "Spain"]
    elif country:
        teams = [t for t in teams if t.country and t.country.lower() == country.strip().lower()]

    teams.sort(key=lambda t: t.name)

    return jsonify({
        "status": "success",
        "data": [
            {
                "id": t.id,
                "name": t.name,
                "full_name": t.full_name,
                "code": t.code,
                "country": t.country,
                "confederation": t.confederation,
                "league": "Premier League" if t.country == "England" else "La Liga",
                "league_code": "PL" if t.country == "England" else "PD",
                "logo_url": t.logo_url,
            }
            for t in teams
        ],
    })


@team_bp.route("/<int:team_id>", methods=["GET"])
def get_team(team_id: int):
    team = team_repo.get_by_id(team_id)
    if not team:
        return jsonify({"status": "error", "error": "Equipo no encontrado"}), 404

    ranking = ranking_repo.get_latest_by_team(team_id)

    return jsonify({
        "status": "success",
        "data": {
            "id": team.id,
            "name": team.name,
            "full_name": team.full_name,
            "code": team.code,
            "country": team.country,
            "confederation": team.confederation,
            "founded_year": team.founded_year,
            "logo_url": team.logo_url,
            "ranking": {
                "fifa_rank": ranking.rank if ranking else None,
                "fifa_points": ranking.points if ranking else None,
            } if ranking else None,
        },
    })


@team_bp.route("/<int:team_id>/history", methods=["GET"])
def get_team_history(team_id: int):
    from src.infrastructure.database.repositories import MatchRepository
    match_repo = MatchRepository()
    matches = match_repo.get_by_team(team_id, limit=20)

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
                "is_home": m.home_team_id == team_id,
                "stage": m.stage,
            }
            for m in matches
        ],
    })
