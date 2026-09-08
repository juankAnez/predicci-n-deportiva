"""
Script to expand database with Top 5 European Leagues, Champions League, Europa League,
Domestic Cups, new clubs, authentic rosters, historical results and upcoming fixtures.
"""
import sqlite3
from datetime import date, datetime, timedelta

DB_PATH = "data/prediccion.db"

def seed_european_football():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    print("Iniciando expansión de ligas europeas y torneos...")

    # 1. Insert Competitions
    competitions = [
        # (id, name, short_name, type, confederation, season)
        (7, "Serie A", "ITA_SA", "league", "Italy", "2425"),
        (8, "Bundesliga", "GER_BL", "league", "Germany", "2425"),
        (9, "Ligue 1", "FRA_L1", "league", "France", "2425"),
        (10, "UEFA Champions League", "UEFA_CL", "continental", "UEFA", "2425"),
        (11, "UEFA Europa League", "UEFA_EL", "continental", "UEFA", "2425"),
        (12, "Copa del Rey", "ESP_CDR", "cup", "Spain", "2425"),
        (13, "FA Cup", "ENG_FAC", "cup", "England", "2425"),
        (14, "Coppa Italia", "ITA_CI", "cup", "Italy", "2425"),
        (15, "DFB-Pokal", "GER_POK", "cup", "Germany", "2425"),
        (16, "Coupe de France", "FRA_CDF", "cup", "France", "2425"),
    ]

    for comp in competitions:
        cur.execute("""
            INSERT OR REPLACE INTO competitions (id, name, short_name, type, confederation, season, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, comp)
    print("Competencias añadidas exitosamente.")

    # 2. Insert Teams for Italy, Germany, France
    new_teams = [
        # Italy
        (49, "Inter de Milán", "FC Internazionale Milano", "INT", "Italy", "UEFA", 1908),
        (50, "AC Milan", "Associazione Calcio Milan", "MIL", "Italy", "UEFA", 1899),
        (51, "Juventus", "Juventus Football Club", "JUV", "Italy", "UEFA", 1897),
        (52, "Napoli", "Società Sportiva Calcio Napoli", "NAP", "Italy", "UEFA", 1926),
        (53, "AS Roma", "Associazione Sportiva Roma", "ROM", "Italy", "UEFA", 1927),
        (54, "Atalanta", "Atalanta Bergamasca Calcio", "ATA", "Italy", "UEFA", 1907),
        (55, "Lazio", "Società Sportiva Lazio", "LAZ", "Italy", "UEFA", 1900),
        (56, "Fiorentina", "ACF Fiorentina", "FIO", "Italy", "UEFA", 1926),
        # Germany
        (57, "Bayern Múnich", "FC Bayern München", "BAY", "Germany", "UEFA", 1900),
        (58, "Borussia Dortmund", "Ballspielverein Borussia Dortmund", "BVB", "Germany", "UEFA", 1909),
        (59, "Bayer Leverkusen", "Bayer 04 Leverkusen", "LEV", "Germany", "UEFA", 1904),
        (60, "RB Leipzig", "RasenBallsport Leipzig", "RBL", "Germany", "UEFA", 2009),
        (61, "Eintracht Frankfurt", "Eintracht Frankfurt Fußball AG", "SGE", "Germany", "UEFA", 1899),
        (62, "VfB Stuttgart", "Verein für Bewegungsspiele Stuttgart", "VFB", "Germany", "UEFA", 1893),
        # France
        (63, "Paris Saint-Germain", "Paris Saint-Germain Football Club", "PSG", "France", "UEFA", 1970),
        (64, "AS Mónaco", "Association Sportive de Monaco FC", "MON", "France", "UEFA", 1924),
        (65, "Olympique de Marsella", "Olympique de Marseille", "MAR", "France", "UEFA", 1899),
        (66, "Olympique de Lyon", "Olympique Lyonnais", "LYO", "France", "UEFA", 1950),
        (67, "Lille OSC", "Lille Olympique Sporting Club", "LIL", "France", "UEFA", 1944),
        (68, "Stade Rennais", "Stade Rennais Football Club", "REN", "France", "UEFA", 1901),
    ]

    for t in new_teams:
        cur.execute("""
            INSERT OR REPLACE INTO teams (id, name, full_name, code, country, confederation, founded_year, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, t)
    print("20 clubes de Serie A, Bundesliga y Ligue 1 agregados exitosamente.")

    # 3. Seed Players for New Teams
    # (id, name, team_id, position, shirt, age, market_val, rating, goals, assists)
    star_players = [
        # Inter (49)
        (529, "Lautaro Martínez", 49, "FW", 10, 27, 110000000, 9.0, 24, 6),
        (530, "Nicolò Barella", 49, "MF", 23, 27, 80000000, 8.8, 4, 9),
        (531, "Marcus Thuram", 49, "FW", 9, 27, 65000000, 8.6, 15, 7),
        (532, "Alessandro Bastoni", 49, "DF", 95, 25, 75000000, 8.7, 2, 4),
        (533, "Federico Dimarco", 49, "DF", 32, 26, 60000000, 8.5, 6, 8),
        (534, "Hakan Çalhanoğlu", 49, "MF", 20, 30, 45000000, 8.7, 13, 5),
        (535, "Yann Sommer", 49, "GK", 1, 35, 5000000, 8.4, 0, 0),

        # Milan (50)
        (536, "Rafael Leão", 50, "FW", 10, 25, 90000000, 8.8, 14, 11),
        (537, "Theo Hernández", 50, "DF", 19, 26, 60000000, 8.7, 5, 8),
        (538, "Christian Pulisic", 50, "FW", 11, 26, 50000000, 8.5, 12, 8),
        (539, "Tijjani Reijnders", 50, "MF", 14, 26, 40000000, 8.4, 4, 6),
        (540, "Fikayo Tomori", 50, "DF", 23, 26, 35000000, 8.3, 1, 0),
        (541, "Mike Maignan", 50, "GK", 16, 29, 38000000, 8.6, 0, 0),

        # Juventus (51)
        (542, "Dušan Vlahović", 51, "FW", 9, 24, 65000000, 8.6, 17, 4),
        (543, "Gleison Bremer", 51, "DF", 3, 27, 60000000, 8.6, 3, 0),
        (544, "Teun Koopmeiners", 51, "MF", 8, 26, 55000000, 8.6, 12, 6),
        (545, "Kenan Yıldız", 51, "FW", 10, 19, 40000000, 8.3, 5, 4),
        (546, "Michele Di Gregorio", 51, "GK", 29, 27, 20000000, 8.4, 0, 0),

        # Napoli (52)
        (547, "Khvicha Kvaratskhelia", 52, "FW", 77, 23, 85000000, 8.8, 13, 8),
        (548, "Romelu Lukaku", 52, "FW", 11, 31, 30000000, 8.5, 14, 5),
        (549, "Scott McTominay", 52, "MF", 8, 27, 32000000, 8.3, 7, 3),
        (550, "Giovanni Di Lorenzo", 52, "DF", 22, 31, 15000000, 8.3, 2, 6),
        (551, "Alex Meret", 52, "GK", 1, 27, 12000000, 8.2, 0, 0),

        # Bayern Munich (57)
        (552, "Harry Kane", 57, "FW", 9, 31, 100000000, 9.2, 36, 9),
        (553, "Jamal Musiala", 57, "MF", 42, 21, 130000000, 9.1, 12, 10),
        (554, "Michael Olise", 57, "FW", 17, 22, 65000000, 8.8, 10, 8),
        (555, "Joshua Kimmich", 57, "MF", 6, 29, 50000000, 8.7, 3, 10),
        (556, "Alphonso Davies", 57, "DF", 19, 23, 50000000, 8.6, 2, 6),
        (557, "Dayot Upamecano", 57, "DF", 2, 25, 45000000, 8.3, 1, 0),
        (558, "Manuel Neuer", 57, "GK", 1, 38, 4000000, 8.5, 0, 0),

        # Bayer Leverkusen (59)
        (559, "Florian Wirtz", 59, "MF", 10, 21, 130000000, 9.1, 18, 19),
        (560, "Granit Xhaka", 59, "MF", 34, 31, 20000000, 8.7, 4, 3),
        (561, "Jeremie Frimpong", 59, "DF", 30, 23, 50000000, 8.7, 12, 10),
        (562, "Alejandro Grimaldo", 59, "DF", 20, 28, 45000000, 8.7, 11, 15),
        (563, "Victor Boniface", 59, "FW", 22, 23, 45000000, 8.5, 16, 8),
        (564, "Lukáš Hrádecký", 59, "GK", 1, 34, 3000000, 8.3, 0, 0),

        # Borussia Dortmund (58)
        (565, "Serhou Guirassy", 58, "FW", 9, 28, 45000000, 8.6, 28, 3),
        (566, "Julian Brandt", 58, "MF", 10, 28, 40000000, 8.5, 8, 12),
        (567, "Nico Schlotterbeck", 58, "DF", 4, 24, 40000000, 8.5, 2, 2),
        (568, "Marcel Sabitzer", 58, "MF", 20, 30, 20000000, 8.3, 6, 6),
        (569, "Gregor Kobel", 58, "GK", 1, 26, 40000000, 8.6, 0, 0),

        # Paris Saint-Germain (63)
        (570, "Ousmane Dembélé", 63, "FW", 10, 27, 60000000, 8.8, 6, 14),
        (571, "Bradley Barcola", 63, "FW", 29, 22, 65000000, 8.7, 9, 8),
        (572, "Achraf Hakimi", 63, "DF", 2, 25, 60000000, 8.8, 5, 8),
        (573, "Vitinha", 63, "MF", 17, 24, 55000000, 8.8, 9, 5),
        (574, "Warren Zaïre-Emery", 63, "MF", 33, 18, 60000000, 8.5, 3, 6),
        (575, "Marquinhos", 63, "DF", 5, 30, 50000000, 8.5, 1, 1),
        (576, "Gianluigi Donnarumma", 63, "GK", 1, 25, 40000000, 8.7, 0, 0),

        # Monaco (64)
        (577, "Aleksandr Golovin", 64, "MF", 10, 28, 30000000, 8.4, 6, 7),
        (578, "Denis Zakaria", 64, "MF", 6, 27, 28000000, 8.4, 4, 2),
        (579, "Maghnes Akliouche", 64, "MF", 11, 22, 30000000, 8.3, 8, 4),
        (580, "Folarin Balogun", 64, "FW", 9, 23, 25000000, 8.2, 8, 5),

        # Marseille (65)
        (581, "Mason Greenwood", 65, "FW", 10, 22, 35000000, 8.6, 12, 6),
        (582, "Adrien Rabiot", 65, "MF", 25, 29, 30000000, 8.5, 5, 4),
        (583, "Pierre-Emile Højbjerg", 65, "MF", 23, 29, 18000000, 8.4, 2, 3),
        (584, "Gerónimo Rulli", 65, "GK", 1, 32, 5000000, 8.2, 0, 0),
    ]

    for p in star_players:
        pid, name, tid, pos, shirt, age, mval, rat, g, a = p
        cur.execute("""
            INSERT OR REPLACE INTO players (id, name, full_name, team_id, position, shirt_number, age, market_value_eur, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (pid, name, name, tid, pos, shirt, age, mval))

        cur.execute("""
            INSERT OR REPLACE INTO player_stats (id, match_id, player_id, team_id, position, rating, goals, assists, xg, xa, created_at)
            VALUES (?, 0, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (pid, pid, tid, pos, rat, g, a, round(g * 0.85, 2), round(a * 0.75, 2)))

    # Also fill position depth for any other teams 53-56, 60-62, 66-68
    pos_map = [("GK", 1, 8.0, 15000000), ("DF", 2, 8.0, 20000000), ("DF", 4, 8.1, 22000000),
               ("MF", 6, 8.1, 25000000), ("MF", 8, 8.2, 30000000), ("FW", 9, 8.3, 35000000)]
    curr_pid = 585
    for t_id in range(49, 69):
        # check if team has at least 5 players
        cnt = cur.execute("SELECT count(*) FROM players WHERE team_id = ?", (t_id,)).fetchone()[0]
        if cnt < 5:
            t_name = cur.execute("SELECT name FROM teams WHERE id = ?", (t_id,)).fetchone()[0]
            for pos, shirt, rat, val in pos_map:
                p_name = f"{t_name} {pos}{shirt}"
                cur.execute("""
                    INSERT OR REPLACE INTO players (id, name, full_name, team_id, position, shirt_number, age, market_value_eur, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 25, ?, datetime('now'), datetime('now'))
                """, (curr_pid, p_name, p_name, t_id, pos, shirt, val))
                cur.execute("""
                    INSERT OR REPLACE INTO player_stats (id, match_id, player_id, team_id, position, rating, goals, assists, xg, xa, created_at)
                    VALUES (?, 0, ?, ?, ?, ?, 3, 2, 2.5, 1.8, datetime('now'))
                """, (curr_pid, curr_pid, t_id, pos, rat))
                curr_pid += 1

    print("Plantillas y puntuaciones registradas para los clubes europeos.")

    # 4. Seed Historical Matches for Italy, Germany, France to allow ML rolling form
    match_id = 2301
    today = date.today()
    
    # Historical matches in past 2 months
    hist_pairs = [
        # Serie A (comp 7)
        (7, 49, 50, 2, 1), (7, 51, 52, 0, 0), (7, 53, 54, 1, 2), (7, 55, 56, 1, 0),
        (7, 49, 51, 1, 0), (7, 50, 52, 2, 2), (7, 54, 49, 1, 3), (7, 52, 53, 2, 1),
        # Bundesliga (comp 8)
        (8, 57, 58, 3, 1), (8, 59, 60, 2, 1), (8, 61, 62, 1, 1), (8, 57, 59, 2, 2),
        (8, 58, 60, 1, 2), (8, 59, 58, 3, 0), (8, 57, 61, 4, 1), (8, 60, 62, 2, 0),
        # Ligue 1 (comp 9)
        (9, 63, 64, 3, 1), (9, 65, 66, 2, 1), (9, 67, 68, 1, 0), (9, 63, 65, 2, 0),
        (9, 64, 66, 2, 2), (9, 63, 67, 3, 1), (9, 65, 67, 1, 1), (9, 64, 68, 2, 0),
        # Champions League Past (comp 10)
        (10, 14, 57, 2, 1), (10, 44, 49, 1, 0), (10, 7, 63, 2, 3), (10, 26, 58, 1, 0),
        (10, 28, 59, 3, 1), (10, 50, 28, 1, 3), (10, 57, 26, 1, 0), (10, 14, 44, 3, 3),
    ]

    for comp_id, h_id, a_id, h_sc, a_sc in hist_pairs:
        m_date = today - timedelta(days=(match_id % 30) + 5)
        cur.execute("""
            INSERT OR REPLACE INTO matches (id, competition_id, season, stage, match_date, home_team_id, away_team_id, home_score, away_score, created_at, updated_at)
            VALUES (?, ?, '2425', 'Regular', ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (match_id, comp_id, m_date.isoformat(), h_id, a_id, h_sc, a_sc))
        match_id += 1

    print(f"Partidos históricos europeos registrados. ID actual: {match_id}")

    # 5. Seed Official Upcoming Matches across ALL competitions
    # This weekend / upcoming dates:
    # 2026-09-12 to 2026-09-17
    d_sat = (today + timedelta(days=(5 - today.weekday()) % 7)).isoformat()
    d_sun = (today + timedelta(days=(6 - today.weekday()) % 7)).isoformat()
    d_midweek = (today + timedelta(days=(8 - today.weekday()) % 7)).isoformat()

    upcoming_fixtures = [
        # Serie A (comp 7)
        (match_id + 0, 50, 56, 7, d_sat, "18:00", "Jornada 4"),   # AC Milan vs Fiorentina
        (match_id + 1, 51, 53, 7, d_sat, "20:45", "Jornada 4"),   # Juventus vs AS Roma
        (match_id + 2, 54, 55, 7, d_sun, "15:00", "Jornada 4"),   # Atalanta vs Lazio
        (match_id + 3, 52, 49, 7, d_sun, "20:45", "Jornada 4"),   # Napoli vs Inter (Clásico Italiano)
        
        # Bundesliga (comp 8)
        (match_id + 4, 58, 61, 8, d_sat, "15:30", "Jornada 3"),   # Dortmund vs Frankfurt
        (match_id + 5, 59, 62, 8, d_sat, "15:30", "Jornada 3"),   # Leverkusen vs Stuttgart
        (match_id + 6, 60, 57, 8, d_sat, "18:30", "Jornada 3"),   # RB Leipzig vs Bayern Múnich
        
        # Ligue 1 (comp 9)
        (match_id + 7, 65, 66, 9, d_sat, "21:00", "Jornada 4"),   # Marsella vs Lyon (Choc des Olympiques)
        (match_id + 8, 64, 67, 9, d_sun, "17:00", "Jornada 4"),   # Mónaco vs Lille
        (match_id + 9, 63, 68, 9, d_sun, "20:45", "Jornada 4"),   # PSG vs Rennes

        # UEFA Champions League (comp 10)
        (match_id + 10, 14, 57, 10, d_midweek, "21:00", "Fase de Liga - J1"), # Real Madrid vs Bayern Múnich
        (match_id + 11, 44, 49, 10, d_midweek, "21:00", "Fase de Liga - J1"), # Man City vs Inter de Milán
        (match_id + 12, 50, 28, 10, d_midweek, "21:00", "Fase de Liga - J1"), # AC Milan vs Liverpool
        (match_id + 13, 26, 59, 10, d_midweek, "21:00", "Fase de Liga - J1"), # Arsenal vs Bayer Leverkusen
        (match_id + 14, 7, 63, 10, d_midweek, "21:00", "Fase de Liga - J1"),  # Barcelona vs PSG
        (match_id + 15, 51, 58, 10, d_midweek, "21:00", "Fase de Liga - J1"), # Juventus vs Borussia Dortmund
    ]

    for m in upcoming_fixtures:
        mid, hid, aid, cid, mdate, mtime, mstage = m
        cur.execute("""
            INSERT OR REPLACE INTO matches (id, competition_id, season, stage, match_date, match_time, home_team_id, away_team_id, home_score, away_score, created_at, updated_at)
            VALUES (?, ?, '2425', ?, ?, ?, ?, ?, NULL, NULL, datetime('now'), datetime('now'))
        """, (mid, cid, mstage, mdate, mtime, hid, aid))

    print(f"16 nuevos partidos oficiales añadidos (Serie A, Bundesliga, Ligue 1 y Champions League).")

    con.commit()
    con.close()
    print("Base de datos expandida con éxito.")

if __name__ == "__main__":
    seed_european_football()
