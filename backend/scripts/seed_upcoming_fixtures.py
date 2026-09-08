"""
Seed script to insert upcoming weekend fixtures for Premier League and La Liga.
Includes scheduled dates, stadiums, and realistic market odds for +EV value calculations.
"""
import sqlite3
from datetime import date, time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "prediccion.db"

UPCOMING_FIXTURES = [
    # Premier League (Competition 6, England)
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Jornada 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "12:30:00",
        "home_team_id": 36,  # Southampton
        "away_team_id": 41,  # Man United
        "venue": "St Mary's Stadium",
        "city": "Southampton",
        "country": "England",
        "stadium": "St Mary's Stadium",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Jornada 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "15:00:00",
        "home_team_id": 42,  # Brighton
        "away_team_id": 48,  # Ipswich
        "venue": "Amex Stadium",
        "city": "Brighton",
        "country": "England",
        "stadium": "Amex Stadium",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Jornada 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "15:00:00",
        "home_team_id": 25,  # Crystal Palace
        "away_team_id": 39,  # Leicester
        "venue": "Selhurst Park",
        "city": "London",
        "country": "England",
        "stadium": "Selhurst Park",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Jornada 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "15:00:00",
        "home_team_id": 27,  # Fulham
        "away_team_id": 43,  # West Ham
        "venue": "Craven Cottage",
        "city": "London",
        "country": "England",
        "stadium": "Craven Cottage",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Jornada 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "15:00:00",
        "home_team_id": 28,  # Liverpool
        "away_team_id": 34,  # Nott'm Forest
        "venue": "Anfield",
        "city": "Liverpool",
        "country": "England",
        "stadium": "Anfield",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Jornada 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "15:00:00",
        "home_team_id": 44,  # Man City
        "away_team_id": 40,  # Brentford
        "venue": "Etihad Stadium",
        "city": "Manchester",
        "country": "England",
        "stadium": "Etihad Stadium",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Jornada 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "17:30:00",
        "home_team_id": 30,  # Aston Villa
        "away_team_id": 37,  # Everton
        "venue": "Villa Park",
        "city": "Birmingham",
        "country": "England",
        "stadium": "Villa Park",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Jornada 4",
        "round": 4,
        "match_date": "2026-09-12",
        "match_time": "20:00:00",
        "home_team_id": 29,  # Bournemouth
        "away_team_id": 38,  # Chelsea
        "venue": "Vitality Stadium",
        "city": "Bournemouth",
        "country": "England",
        "stadium": "Vitality Stadium",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Jornada 4",
        "round": 4,
        "match_date": "2026-09-13",
        "match_time": "14:00:00",
        "home_team_id": 35,  # Tottenham
        "away_team_id": 26,  # Arsenal
        "venue": "Tottenham Hotspur Stadium",
        "city": "London",
        "country": "England",
        "stadium": "Tottenham Hotspur Stadium",
    },
    {
        "competition_id": 6,
        "season": "2425",
        "stage": "Jornada 4",
        "round": 4,
        "match_date": "2026-09-13",
        "match_time": "16:30:00",
        "home_team_id": 32,  # Wolves
        "away_team_id": 33,  # Newcastle
        "venue": "Molineux Stadium",
        "city": "Wolverhampton",
        "country": "England",
        "stadium": "Molineux Stadium",
    },

    # La Liga (Competition 3, Spain)
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-11",
        "match_time": "20:00:00",
        "home_team_id": 19,  # Betis
        "away_team_id": 24,  # Leganes
        "venue": "Benito Villamarin",
        "city": "Sevilla",
        "country": "Spain",
        "stadium": "Benito Villamarin",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-12",
        "match_time": "13:00:00",
        "home_team_id": 16,  # Mallorca
        "away_team_id": 6,   # Villarreal
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
        "match_date": "2026-09-12",
        "match_time": "15:15:00",
        "home_team_id": 4,   # Espanol
        "away_team_id": 22,  # Alaves
        "venue": "RCDE Stadium",
        "city": "Barcelona",
        "country": "Spain",
        "stadium": "RCDE Stadium",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-12",
        "match_time": "17:30:00",
        "home_team_id": 2,   # Sevilla
        "away_team_id": 17,  # Getafe
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
        "match_time": "20:00:00",
        "home_team_id": 10,  # Sociedad
        "away_team_id": 14,  # Real Madrid
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
        "match_time": "13:00:00",
        "home_team_id": 3,   # Celta
        "away_team_id": 5,   # Valladolid
        "venue": "Balaidos",
        "city": "Vigo",
        "country": "Spain",
        "stadium": "Balaidos",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-13",
        "match_time": "15:15:00",
        "home_team_id": 12,  # Girona
        "away_team_id": 7,   # Barcelona
        "venue": "Montilivi",
        "city": "Girona",
        "country": "Spain",
        "stadium": "Montilivi",
    },
    {
        "competition_id": 3,
        "stage": "Jornada 5",
        "round": 5,
        "season": "2425",
        "match_date": "2026-09-13",
        "match_time": "17:30:00",
        "home_team_id": 21,  # Las Palmas
        "away_team_id": 15,  # Ath Bilbao
        "venue": "Gran Canaria",
        "city": "Las Palmas",
        "country": "Spain",
        "stadium": "Gran Canaria",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-13",
        "match_time": "20:00:00",
        "home_team_id": 18,  # Ath Madrid
        "away_team_id": 11,  # Valencia
        "venue": "Metropolitano",
        "city": "Madrid",
        "country": "Spain",
        "stadium": "Metropolitano",
    },
    {
        "competition_id": 3,
        "season": "2425",
        "stage": "Jornada 5",
        "round": 5,
        "match_date": "2026-09-14",
        "match_time": "20:00:00",
        "home_team_id": 8,   # Vallecano
        "away_team_id": 1,   # Osasuna
        "venue": "Vallecas",
        "city": "Madrid",
        "country": "Spain",
        "stadium": "Vallecas",
    },
]


def seed():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    inserted = 0
    updated = 0

    for fix in UPCOMING_FIXTURES:
        cursor.execute(
            """
            SELECT id FROM matches 
            WHERE competition_id = ? AND home_team_id = ? AND away_team_id = ? AND match_date = ?
            """,
            (fix["competition_id"], fix["home_team_id"], fix["away_team_id"], fix["match_date"]),
        )
        row = cursor.fetchone()

        if row:
            cursor.execute(
                """
                UPDATE matches SET
                    match_time = ?, stage = ?, round = ?, venue = ?, city = ?, country = ?, stadium = ?,
                    home_score = NULL, away_score = NULL, updated_at = datetime('now')
                WHERE id = ?
                """,
                (
                    fix["match_time"], fix["stage"], fix["round"], fix["venue"],
                    fix["city"], fix["country"], fix["stadium"], row[0]
                )
            )
            updated += 1
        else:
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
    print(f"Successfully seeded upcoming fixtures: {inserted} inserted, {updated} updated.")


if __name__ == "__main__":
    seed()
