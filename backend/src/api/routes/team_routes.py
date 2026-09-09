from flask import Blueprint, jsonify, request

from src.infrastructure.database.repositories import TeamRepository, RankingRepository

team_bp = Blueprint("teams", __name__)
team_repo = TeamRepository()
ranking_repo = RankingRepository()


UCL_TEAM_IDS = {
    6, 7, 12, 14, 18, 19, 26, 28, 30, 41, 44, 49, 50, 51, 52, 53, 54, 57, 58, 59, 60, 62, 63, 64, 67,
    69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85
}
UEL_TEAM_IDS = {15, 10, 19, 35, 41, 38, 53, 55, 56, 61, 65, 66, 68}


def _get_league(c):
    if c == "England":
        return "Premier League", "PL"
    elif c == "Spain":
        return "La Liga", "PD"
    elif c == "Italy":
        return "Serie A", "SA"
    elif c == "Germany":
        return "Bundesliga", "BL"
    elif c == "France":
        return "Ligue 1", "L1"
    return "Europa", "EU"


def _get_competitions(t):
    comps = []
    c = t.country
    if c == "Spain":
        comps.extend(["PD", "CDR"])
    elif c == "England":
        comps.extend(["PL", "FAC"])
    elif c == "Italy":
        comps.extend(["SA", "CI"])
    elif c == "Germany":
        comps.extend(["BL", "DFB"])
    elif c == "France":
        comps.extend(["L1", "CDF"])

    if t.id in UCL_TEAM_IDS:
        comps.append("UCL")
    if t.id in UEL_TEAM_IDS:
        comps.append("UEL")
    return comps


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
        if l_upper in ("PL", "PREMIER", "PREMIER LEAGUE", "ENG_PL"):
            teams = [t for t in teams if t.country == "England"]
        elif l_upper in ("PD", "LIGA", "LA LIGA", "ESP_L1"):
            teams = [t for t in teams if t.country == "Spain"]
        elif l_upper in ("SA", "SERIE A", "SERIE_A", "ITA_SA"):
            teams = [t for t in teams if t.country == "Italy"]
        elif l_upper in ("BL", "BUNDESLIGA", "GER_BL"):
            teams = [t for t in teams if t.country == "Germany"]
        elif l_upper in ("L1", "LIGUE 1", "LIGUE_1", "FRA_L1"):
            teams = [t for t in teams if t.country == "France"]
        elif l_upper in ("UCL", "CHAMPIONS", "CHAMPIONS LEAGUE", "UEFA_CL"):
            teams = [t for t in teams if t.id in UCL_TEAM_IDS]
        elif l_upper in ("UEL", "EUROPA", "EUROPA LEAGUE", "UEFA_EL"):
            teams = [t for t in teams if t.id in UEL_TEAM_IDS]
        elif l_upper in ("CDR", "COPA DEL REY", "COPA_DEL_REY", "ESP_CDR"):
            teams = [t for t in teams if t.country == "Spain"]
        elif l_upper in ("FAC", "FA CUP", "FA_CUP", "ENG_FAC"):
            teams = [t for t in teams if t.country == "England"]
        elif l_upper in ("CI", "COPPA ITALIA", "COPPA_ITALIA", "ITA_CI"):
            teams = [t for t in teams if t.country == "Italy"]
        elif l_upper in ("DFB", "DFB-POKAL", "DFB_POKAL", "GER_POK"):
            teams = [t for t in teams if t.country == "Germany"]
        elif l_upper in ("CDF", "COUPE DE FRANCE", "COUPE_DE_FRANCE", "FRA_CDF"):
            teams = [t for t in teams if t.country == "France"]
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
                "league": _get_league(t.country)[0],
                "league_code": _get_league(t.country)[1],
                "competitions": _get_competitions(t),
                "is_ucl": t.id in UCL_TEAM_IDS,
                "is_uel": t.id in UEL_TEAM_IDS,
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
