"""
Script de sincronización oficial de UEFA Champions League desde la API de ESPN.
1. Registra nuevos clubes participantes europeos en 'teams'.
2. Registra rankings ELO iniciales en 'rankings'.
3. Registra jugadores clave en 'players' y 'player_stats'.
4. Elimina partidos simulados/falsos de UCL en 'matches'.
5. Inserta los 36 partidos oficiales de Fase de Liga de Champions League (J1 y J2):
   - 2026-09-08 (Finalizados con resultados oficiales)
   - 2026-09-09 (Partidos de HOY programados)
   - 2026-09-10 (Partidos de MAÑANA programados)
   - 2026-10-13 y 2026-10-14 (Jornada 2 programada)
"""

import json
import sqlite3
import urllib.request
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "prediccion.db"

# 1. Definición de nuevos clubes europeos
NEW_CLUBS_DATA = [
    # name, full_name, code, country, confederation, founded, elo, logo_url
    ("AEK Athens", "AEK Athens Football Club", "AEK", "Greece", "UEFA", 1924, 1580.0, "https://a.espncdn.com/i/teamlogos/soccer/500/2153.png"),
    ("LASK Linz", "Linzer Athletik-Sport-Klub", "LSK", "Austria", "UEFA", 1908, 1560.0, "https://a.espncdn.com/i/teamlogos/soccer/500/4094.png"),
    ("Club Brugge", "Club Brugge Koninklijke Voetbalvereniging", "CLU", "Belgium", "UEFA", 1891, 1680.0, "https://a.espncdn.com/i/teamlogos/soccer/500/188.png"),
    ("FC Porto", "Futebol Clube do Porto", "POR", "Portugal", "UEFA", 1893, 1780.0, "https://a.espncdn.com/i/teamlogos/soccer/500/437.png"),
    ("Feyenoord", "Feyenoord Rotterdam", "FEY", "Netherlands", "UEFA", 1908, 1740.0, "https://a.espncdn.com/i/teamlogos/soccer/500/139.png"),
    ("Viking FK", "Viking Fotballklubb", "VIK", "Norway", "UEFA", 1899, 1540.0, "https://a.espncdn.com/i/teamlogos/soccer/500/1031.png"),
    ("Slovan Bratislava", "ŠK Slovan Bratislava", "SLO", "Slovakia", "UEFA", 1919, 1520.0, "https://a.espncdn.com/i/teamlogos/soccer/500/2205.png"),
    ("Sporting CP", "Sporting Clube de Portugal", "SCP", "Portugal", "UEFA", 1906, 1810.0, "https://a.espncdn.com/i/teamlogos/soccer/500/439.png"),
    ("Galatasaray", "Galatasaray Spor Kulübü", "GAL", "Turkey", "UEFA", 1905, 1720.0, "https://a.espncdn.com/i/teamlogos/soccer/500/432.png"),
    ("Fenerbahce", "Fenerbahçe Spor Kulübü", "FEN", "Turkey", "UEFA", 1907, 1710.0, "https://a.espncdn.com/i/teamlogos/soccer/500/431.png"),
    ("PSV Eindhoven", "Philips Sport Vereniging Eindhoven", "PSV", "Netherlands", "UEFA", 1913, 1760.0, "https://a.espncdn.com/i/teamlogos/soccer/500/148.png"),
    ("Shakhtar Donetsk", "FC Shakhtar Donetsk", "SHK", "Ukraine", "UEFA", 1936, 1670.0, "https://a.espncdn.com/i/teamlogos/soccer/500/627.png"),
    ("Bodo/Glimt", "FK Bodø/Glimt", "BOD", "Norway", "UEFA", 1916, 1630.0, "https://a.espncdn.com/i/teamlogos/soccer/500/2747.png"),
    ("Como", "Como 1907", "COM", "Italy", "UEFA", 1907, 1610.0, "https://a.espncdn.com/i/teamlogos/soccer/500/2697.png"),
    ("Sabah FK", "Sabah Futbol Klubu", "SAB", "Azerbaijan", "UEFA", 2017, 1490.0, "https://a.espncdn.com/i/teamlogos/soccer/500/20340.png"),
    ("Slavia Prague", "SK Slavia Praha", "SLA", "Czech Republic", "UEFA", 1892, 1660.0, "https://a.espncdn.com/i/teamlogos/soccer/500/2157.png"),
    ("RC Lens", "Racing Club de Lens", "RCL", "France", "UEFA", 1906, 1690.0, "https://a.espncdn.com/i/teamlogos/soccer/500/165.png"),
]

# 2. Mapeo de nombres ESPN a nombres en base de datos
ESPN_NAME_MAP = {
    "Real Madrid": "Real Madrid",
    "Barcelona": "Barcelona",
    "Ath Madrid": "Ath Madrid",
    "Atlético Madrid": "Ath Madrid",
    "Atltico Madrid": "Ath Madrid",
    "Villarreal": "Villarreal",
    "Real Betis": "Betis",
    "Manchester City": "Man City",
    "Arsenal": "Arsenal",
    "Liverpool": "Liverpool",
    "Aston Villa": "Aston Villa",
    "Manchester United": "Man United",
    "Internazionale": "Inter de Milan",
    "Inter de Milan": "Inter de Milan",
    "Inter de Milán": "Inter de Milan",
    "Napoli": "Napoli",
    "AS Roma": "AS Roma",
    "Bayern Munich": "Bayern Munich",
    "Bayern Múnich": "Bayern Munich",
    "Borussia Dortmund": "Borussia Dortmund",
    "VfB Stuttgart": "VfB Stuttgart",
    "RB Leipzig": "RB Leipzig",
    "Paris Saint-Germain": "Paris Saint-Germain",
    "Lille": "Lille OSC",
    "Lille OSC": "Lille OSC",
    "AEK Athens": "AEK Athens",
    "LASK Linz": "LASK Linz",
    "Club Brugge": "Club Brugge",
    "FC Porto": "FC Porto",
    "Feyenoord Rotterdam": "Feyenoord",
    "Feyenoord": "Feyenoord",
    "Viking FK": "Viking FK",
    "Slovan Bratislava": "Slovan Bratislava",
    "Sporting CP": "Sporting CP",
    "Galatasaray": "Galatasaray",
    "Fenerbahce": "Fenerbahce",
    "PSV Eindhoven": "PSV Eindhoven",
    "Shakhtar Donetsk": "Shakhtar Donetsk",
    "Bodo/Glimt": "Bodo/Glimt",
    "Como": "Como",
    "Sabah FK": "Sabah FK",
    "Slavia Prague": "Slavia Prague",
    "Lens": "RC Lens",
    "RC Lens": "RC Lens",
}

# 3. Jugadores representativos para cada club nuevo
SAMPLE_PLAYERS = {
    "Feyenoord": [
        ("Timon Wellenreuther", "GK", 1, 7.2, 4_000_000),
        ("David Hancko", "DF", 3, 7.6, 35_000_000),
        ("Gernot Trauner", "DF", 18, 7.1, 5_000_000),
        ("Quinten Timber", "MF", 8, 7.7, 30_000_000),
        ("Calvin Stengs", "MF", 10, 7.4, 15_000_000),
        ("Santiago Giménez", "FW", 29, 7.8, 45_000_000),
        ("Igor Paixão", "FW", 14, 7.3, 14_000_000),
    ],
    "Sporting CP": [
        ("Franco Israel", "GK", 1, 7.1, 8_000_000),
        ("Gonçalo Inácio", "DF", 25, 7.6, 45_000_000),
        ("Ousmane Diomande", "DF", 26, 7.5, 40_000_000),
        ("Morten Hjulmand", "MF", 42, 7.7, 40_000_000),
        ("Pedro Gonçalves", "MF", 8, 7.8, 32_000_000),
        ("Viktor Gyökeres", "FW", 9, 8.4, 70_000_000),
        ("Francisco Trincão", "FW", 17, 7.5, 20_000_000),
    ],
    "Galatasaray": [
        ("Fernando Muslera", "GK", 1, 7.3, 2_000_000),
        ("Davinson Sánchez", "DF", 6, 7.5, 18_000_000),
        ("Abdulkerim Bardakci", "DF", 42, 7.2, 9_000_000),
        ("Lucas Torreira", "MF", 34, 7.6, 15_000_000),
        ("Gabriel Sara", "MF", 20, 7.4, 20_000_000),
        ("Mauro Icardi", "FW", 9, 7.7, 15_000_000),
        ("Victor Osimhen", "FW", 45, 8.3, 75_000_000),
    ],
    "PSV Eindhoven": [
        ("Walter Benítez", "GK", 1, 7.3, 12_000_000),
        ("Olivier Boscagli", "DF", 18, 7.4, 27_000_000),
        ("Ryan Flamingo", "DF", 6, 7.1, 10_000_000),
        ("Jerdy Schouten", "MF", 22, 7.7, 28_000_000),
        ("Joey Veerman", "MF", 23, 7.8, 35_000_000),
        ("Luuk de Jong", "FW", 9, 7.6, 5_000_000),
        ("Johan Bakayoko", "FW", 11, 7.7, 45_000_000),
    ],
    "FC Porto": [
        ("Diogo Costa", "GK", 99, 7.8, 45_000_000),
        ("Nehuén Pérez", "DF", 24, 7.3, 13_000_000),
        ("Zé Pedro", "DF", 97, 7.0, 5_000_000),
        ("Alan Varela", "MF", 22, 7.7, 35_000_000),
        ("Nico González", "MF", 16, 7.5, 18_000_000),
        ("Samu Omorodion", "FW", 9, 7.6, 35_000_000),
        ("Galeno", "FW", 13, 7.6, 25_000_000),
    ],
    "Viking FK": [
        ("Patrik Gunnarsson", "GK", 1, 6.9, 1_500_000),
        ("David Brekalo", "DF", 4, 7.0, 3_000_000),
        ("Gianni Stensness", "DF", 3, 6.8, 1_200_000),
        ("Joe Bell", "MF", 8, 7.1, 2_500_000),
        ("Zlatko Tripic", "FW", 10, 7.3, 2_000_000),
    ],
    "Slovan Bratislava": [
        ("Dominik Takác", "GK", 1, 6.9, 1_200_000),
        ("Guram Kashia", "DF", 4, 6.8, 500_000),
        ("Kenan Bajric", "DF", 6, 6.8, 1_000_000),
        ("Juraj Kucka", "MF", 33, 7.1, 1_000_000),
        ("Tigran Barseghyan", "FW", 11, 7.3, 2_500_000),
        ("David Strelec", "FW", 13, 7.2, 3_000_000),
    ],
    "Club Brugge": [
        ("Simon Mignolet", "GK", 22, 7.2, 3_000_000),
        ("Brandon Mechele", "DF", 44, 7.0, 4_000_000),
        ("Maxim De Cuyper", "DF", 55, 7.4, 12_000_000),
        ("Raphael Onyedika", "MF", 15, 7.4, 15_000_000),
        ("Hans Vanaken", "MF", 20, 7.7, 8_000_000),
        ("Christos Tzolis", "FW", 8, 7.5, 12_000_000),
    ],
    "Fenerbahce": [
        ("Dominik Livakovic", "GK", 40, 7.4, 11_000_000),
        ("Alexander Djiku", "DF", 6, 7.2, 9_000_000),
        ("Caglar Söyüncü", "DF", 2, 7.3, 10_000_000),
        ("Fred", "MF", 13, 7.7, 15_000_000),
        ("Sofyan Amrabat", "MF", 34, 7.5, 22_000_000),
        ("Edin Dzeko", "FW", 9, 7.6, 3_000_000),
        ("Youssef En-Nesyri", "FW", 19, 7.5, 22_000_000),
    ],
    "Bodo/Glimt": [
        ("Nikita Haikin", "GK", 12, 7.1, 2_000_000),
        ("Jostein Gundersen", "DF", 6, 7.0, 2_500_000),
        ("Patrick Berg", "MF", 7, 7.5, 5_000_000),
        ("Hakons Evjen", "MF", 10, 7.2, 3_000_000),
        ("Jens Petter Hauge", "FW", 23, 7.4, 4_000_000),
    ],
    "Como": [
        ("Emil Audero", "GK", 1, 7.1, 5_000_000),
        ("Alberto Dossena", "DF", 4, 7.1, 6_000_000),
        ("Sergi Roberto", "MF", 20, 7.2, 4_000_000),
        ("Nico Paz", "MF", 79, 7.7, 15_000_000),
        ("Patrick Cutrone", "FW", 10, 7.3, 5_000_000),
    ],
    "RC Lens": [
        ("Brice Samba", "GK", 30, 7.5, 15_000_000),
        ("Facundo Medina", "DF", 14, 7.5, 25_000_000),
        ("Kevin Danso", "DF", 4, 7.6, 25_000_000),
        ("Andy Diouf", "MF", 18, 7.3, 12_000_000),
        ("Florian Sotoca", "FW", 7, 7.2, 4_000_000),
    ],
    "Slavia Prague": [
        ("Antonin Kinsky", "GK", 1, 7.0, 3_000_000),
        ("Tomas Holes", "DF", 3, 7.2, 3_500_000),
        ("David Doudera", "MF", 21, 7.2, 4_000_000),
        ("Lukas Provod", "MF", 17, 7.5, 6_000_000),
        ("Tomas Chory", "FW", 25, 7.3, 3_500_000),
    ],
    "Shakhtar Donetsk": [
        ("Dmytro Riznyk", "GK", 31, 7.1, 7_000_000),
        ("Mykola Matviyenko", "DF", 22, 7.4, 18_000_000),
        ("Georgiy Sudakov", "MF", 10, 7.9, 35_000_000),
        ("Artem Bondarenko", "MF", 21, 7.3, 9_000_000),
        ("Danylo Sikan", "FW", 14, 7.2, 7_000_000),
    ],
    "AEK Athens": [
        ("Thomas Strakosha", "GK", 1, 7.1, 3_000_000),
        ("Domagoj Vida", "DF", 21, 7.0, 1_500_000),
        ("Orbelín Pineda", "MF", 13, 7.5, 7_000_000),
        ("Levi García", "FW", 11, 7.4, 12_000_000),
    ],
    "LASK Linz": [
        ("Jörg Siebenhandl", "GK", 28, 6.9, 800_000),
        ("Philipp Ziereis", "DF", 5, 7.0, 1_200_000),
        ("Sascha Horvath", "MF", 30, 7.1, 2_000_000),
        ("Marin Ljubicic", "FW", 9, 7.3, 4_000_000),
    ],
    "Sabah FK": [
        ("Nijat Mehbaliyev", "GK", 1, 6.7, 500_000),
        ("Sofian Chakla", "DF", 4, 6.9, 1_000_000),
        ("Aleksey Isayev", "MF", 8, 7.0, 1_200_000),
        ("Pavol Safranko", "FW", 18, 7.0, 1_000_000),
    ]
}


def sync_ucl():
    import unicodedata
    def norm(s):
        return unicodedata.normalize('NFKD', str(s)).encode('ASCII', 'ignore').decode('utf-8').lower().strip()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== PASO 1: Upsert de Nuevos Clubes Europeos en 'teams' ===")
    team_name_to_id = {}
    for row in cur.execute("SELECT id, name FROM teams"):
        team_name_to_id[row[1]] = row[0]
        team_name_to_id[norm(row[1])] = row[0]

    for name, fname, code, country, conf, founded, elo, logo in NEW_CLUBS_DATA:
        if name not in team_name_to_id:
            cur.execute("""
                INSERT INTO teams (name, full_name, code, country, confederation, founded_year, logo_url, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (name, fname, code, country, conf, founded, logo))
            new_id = cur.lastrowid
            team_name_to_id[name] = new_id
            print(f"  + Creado club: {name} (ID {new_id}, {code}, {country})")
            
            # Ranking ELO
            cur.execute("""
                INSERT INTO rankings (team_id, ranking_type, rank, points, change_points, rank_date, created_at)
                VALUES (?, 'elo', 0, ?, 0, '2026-09-08', datetime('now'))
            """, (new_id, elo))
        else:
            tid = team_name_to_id[name]
            cur.execute("UPDATE teams SET code = ?, country = ?, logo_url = ? WHERE id = ?", (code, country, logo, tid))
            print(f"  * Actualizado club existente: {name} (ID {tid})")

    conn.commit()

    print("\n=== PASO 2: Jugadores y estadísticas de plantilla para nuevos clubes ===")
    for team_name, players in SAMPLE_PLAYERS.items():
        tid = team_name_to_id.get(team_name)
        if not tid:
            continue
        for p_name, pos, num, rating, mval in players:
            cur.execute("SELECT id FROM players WHERE name = ? AND team_id = ?", (p_name, tid))
            p_row = cur.fetchone()
            if not p_row:
                cur.execute("""
                    INSERT INTO players (name, full_name, team_id, position, position_detail, shirt_number, market_value_eur, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """, (p_name, p_name, tid, pos, pos, num, mval))
                pid = cur.lastrowid
                cur.execute("""
                    INSERT INTO player_stats (match_id, player_id, team_id, position, rating, minutes_played, goals, assists, created_at)
                    VALUES (2450, ?, ?, ?, ?, 90, 0, 0, datetime('now'))
                """, (pid, tid, pos, rating))
    conn.commit()
    print("  Jugadores y ratings registrados correctamente.")

    print("\n=== PASO 3: Fetch de Partidos Oficiales de UEFA Champions League desde ESPN ===")
    dates = ["20260908", "20260909", "20260910", "20261013", "20261014"]
    espn_matches = []

    for d in dates:
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/scoreboard?dates={d}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                events = data.get("events", [])
                for ev in events:
                    comp = ev.get("competitions", [{}])[0]
                    competitors = comp.get("competitors", [])
                    h_c = next((c for c in competitors if c.get("homeAway") == "home"), {})
                    a_c = next((c for c in competitors if c.get("homeAway") == "away"), {})
                    h_name_raw = h_c.get("team", {}).get("displayName", "")
                    a_name_raw = a_c.get("team", {}).get("displayName", "")
                    
                    h_name = ESPN_NAME_MAP.get(h_name_raw, h_name_raw)
                    a_name = ESPN_NAME_MAP.get(a_name_raw, a_name_raw)

                    h_id = team_name_to_id.get(h_name) or team_name_to_id.get(norm(h_name))
                    a_id = team_name_to_id.get(a_name) or team_name_to_id.get(norm(a_name))

                    if not h_id or not a_id:
                        print(f"  [AVISO] No se encontró ID para '{h_name_raw}' ({h_id}) o '{a_name_raw}' ({a_id})")
                        continue

                    # Parse datetime
                    iso_date = ev.get("date", "")
                    dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
                    m_date = dt.strftime("%Y-%m-%d")
                    m_time = dt.strftime("%H:%M:%S")

                    # Status
                    status_type = ev.get("status", {}).get("type", {}).get("name", "")
                    is_completed = status_type in ("STATUS_FINAL", "STATUS_FULL_TIME") or ev.get("status", {}).get("type", {}).get("completed", False)
                    
                    h_score = int(h_c.get("score")) if is_completed and h_c.get("score") is not None else None
                    a_score = int(a_c.get("score")) if is_completed and a_c.get("score") is not None else None

                    stage = "Fase de Liga - J1" if d in ("20260908", "20260909", "20260910") else "Fase de Liga - J2"
                    venue = comp.get("venue", {}).get("fullName")

                    espn_matches.append({
                        "espn_id": ev.get("id"),
                        "date": m_date,
                        "time": m_time,
                        "home_id": h_id,
                        "away_id": a_id,
                        "home_name": h_name,
                        "away_name": a_name,
                        "home_score": h_score,
                        "away_score": a_score,
                        "is_completed": is_completed,
                        "stage": stage,
                        "venue": venue,
                    })
        except Exception as ex:
            print(f"Error consultando ESPN para {d}: {ex}")

    print(f"Total de partidos oficiales obtenidos de ESPN: {len(espn_matches)}")

    print("\n=== PASO 4: Limpieza de partidos simulados e inserción de partidos oficiales ===")
    cur.execute("DELETE FROM matches WHERE competition_id = 10 AND (season = '2425' OR match_date >= '2026-08-01')")
    print(f"  Partidos simulados previos de UCL eliminados.")

    # Insertar partidos oficiales
    inserted_count = 0
    for m in espn_matches:
        cur.execute("""
            INSERT INTO matches (
                competition_id, season, stage, match_date, match_time,
                home_team_id, away_team_id, home_score, away_score,
                venue, created_at, updated_at
            ) VALUES (10, '2425', ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            m["stage"], m["date"], m["time"],
            m["home_id"], m["away_id"],
            m["home_score"], m["away_score"],
            m["venue"]
        ))
        inserted_count += 1
        st_text = f"{m['home_score']}-{m['away_score']}" if m['is_completed'] else "PROGRAMADO"
        print(f"  + Insertado: {m['date']} {m['time']} | {m['home_name']} vs {m['away_name']} [{st_text}]")

    conn.commit()
    print(f"\nSincronización completada con éxito. {inserted_count} partidos auténticos insertados en la base de datos.")

    cur.execute("""
        SELECT COUNT(*) FROM matches
        WHERE competition_id = 10 AND home_score IS NULL AND match_date = '2026-09-09'
    """)
    today_count = cur.fetchone()[0]
    print(f"Partidos oficiales de UCL para HOY (2026-09-09): {today_count}")

    conn.close()

if __name__ == "__main__":
    sync_ucl()
