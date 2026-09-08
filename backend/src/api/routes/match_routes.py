from datetime import date
from flask import Blueprint, jsonify, request

from src.infrastructure.database.repositories import MatchRepository, TeamRepository

match_bp = Blueprint("matches", __name__)
match_repo = MatchRepository()
team_repo = TeamRepository()


DEFAULT_MATCH_ODDS = {
    # Premier League (Gameweek 4: Sept 12-14, 2026)
    (29, 40): {"h": 2.30, "d": 3.50, "a": 3.00},  # Bournemouth vs Brentford
    (30, 34): {"h": 1.65, "d": 4.00, "a": 5.00},  # Aston Villa vs Nott'm Forest
    (25, 48): {"h": 1.80, "d": 3.75, "a": 4.40},  # Crystal Palace vs Ipswich
    (28, 27): {"h": 1.25, "d": 6.50, "a": 10.00}, # Liverpool vs Fulham
    (35, 37): {"h": 1.55, "d": 4.40, "a": 5.50},  # Tottenham vs Everton
    (42, 38): {"h": 3.20, "d": 3.70, "a": 2.15},  # Brighton vs Chelsea
    (36, 26): {"h": 6.50, "d": 4.50, "a": 1.48},  # Southampton vs Arsenal
    (41, 44): {"h": 3.80, "d": 3.80, "a": 1.90},  # Man United vs Man City (Manchester Derby)
    (32, 43): {"h": 2.50, "d": 3.40, "a": 2.80},  # Wolves vs West Ham
    (31, 33): {"h": 3.10, "d": 3.50, "a": 2.25},  # Leeds vs Newcastle

    # La Liga (Jornada 5: Sept 11-14, 2026)
    (2, 11):  {"h": 2.15, "d": 3.25, "a": 3.50},  # Sevilla vs Valencia
    (22, 21): {"h": 2.05, "d": 3.20, "a": 3.90},  # Alaves vs Las Palmas
    (14, 8):  {"h": 1.22, "d": 6.50, "a": 12.00}, # Real Madrid vs Rayo Vallecano
    (6, 19):  {"h": 2.10, "d": 3.50, "a": 3.40},  # Villarreal vs Betis
    (16, 3):  {"h": 2.40, "d": 3.10, "a": 3.20},  # Mallorca vs Celta
    (17, 24): {"h": 2.00, "d": 3.00, "a": 4.30},  # Getafe vs Leganes
    (15, 20): {"h": 1.50, "d": 4.20, "a": 6.80},  # Ath Bilbao vs Elche
    (10, 18): {"h": 2.90, "d": 3.20, "a": 2.55},  # Sociedad vs Ath Madrid
    (12, 7):  {"h": 3.90, "d": 3.90, "a": 1.85},  # Girona vs Barcelona
    (1, 4):   {"h": 1.95, "d": 3.30, "a": 4.20},  # Osasuna vs Espanol

    # Serie A (Jornada 4: Sept 12-14, 2026)
    (50, 56): {"h": 1.75, "d": 3.60, "a": 4.80},  # AC Milan vs Fiorentina
    (51, 53): {"h": 2.10, "d": 3.25, "a": 3.60},  # Juventus vs AS Roma
    (54, 55): {"h": 2.05, "d": 3.40, "a": 3.70},  # Atalanta vs Lazio
    (52, 49): {"h": 2.80, "d": 3.30, "a": 2.50},  # Napoli vs Inter

    # Bundesliga (Jornada 3: Sept 12-14, 2026)
    (58, 61): {"h": 1.65, "d": 4.20, "a": 4.80},  # Dortmund vs Frankfurt
    (59, 62): {"h": 1.50, "d": 4.50, "a": 6.00},  # Leverkusen vs Stuttgart
    (60, 57): {"h": 3.40, "d": 3.90, "a": 2.00},  # Leipzig vs Bayern

    # Ligue 1 (Jornada 4: Sept 12-14, 2026)
    (65, 66): {"h": 2.00, "d": 3.60, "a": 3.50},  # Marsella vs Lyon
    (64, 67): {"h": 2.15, "d": 3.40, "a": 3.30},  # Monaco vs Lille
    (63, 68): {"h": 1.35, "d": 5.20, "a": 8.50},  # PSG vs Rennes

    # UEFA Champions League (Fase de Liga - J1)
    (14, 57): {"h": 2.25, "d": 3.60, "a": 3.00},  # Real Madrid vs Bayern
    (44, 49): {"h": 1.55, "d": 4.20, "a": 5.80},  # Man City vs Inter
    (50, 28): {"h": 3.50, "d": 3.60, "a": 2.05},  # Milan vs Liverpool
    (26, 59): {"h": 2.05, "d": 3.50, "a": 3.50},  # Arsenal vs Leverkusen
    (7, 63):  {"h": 2.30, "d": 3.70, "a": 2.85},  # Barcelona vs PSG
    (51, 58): {"h": 2.10, "d": 3.40, "a": 3.40},  # Juventus vs Dortmund
}


def get_league_info(competition_id):
    comp_map = {
        1: {"league": "La Liga", "league_code": "PD", "country": "Spain"},
        2: {"league": "La Liga", "league_code": "PD", "country": "Spain"},
        3: {"league": "La Liga", "league_code": "PD", "country": "Spain"},
        4: {"league": "Premier League", "league_code": "PL", "country": "England"},
        5: {"league": "Premier League", "league_code": "PL", "country": "England"},
        6: {"league": "Premier League", "league_code": "PL", "country": "England"},
        7: {"league": "Serie A", "league_code": "SA", "country": "Italy"},
        8: {"league": "Bundesliga", "league_code": "BL", "country": "Germany"},
        9: {"league": "Ligue 1", "league_code": "L1", "country": "France"},
        10: {"league": "Champions League", "league_code": "UCL", "country": "Europe"},
        11: {"league": "Europa League", "league_code": "UEL", "country": "Europe"},
        12: {"league": "Copa del Rey", "league_code": "CDR", "country": "Spain"},
        13: {"league": "FA Cup", "league_code": "FAC", "country": "England"},
        14: {"league": "Coppa Italia", "league_code": "CI", "country": "Italy"},
        15: {"league": "DFB-Pokal", "league_code": "DFB", "country": "Germany"},
        16: {"league": "Coupe de France", "league_code": "CDF", "country": "France"},
    }
    return comp_map.get(competition_id, {"league": "La Liga", "league_code": "PD", "country": "Spain"})


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
            matches = [m for m in matches if m.competition_id in (4, 5, 6, 13)]
        elif l_upper in ("PD", "LIGA", "LA LIGA", "ESP_L1", "SPAIN"):
            matches = [m for m in matches if m.competition_id in (1, 2, 3, 12)]
        elif l_upper in ("SA", "SERIE A", "SERIE_A", "ITA_SA", "ITALY"):
            matches = [m for m in matches if m.competition_id in (7, 14)]
        elif l_upper in ("BL", "BUNDESLIGA", "GER_BL", "GERMANY"):
            matches = [m for m in matches if m.competition_id in (8, 15)]
        elif l_upper in ("L1", "LIGUE 1", "LIGUE_1", "FRA_L1", "FRANCE"):
            matches = [m for m in matches if m.competition_id in (9, 16)]
        elif l_upper in ("UCL", "CHAMPIONS", "CHAMPIONS LEAGUE", "UEFA_CL"):
            matches = [m for m in matches if m.competition_id == 10]
        elif l_upper in ("UEL", "EUROPA", "EUROPA LEAGUE", "UEFA_EL"):
            matches = [m for m in matches if m.competition_id == 11]
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


@match_bp.route("/<int:match_id>/result", methods=["POST", "PUT"])
def update_match_result(match_id: int):
    """
    Guarda el resultado final de un partido terminado.
    Automáticamente pasa de 'Próximo' a 'Historial' y se incorpora al cálculo de métricas futuras.
    """
    payload = request.get_json() or {}
    home_score = payload.get("home_score")
    away_score = payload.get("away_score")

    if home_score is None or away_score is None:
        return jsonify({"status": "error", "error": "home_score y away_score son requeridos"}), 400

    data = {
        "home_score": int(home_score),
        "away_score": int(away_score),
    }
    if "home_xg" in payload and payload["home_xg"] is not None:
        data["home_xg"] = float(payload["home_xg"])
    if "away_xg" in payload and payload["away_xg"] is not None:
        data["away_xg"] = float(payload["away_xg"])

    updated = match_repo.update(match_id, data)
    if not updated:
        return jsonify({"status": "error", "error": f"Partido con ID {match_id} no encontrado"}), 404

    return jsonify({
        "status": "success",
        "message": f"Resultado guardado exitosamente: {updated.home_score} - {updated.away_score}",
        "data": {
            "id": updated.id,
            "home_score": updated.home_score,
            "away_score": updated.away_score,
            "is_finished": updated.is_finished,
        },
    })

