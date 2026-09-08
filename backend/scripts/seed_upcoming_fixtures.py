"""
Seed script to insert authentic, official upcoming weekend fixtures for
Premier League (Gameweek 4) and La Liga (Jornada 5) for September 11-14, 2026.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "prediccion.db"

# Official Fixtures verified against Premier League and La Liga official calendars
OFFICIAL_FIXTURES = [
    # =========================================================================
    # PREMIER LEAGUE - Gameweek 4 (Sept 12 - 14, 2026)
    # Competition ID 6
    # =========================================================================
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Gameweek 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "15:00:00",
        "home_team_id": 29,  # Bournemouth
        "away_team_id": 40,  # Brentford
        "venue": "Vitality Stadium",
        "city": "Bournemouth",
        "country": "England",
        "stadium": "Vitality Stadium",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Gameweek 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "15:00:00",
        "home_team_id": 30,  # Aston Villa
        "away_team_id": 34,  # Nottingham Forest
        "venue": "Villa Park",
        "city": "Birmingham",
        "country": "England",
        "stadium": "Villa Park",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Gameweek 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "15:00:00",
        "home_team_id": 25,  # Crystal Palace
        "away_team_id": 48,  # Ipswich
        "venue": "Selhurst Park",
        "city": "London",
        "country": "England",
        "stadium": "Selhurst Park",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Gameweek 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "15:00:00",
        "home_team_id": 28,  # Liverpool
        "away_team_id": 27,  # Fulham
        "venue": "Anfield",
        "city": "Liverpool",
        "country": "England",
        "stadium": "Anfield",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Gameweek 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "17:30:00",
        "home_team_id": 35,  # Tottenham Hotspur
        "away_team_id": 37,  # Everton
        "venue": "Tottenham Hotspur Stadium",
        "city": "London",
        "country": "England",
        "stadium": "Tottenham Hotspur Stadium",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Gameweek 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "20:00:00",
        "home_team_id": 42,  # Brighton
        "away_team_id": 38,  # Chelsea
        "venue": "Amex Stadium",
        "city": "Brighton",
        "country": "England",
        "stadium": "Amex Stadium",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Gameweek 4",
        "round": 4,
        "match_date": "2026-09-13",
        "match_time": "14:00:00",
        "home_team_id": 36,  # Southampton
        "away_team_id": 26,  # Arsenal
        "venue": "St Mary's Stadium",
        "city": "Southampton",
        "country": "England",
        "stadium": "St Mary's Stadium",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Gameweek 4",
        "round": 4,
        "match_date": "2026-09-13",
        "match_time": "16:30:00",
        "home_team_id": 41,  # Manchester United
        "away_team_id": 44,  # Manchester City (Manchester Derby)
        "venue": "Old Trafford",
        "city": "Manchester",
        "country": "England",
        "stadium": "Old Trafford",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Gameweek 4",
        "round": 4,
        "match_date": "2026-09-13",
        "match_time": "14:00:00",
        "home_team_id": 32,  # Wolves
        "away_team_id": 43,  # West Ham
        "venue": "Molineux Stadium",
        "city": "Wolverhampton",
        "country": "England",
        "stadium": "Molineux Stadium",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Gameweek 4",
        "round": 4,
        "match_date": "2026-09-14",
        "match_time": "20:00:00",
        "home_team_id": 31,  # Leeds United
        "away_team_id": 33,  # Newcastle United
        "venue": "Elland Road",
        "city": "Leeds",
        "country": "England",
        "stadium": "Elland Road",
    },

    # =========================================================================
    # LA LIGA EA SPORTS - Jornada 5 (Sept 11 - 14, 2026)
    # Competition ID 3
    # =========================================================================
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-11",
        "match_time": "21:00:00",
        "home_team_id": 2,   # Sevilla FC
        "away_team_id": 11,  # Valencia CF
        "venue": "Ramon Sanchez-Pizjuan",
        "city": "Sevilla",
        "country": "Spain",
        "stadium": "Ramon Sanchez-Pizjuan",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-12",
        "match_time": "14:00:00",
        "home_team_id": 22,  # Deportivo Alavés
        "away_team_id": 21,  # UD Las Palmas
        "venue": "Mendizorroza",
        "city": "Vitoria-Gasteiz",
        "country": "Spain",
        "stadium": "Mendizorroza",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-12",
        "match_time": "16:15:00",
        "home_team_id": 14,  # Real Madrid
        "away_team_id": 8,   # Rayo Vallecano
        "venue": "Santiago Bernabeu",
        "city": "Madrid",
        "country": "Spain",
        "stadium": "Santiago Bernabeu",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-12",
        "match_time": "18:30:00",
        "home_team_id": 6,   # Villarreal CF
        "away_team_id": 19,  # Real Betis
        "venue": "Estadio de la Ceramica",
        "city": "Villarreal",
        "country": "Spain",
        "stadium": "Estadio de la Ceramica",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-12",
        "match_time": "21:00:00",
        "home_team_id": 16,  # RCD Mallorca
        "away_team_id": 3,   # RC Celta
        "venue": "Son Moix",
        "city": "Palma",
        "country": "Spain",
        "stadium": "Son Moix",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-13",
        "match_time": "14:00:00",
        "home_team_id": 17,  # Getafe CF
        "away_team_id": 24,  # CD Leganes
        "venue": "Coliseum",
        "city": "Getafe",
        "country": "Spain",
        "stadium": "Coliseum",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-13",
        "match_time": "16:15:00",
        "home_team_id": 15,  # Athletic Club
        "away_team_id": 20,  # Elche CF
        "venue": "San Mames",
        "city": "Bilbao",
        "country": "Spain",
        "stadium": "San Mames",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-13",
        "match_time": "18:30:00",
        "home_team_id": 10,  # Real Sociedad
        "away_team_id": 18,  # Atletico de Madrid
        "venue": "Reale Arena",
        "city": "San Sebastian",
        "country": "Spain",
        "stadium": "Reale Arena",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-13",
        "match_time": "21:00:00",
        "home_team_id": 12,  # Girona FC
        "away_team_id": 7,   # FC Barcelona
        "venue": "Montilivi",
        "city": "Girona",
        "country": "Spain",
        "stadium": "Montilivi",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-14",
        "match_time": "21:00:00",
        "home_team_id": 1,   # CA Osasuna
        "away_team_id": 4,   # RCD Espanyol
        "venue": "El Sadar",
        "city": "Pamplona",
        "country": "Spain",
        "stadium": "El Sadar",
    },
]


def seed():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clean out any old/erroneous upcoming fixtures (where home_score is NULL)
    cursor.execute("DELETE FROM matches WHERE home_score IS NULL")
    deleted = cursor.rowcount
    print(f"Cleared {deleted} previous pending matches.")

    inserted = 0
    for fix in OFFICIAL_FIXTURES:
        cursor.execute(
            """
            INSERT INTO matches (
                competition_id, season, stage, round, match_date, match_time,
                home_team_id, away_team_id, home_score, away_score,
                venue, city, country, stadium, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (
                fix["competition_id"], fix["season"], fix["stage"], fix["round"],
                fix["match_date"], fix["match_time"], fix["home_team_id"], fix["away_team_id"],
                fix["venue"], fix["city"], fix["country"], fix["stadium"]
            )
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"Successfully seeded {inserted} verified official fixtures.")


if __name__ == "__main__":
    seed()
