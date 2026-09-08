from datetime import date
from flask import Blueprint, jsonify, request

from src.infrastructure.database.repositories import MatchRepository, TeamRepository

match_bp = Blueprint("matches", __name__)
match_repo = MatchRepository()
team_repo = TeamRepository()


DEFAULT_MATCH_ODDS = {
    # Premier League
    (36, 41): {"h": 4.50, "d": 3.90, "a": 1.75},  # Southampton vs Man United
    (42, 48): {"h": 1.55, "d": 4.40, "a": 5.80},  # Brighton vs Ipswich
    (25, 39): {"h": 1.62, "d": 4.10, "a": 5.25},  # Crystal Palace vs Leicester
    (27, 43): {"h": 2.40, "d": 3.50, "a": 2.90},  # Fulham vs West Ham
    (28, 34): {"h": 1.22, "d": 6.80, "a": 12.00}, # Liverpool vs Nott'm Forest
    (44, 40): {"h": 1.18, "d": 7.50, "a": 14.00}, # Man City vs Brentford
    (30, 37): {"h": 1.50, "d": 4.50, "a": 6.20},  # Aston Villa vs Everton
    (29, 38): {"h": 3.40, "d": 3.80, "a": 2.05},  # Bournemouth vs Chelsea
    (35, 26): {"h": 2.90, "d": 3.60, "a": 2.35},  # Tottenham vs Arsenal
    (32, 33): {"h": 3.30, "d": 3.70, "a": 2.10},  # Wolves vs Newcastle
    # La Liga
    (19, 24): {"h": 1.68, "d": 3.70, "a": 5.50},  # Betis vs Leganes
    (16, 6):  {"h": 3.10, "d": 3.30, "a": 2.35},  # Mallorca vs Villarreal
    (4, 22):  {"h": 2.65, "d": 3.10, "a": 2.90},  # Espanol vs Alaves
    (2, 17):  {"h": 2.15, "d": 3.10, "a": 3.80},  # Sevilla vs Getafe
    (10, 14): {"h": 4.33, "d": 3.75, "a": 1.80},  # Sociedad vs Real Madrid
    (3, 5):   {"h": 1.70, "d": 3.80, "a": 5.00},  # Celta vs Valladolid
    (12, 7):  {"h": 3.90, "d": 3.90, "a": 1.85},  # Girona vs Barcelona
    (21, 15): {"h": 3.75, "d": 3.40, "a": 2.05},  # Las Palmas vs Ath Bilbao
    (18, 11): {"h": 1.35, "d": 5.00, "a": 9.50},  # Ath Madrid vs Valencia
    (8, 1):   {"h": 2.10, "d": 3.20, "a": 3.80},  # Vallecano vs Osasuna
}


def get_league_info(competition_id):
    if competition_id in (4, 5, 6):
        return {"league": "Premier League", "league_code": "PL", "country": "England"}
    return {"league": "La Liga", "league_code": "PD", "country": "Spain"}


@match_bp.route("", methods=["GET"])
def list_matches():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    team_id = request.args.get("team_id", type=int)
    competition_id = request.args.get("competition_id", type=int)
    league = request.args.get("league")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    status = request.args.get("status")

    matches = match_repo.get_all()

    if team_id:
        matches = [m for m in matches if m.home_team_id == team_id or m.away_team_id == team_id]
    
    if league:
        l_upper = league.strip().upper()
        if l_upper in ("PL", "PREMIER", "PREMIER LEAGUE", "ENG_PL", "ENGLAND"):
            matches = [m for m in matches if m.competition_id in (4, 5, 6)]
        elif l_upper in ("PD", "LIGA", "LA LIGA", "ESP_L1", "SPAIN"):
            matches = [m for m in matches if m.competition_id in (1, 2, 3)]
    elif competition_id:
        matches = [m for m in matches if m.competition_id == competition_id]

    if date_from:
        matches = [m for m in matches if m.match_date and m.match_date >= date.fromisoformat(date_from)]
    if date_to:
        matches = [m for m in matches if m.match_date and m.match_date <= date.fromisoformat(date_to)]

    if status == "upcoming":
        matches = [m for m in matches if not m.is_finished and m.match_date and m.match_date >= date.today()]
        matches.sort(key=lambda m: (m.match_date or date.max, str(m.match_time or "")))
    elif status == "finished":
        matches = [m for m in matches if m.is_finished]
        matches.sort(key=lambda m: m.match_date or date.min, reverse=True)
    else:
        # Combined: upcoming first (sorted ascending), then finished (sorted descending)
        upcoming_matches = [m for m in matches if not m.is_finished and m.match_date and m.match_date >= date.today()]
        upcoming_matches.sort(key=lambda m: (m.match_date or date.max, str(m.match_time or "")))
        finished_matches = [m for m in matches if m.is_finished]
        finished_matches.sort(key=lambda m: m.match_date or date.min, reverse=True)
        other_matches = [m for m in matches if not m.is_finished and (not m.match_date or m.match_date < date.today())]
        matches = upcoming_matches + finished_matches + other_matches

    total = len(matches)
    start = (page - 1) * per_page
    matches_page = matches[start:start + per_page]

    teams = {t.id: t.name for t in team_repo.get_all()}

    output = []
    for m in matches_page:
        info = get_league_info(m.competition_id)
        default_odds = DEFAULT_MATCH_ODDS.get(
            (m.home_team_id, m.away_team_id),
            {"h": 2.20, "d": 3.30, "a": 3.20}
        )
        output.append({
            "id": m.id,
            "date": m.match_date.isoformat() if m.match_date else None,
            "time": str(m.match_time) if m.match_time else None,
            "home_team_id": m.home_team_id,
            "away_team_id": m.away_team_id,
            "home_team_name": teams.get(m.home_team_id, f"Team_{m.home_team_id}"),
            "away_team_name": teams.get(m.away_team_id, f"Team_{m.away_team_id}"),
            "home_score": m.home_score,
            "away_score": m.away_score,
            "stage": m.stage,
            "competition_id": m.competition_id,
            "league": info["league"],
            "league_code": info["league_code"],
            "country": info["country"],
            "venue": m.venue or m.stadium,
            "stadium": m.stadium or m.venue,
            "is_finished": m.is_finished,
            "odds": default_odds,
        })

    return jsonify({
        "status": "success",
        "data": output,
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
