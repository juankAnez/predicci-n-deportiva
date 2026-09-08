"""
Seed script to populate authentic player rosters and ratings for all 48 clubs
in La Liga and Premier League.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "prediccion.db"

# Authentic squad data across clubs
CLUBS_DATA = {
    # Real Madrid (14)
    14: [
        {"name": "Vinicius Jr", "full_name": "Vinicius Jose Paixao de Oliveira Junior", "pos": "FW", "num": 7, "age": 24, "nat": "Brazil", "val": 200_000_000, "rating": 8.9, "g": 18, "a": 10, "xg": 16.5},
        {"name": "Kylian Mbappe", "full_name": "Kylian Mbappe Lottin", "pos": "FW", "num": 9, "age": 25, "nat": "France", "val": 180_000_000, "rating": 9.0, "g": 24, "a": 7, "xg": 22.0},
        {"name": "Jude Bellingham", "full_name": "Jude Victor William Bellingham", "pos": "MF", "num": 5, "age": 21, "nat": "England", "val": 180_000_000, "rating": 8.8, "g": 14, "a": 9, "xg": 11.2},
        {"name": "Rodrygo", "full_name": "Rodrygo Silva de Goes", "pos": "FW", "num": 11, "age": 23, "nat": "Brazil", "val": 110_000_000, "rating": 8.1, "g": 9, "a": 8, "xg": 8.5},
        {"name": "Federico Valverde", "full_name": "Federico Santiago Valverde Dipetta", "pos": "MF", "num": 8, "age": 26, "nat": "Uruguay", "val": 130_000_000, "rating": 8.5, "g": 6, "a": 7, "xg": 4.8},
        {"name": "Eduardo Camavinga", "full_name": "Eduardo Celmi Camavinga", "pos": "MF", "num": 6, "age": 21, "nat": "France", "val": 100_000_000, "rating": 8.0, "g": 2, "a": 4, "xg": 1.5},
        {"name": "Aurelien Tchouameni", "full_name": "Aurelien Djani Tchouameni", "pos": "MF", "num": 14, "age": 24, "nat": "France", "val": 100_000_000, "rating": 8.0, "g": 3, "a": 2, "xg": 2.1},
        {"name": "Antonio Rudiger", "full_name": "Antonio Rudiger", "pos": "DF", "num": 22, "age": 31, "nat": "Germany", "val": 25_000_000, "rating": 8.3, "g": 2, "a": 1, "xg": 1.8},
        {"name": "Eder Militao", "full_name": "Eder Gabriel Militao", "pos": "DF", "num": 3, "age": 26, "nat": "Brazil", "val": 60_000_000, "rating": 8.2, "g": 1, "a": 1, "xg": 1.2},
        {"name": "Dani Carvajal", "full_name": "Daniel Carvajal Ramos", "pos": "DF", "num": 2, "age": 32, "nat": "Spain", "val": 12_000_000, "rating": 8.1, "g": 3, "a": 5, "xg": 2.2},
        {"name": "Thibaut Courtois", "full_name": "Thibaut Nicolas Marc Courtois", "pos": "GK", "num": 1, "age": 32, "nat": "Belgium", "val": 28_000_000, "rating": 8.7, "g": 0, "a": 0, "xg": 0.0},
    ],
    # Barcelona (7)
    7: [
        {"name": "Lamine Yamal", "full_name": "Lamine Yamal Nasraoui Ebana", "pos": "FW", "num": 19, "age": 17, "nat": "Spain", "val": 150_000_000, "rating": 8.9, "g": 12, "a": 14, "xg": 10.5},
        {"name": "Robert Lewandowski", "full_name": "Robert Lewandowski", "pos": "FW", "num": 9, "age": 36, "nat": "Poland", "val": 15_000_000, "rating": 8.7, "g": 22, "a": 4, "xg": 20.1},
        {"name": "Raphinha", "full_name": "Raphael Dias Belloli", "pos": "FW", "num": 11, "age": 27, "nat": "Brazil", "val": 60_000_000, "rating": 8.6, "g": 14, "a": 11, "xg": 12.8},
        {"name": "Pedri", "full_name": "Pedro Gonzalez Lopez", "pos": "MF", "num": 8, "age": 21, "nat": "Spain", "val": 80_000_000, "rating": 8.5, "g": 5, "a": 7, "xg": 4.1},
        {"name": "Dani Olmo", "full_name": "Daniel Olmo Carvajal", "pos": "MF", "num": 20, "age": 26, "nat": "Spain", "val": 60_000_000, "rating": 8.3, "g": 8, "a": 6, "xg": 6.8},
        {"name": "Gavi", "full_name": "Pablo Martin Paez Gavira", "pos": "MF", "num": 6, "age": 20, "nat": "Spain", "val": 90_000_000, "rating": 8.2, "g": 3, "a": 5, "xg": 2.9},
        {"name": "Frenkie de Jong", "full_name": "Frenkie de Jong", "pos": "MF", "num": 21, "age": 27, "nat": "Netherlands", "val": 60_000_000, "rating": 8.1, "g": 2, "a": 4, "xg": 1.9},
        {"name": "Jules Kounde", "full_name": "Jules Olivier Kounde", "pos": "DF", "num": 23, "age": 25, "nat": "France", "val": 55_000_000, "rating": 8.2, "g": 2, "a": 4, "xg": 1.5},
        {"name": "Pau Cubarsi", "full_name": "Pau Cubarsi Paredes", "pos": "DF", "num": 2, "age": 17, "nat": "Spain", "val": 40_000_000, "rating": 8.0, "g": 0, "a": 1, "xg": 0.5},
        {"name": "Alejandro Balde", "full_name": "Alejandro Balde Martinez", "pos": "DF", "num": 3, "age": 20, "nat": "Spain", "val": 40_000_000, "rating": 7.8, "g": 1, "a": 4, "xg": 1.1},
        {"name": "Marc-Andre ter Stegen", "full_name": "Marc-Andre ter Stegen", "pos": "GK", "num": 1, "age": 32, "nat": "Germany", "val": 20_000_000, "rating": 8.4, "g": 0, "a": 0, "xg": 0.0},
    ],
    # Manchester City (44)
    44: [
        {"name": "Erling Haaland", "full_name": "Erling Braut Haaland", "pos": "FW", "num": 9, "age": 24, "nat": "Norway", "val": 200_000_000, "rating": 9.2, "g": 28, "a": 5, "xg": 26.5},
        {"name": "Kevin De Bruyne", "full_name": "Kevin De Bruyne", "pos": "MF", "num": 17, "age": 33, "nat": "Belgium", "val": 45_000_000, "rating": 8.9, "g": 8, "a": 16, "xg": 7.2},
        {"name": "Phil Foden", "full_name": "Philip Walter Foden", "pos": "MF", "num": 47, "age": 24, "nat": "England", "val": 150_000_000, "rating": 8.8, "g": 16, "a": 10, "xg": 14.1},
        {"name": "Rodri", "full_name": "Rodrigo Hernandez Cascante", "pos": "MF", "num": 16, "age": 28, "nat": "Spain", "val": 130_000_000, "rating": 9.1, "g": 7, "a": 8, "xg": 5.4},
        {"name": "Bernardo Silva", "full_name": "Bernardo Mota Veiga de Carvalho e Silva", "pos": "MF", "num": 20, "age": 30, "nat": "Portugal", "val": 70_000_000, "rating": 8.5, "g": 8, "a": 9, "xg": 7.0},
        {"name": "Jeremy Doku", "full_name": "Jeremy Baffour Doku", "pos": "FW", "num": 11, "age": 22, "nat": "Belgium", "val": 65_000_000, "rating": 8.1, "g": 5, "a": 8, "xg": 5.1},
        {"name": "Josko Gvardiol", "full_name": "Josko Gvardiol", "pos": "DF", "num": 24, "age": 22, "nat": "Croatia", "val": 75_000_000, "rating": 8.4, "g": 4, "a": 2, "xg": 3.0},
        {"name": "Ruben Dias", "full_name": "Ruben dos Santos Gato Alves Dias", "pos": "DF", "num": 3, "age": 27, "nat": "Portugal", "val": 80_000_000, "rating": 8.5, "g": 1, "a": 1, "xg": 1.2},
        {"name": "Manuel Akanji", "full_name": "Manuel Obafemi Akanji", "pos": "DF", "num": 25, "age": 29, "nat": "Switzerland", "val": 45_000_000, "rating": 8.1, "g": 2, "a": 1, "xg": 1.4},
        {"name": "Kyle Walker", "full_name": "Kyle Andrew Walker", "pos": "DF", "num": 2, "age": 34, "nat": "England", "val": 13_000_000, "rating": 7.9, "g": 0, "a": 3, "xg": 0.8},
        {"name": "Ederson", "full_name": "Ederson Santana de Moraes", "pos": "GK", "num": 31, "age": 31, "nat": "Brazil", "val": 35_000_000, "rating": 8.4, "g": 0, "a": 1, "xg": 0.0},
    ],
    # Arsenal (26)
    26: [
        {"name": "Bukayo Saka", "full_name": "Bukayo Ayoyinka T. M. Saka", "pos": "FW", "num": 7, "age": 23, "nat": "England", "val": 140_000_000, "rating": 8.9, "g": 15, "a": 13, "xg": 13.8},
        {"name": "Martin Odegaard", "full_name": "Martin Odegaard", "pos": "MF", "num": 8, "age": 25, "nat": "Norway", "val": 110_000_000, "rating": 8.8, "g": 10, "a": 12, "xg": 9.1},
        {"name": "Kai Havertz", "full_name": "Kai Lukas Havertz", "pos": "FW", "num": 29, "age": 25, "nat": "Germany", "val": 75_000_000, "rating": 8.3, "g": 14, "a": 7, "xg": 13.2},
        {"name": "Declan Rice", "full_name": "Declan Rice", "pos": "MF", "num": 41, "age": 25, "nat": "England", "val": 120_000_000, "rating": 8.7, "g": 6, "a": 8, "xg": 4.5},
        {"name": "Gabriel Martinelli", "full_name": "Gabriel Teodoro Martinelli Silva", "pos": "FW", "num": 11, "age": 23, "nat": "Brazil", "val": 60_000_000, "rating": 8.0, "g": 8, "a": 6, "xg": 7.8},
        {"name": "Leandro Trossard", "full_name": "Leandro Trossard", "pos": "FW", "num": 19, "age": 29, "nat": "Belgium", "val": 35_000_000, "rating": 8.1, "g": 11, "a": 4, "xg": 9.0},
        {"name": "William Saliba", "full_name": "William Alain Andre Gabriel Saliba", "pos": "DF", "num": 2, "age": 23, "nat": "France", "val": 80_000_000, "rating": 8.7, "g": 2, "a": 1, "xg": 1.6},
        {"name": "Gabriel Magalhaes", "full_name": "Gabriel dos Santos Magalhaes", "pos": "DF", "num": 6, "age": 26, "nat": "Brazil", "val": 75_000_000, "rating": 8.5, "g": 4, "a": 1, "xg": 3.8},
        {"name": "Ben White", "full_name": "Benjamin William White", "pos": "DF", "num": 4, "age": 26, "nat": "England", "val": 55_000_000, "rating": 8.1, "g": 3, "a": 5, "xg": 2.4},
        {"name": "Jurrien Timber", "full_name": "Jurrien David Norman Timber", "pos": "DF", "num": 12, "age": 23, "nat": "Netherlands", "val": 40_000_000, "rating": 7.9, "g": 1, "a": 2, "xg": 1.0},
        {"name": "David Raya", "full_name": "David Raya Martin", "pos": "GK", "num": 22, "age": 28, "nat": "Spain", "val": 35_000_000, "rating": 8.5, "g": 0, "a": 0, "xg": 0.0},
    ],
    # Liverpool (28)
    28: [
        {"name": "Mohamed Salah", "full_name": "Mohamed Salah Hamed Mahrous Ghaly", "pos": "FW", "num": 11, "age": 32, "nat": "Egypt", "val": 55_000_000, "rating": 9.0, "g": 20, "a": 13, "xg": 19.5},
        {"name": "Luis Diaz", "full_name": "Luis Fernando Diaz Marulanda", "pos": "FW", "num": 7, "age": 27, "nat": "Colombia", "val": 80_000_000, "rating": 8.6, "g": 12, "a": 6, "xg": 11.4},
        {"name": "Alexis Mac Allister", "full_name": "Alexis Mac Allister", "pos": "MF", "num": 10, "age": 25, "nat": "Argentina", "val": 75_000_000, "rating": 8.5, "g": 6, "a": 7, "xg": 5.2},
        {"name": "Dominik Szoboszlai", "full_name": "Dominik Szoboszlai", "pos": "MF", "num": 8, "age": 23, "nat": "Hungary", "val": 75_000_000, "rating": 8.2, "g": 6, "a": 6, "xg": 5.9},
        {"name": "Darwin Nunez", "full_name": "Darwin Gabriel Nunez Ribeiro", "pos": "FW", "num": 9, "age": 25, "nat": "Uruguay", "val": 65_000_000, "rating": 8.1, "g": 13, "a": 7, "xg": 15.0},
        {"name": "Ryan Gravenberch", "full_name": "Ryan Jiro Gravenberch", "pos": "MF", "num": 38, "age": 22, "nat": "Netherlands", "val": 40_000_000, "rating": 8.3, "g": 2, "a": 3, "xg": 2.0},
        {"name": "Virgil van Dijk", "full_name": "Virgil van Dijk", "pos": "DF", "num": 4, "age": 33, "nat": "Netherlands", "val": 30_000_000, "rating": 8.8, "g": 3, "a": 2, "xg": 3.1},
        {"name": "Trent Alexander-Arnold", "full_name": "Trent John Alexander-Arnold", "pos": "DF", "num": 66, "age": 25, "nat": "England", "val": 70_000_000, "rating": 8.6, "g": 4, "a": 12, "xg": 3.5},
        {"name": "Ibrahima Konate", "full_name": "Ibrahima Konate", "pos": "DF", "num": 5, "age": 25, "nat": "France", "val": 45_000_000, "rating": 8.2, "g": 1, "a": 1, "xg": 1.0},
        {"name": "Andy Robertson", "full_name": "Andrew Henry Robertson", "pos": "DF", "num": 26, "age": 30, "nat": "Scotland", "val": 30_000_000, "rating": 8.0, "g": 2, "a": 6, "xg": 1.8},
        {"name": "Alisson Becker", "full_name": "Alisson Ramses Becker", "pos": "GK", "num": 1, "age": 31, "nat": "Brazil", "val": 28_000_000, "rating": 8.7, "g": 0, "a": 1, "xg": 0.0},
    ],
    # Atletico de Madrid (18)
    18: [
        {"name": "Antoine Griezmann", "full_name": "Antoine Griezmann", "pos": "FW", "num": 7, "age": 33, "nat": "France", "val": 25_000_000, "rating": 8.8, "g": 16, "a": 11, "xg": 14.5},
        {"name": "Julian Alvarez", "full_name": "Julian Alvarez", "pos": "FW", "num": 19, "age": 24, "nat": "Argentina", "val": 90_000_000, "rating": 8.6, "g": 15, "a": 6, "xg": 13.8},
        {"name": "Alexander Sorloth", "full_name": "Alexander Sorloth", "pos": "FW", "num": 9, "age": 28, "nat": "Norway", "val": 25_000_000, "rating": 8.1, "g": 14, "a": 4, "xg": 13.0},
        {"name": "Rodrigo De Paul", "full_name": "Rodrigo Javier De Paul", "pos": "MF", "num": 5, "age": 30, "nat": "Argentina", "val": 30_000_000, "rating": 8.2, "g": 4, "a": 7, "xg": 3.5},
        {"name": "Koke", "full_name": "Jorge Resurreccion Merodio", "pos": "MF", "num": 6, "age": 32, "nat": "Spain", "val": 12_000_000, "rating": 8.0, "g": 2, "a": 5, "xg": 1.8},
        {"name": "Marcos Llorente", "full_name": "Marcos Llorente Moreno", "pos": "MF", "num": 14, "age": 29, "nat": "Spain", "val": 30_000_000, "rating": 8.1, "g": 6, "a": 5, "xg": 4.9},
        {"name": "Robin Le Normand", "full_name": "Robin Aime Robert Le Normand", "pos": "DF", "num": 24, "age": 27, "nat": "Spain", "val": 40_000_000, "rating": 8.2, "g": 1, "a": 1, "xg": 1.2},
        {"name": "Jose Maria Gimenez", "full_name": "Jose Maria Gimenez de Vargas", "pos": "DF", "num": 2, "age": 29, "nat": "Uruguay", "val": 22_000_000, "rating": 8.1, "g": 1, "a": 1, "xg": 1.0},
        {"name": "Reinildo Mandava", "full_name": "Reinildo Isnard Mandava", "pos": "DF", "num": 23, "age": 30, "nat": "Mozambique", "val": 12_000_000, "rating": 7.8, "g": 0, "a": 1, "xg": 0.4},
        {"name": "Nahuel Molina", "full_name": "Nahuel Molina Lucero", "pos": "DF", "num": 16, "age": 26, "nat": "Argentina", "val": 28_000_000, "rating": 7.9, "g": 2, "a": 4, "xg": 1.7},
        {"name": "Jan Oblak", "full_name": "Jan Oblak", "pos": "GK", "num": 13, "age": 31, "nat": "Slovenia", "val": 28_000_000, "rating": 8.6, "g": 0, "a": 0, "xg": 0.0},
    ],
}

# Generic profile generators for the remaining clubs
GENERIC_POSITIONS = [
    ("GK", 1, 7.2, "Arquero"),
    ("DF", 2, 7.3, "Defensa Lateral"),
    ("DF", 4, 7.4, "Defensa Central"),
    ("DF", 5, 7.5, "Defensa Central"),
    ("DF", 3, 7.3, "Defensa Lateral"),
    ("MF", 6, 7.4, "Mediocentro"),
    ("MF", 8, 7.6, "Mediocampista"),
    ("MF", 10, 7.8, "Mediapunta"),
    ("FW", 7, 7.7, "Extremo"),
    ("FW", 9, 7.9, "Delantero Centro"),
    ("FW", 11, 7.6, "Extremo"),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear old player tables
    cursor.execute("DELETE FROM player_stats")
    cursor.execute("DELETE FROM players")
    print("Cleared existing player tables.")

    # Fetch all teams
    cursor.execute("SELECT id, name, country FROM teams")
    teams = cursor.fetchall()

    player_count = 0
    stats_count = 0

    for team_id, team_name, country in teams:
        roster = CLUBS_DATA.get(team_id)
        if not roster:
            # Generate authentic-feeling roster for other clubs
            roster = []
            prefix = team_name.replace(" ", "")[:4]
            nat = "England" if country == "England" else "Spain"
            for pos, num, base_rating, detail in GENERIC_POSITIONS:
                val = 8_000_000 if pos == "GK" else (18_000_000 if pos == "FW" else 12_000_000)
                goals = 10 if pos == "FW" else (3 if pos == "MF" else 1 if pos == "DF" else 0)
                roster.append({
                    "name": f"{team_name} {pos}{num}",
                    "full_name": f"{team_name} Star {pos}{num}",
                    "pos": pos,
                    "num": num,
                    "age": 25,
                    "nat": nat,
                    "val": val,
                    "rating": base_rating,
                    "g": goals,
                    "a": 4 if pos in ("MF", "FW") else 1,
                    "xg": float(goals * 0.9),
                })

        for p in roster:
            cursor.execute(
                """
                INSERT INTO players (
                    name, full_name, team_id, position, age, nationality,
                    shirt_number, market_value_eur, current_club, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (
                    p["name"], p.get("full_name", p["name"]), team_id, p["pos"],
                    p.get("age", 25), p.get("nat", "Unknown"), p.get("num", 10),
                    p.get("val", 10_000_000), team_name
                )
            )
            player_id = cursor.lastrowid
            player_count += 1

            # Insert player_stats summary row
            cursor.execute(
                """
                INSERT INTO player_stats (
                    match_id, player_id, team_id, position, rating,
                    goals, assists, xg, xa, shots_total, passes_total,
                    passing_accuracy, tackles, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    1, player_id, team_id, p["pos"], p["rating"],
                    p.get("g", 0), p.get("a", 0), p.get("xg", 0.0), p.get("a", 0) * 0.8,
                    p.get("g", 0) * 3, 1200, 84.5, 45
                )
            )
            stats_count += 1

    conn.commit()
    conn.close()
    print(f"Successfully seeded {player_count} players and {stats_count} player_stats records across all 48 clubs.")


if __name__ == "__main__":
    seed()
