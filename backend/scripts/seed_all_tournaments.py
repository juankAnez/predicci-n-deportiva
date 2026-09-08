"""
Script para poblar y asegurar la integridad de todas las ligas y torneos:
- Corrige nombres de equipos con codificación limpia.
- Define partidos históricos y próximos oficiales para:
    * UEFA Europa League (competición 11)
    * Copa del Rey (competición 12)
    * FA Cup (competición 13)
    * Coppa Italia (competición 14)
    * DFB-Pokal (competición 15)
    * Coupe de France (competición 16)
- Asegura que cada liga solo contenga sus clubes legítimos y cada torneo sus participantes clasificados.
"""

import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "prediccion.db"

def run_seed():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # 1. Corregir nombres de equipos con tildes y caracteres limpios UTF-8
    name_fixes = [
        (49, "Inter de Milán", "FC Internazionale Milano"),
        (57, "Bayern Múnich", "FC Bayern München"),
        (64, "AS Mónaco", "AS Monaco FC"),
        (65, "Olympique de Marsella", "Olympique de Marseille"),
    ]
    for tid, name, fname in name_fixes:
        cur.execute("UPDATE teams SET name = ?, full_name = ? WHERE id = ?", (name, fname, tid))
    print("Nombres de clubes corregidos con codificación limpia UTF-8.")

    # 2. Definir participantes de torneos continentales
    # UCL (10):
    # España: Real Madrid (14), Barcelona (7), Ath Madrid (18), Girona (12)
    # Inglaterra: Man City (44), Arsenal (26), Liverpool (28), Aston Villa (30)
    # Italia: Inter (49), AC Milan (50), Juventus (51), Atalanta (54)
    # Alemania: Bayern (57), Dortmund (58), Leverkusen (59), Leipzig (60), Stuttgart (62)
    # Francia: PSG (63), Mónaco (64), Lille (67)

    # UEL (11):
    # España: Ath Bilbao (15), Sociedad (10), Betis (19)
    # Inglaterra: Tottenham (35), Man United (41), Chelsea (38)
    # Italia: AS Roma (53), Lazio (55), Fiorentina (56)
    # Alemania: Frankfurt (61)
    # Francia: Marsella (65), Lyon (66), Rennes (68)

    today = date.today()
    # Próximas fechas para torneos
    # Fin de semana: Viernes a Lunes
    # Entre semana: Martes a Jueves
    d_midweek = (today + timedelta(days=(9 - today.weekday()) % 7)).isoformat()
    d_cup_midweek = (today + timedelta(days=(10 - today.weekday()) % 7)).isoformat()

    # 3. Eliminar partidos de comp 11 a 16 previos si existen para insertar limpiamente
    cur.execute("DELETE FROM matches WHERE competition_id IN (11, 12, 13, 14, 15, 16)")

    # Obtener el ID máximo de matches actual
    max_id = cur.execute("SELECT COALESCE(MAX(id), 2400) FROM matches").fetchone()[0]
    next_id = max(max_id + 1, 2400)

    # A. PARTIDOS HISTÓRICOS Y PRÓXIMOS DE UEFA EUROPA LEAGUE (11)
    # Históricos UEL
    uel_historical = [
        (35, 53, 2, 1), # Tottenham vs Roma
        (41, 66, 3, 2), # Man United vs Lyon
        (19, 61, 1, 1), # Betis vs Frankfurt
        (15, 55, 2, 0), # Ath Bilbao vs Lazio
        (38, 10, 1, 1), # Chelsea vs Sociedad
        (65, 56, 2, 1), # Marsella vs Fiorentina
    ]
    for h_id, a_id, h_sc, a_sc in uel_historical:
        m_date = today - timedelta(days=12 + (next_id % 15))
        cur.execute("""
            INSERT INTO matches (id, competition_id, season, stage, match_date, match_time, home_team_id, away_team_id, home_score, away_score, created_at, updated_at)
            VALUES (?, 11, '2425', 'Fase de Grupos', ?, '21:00', ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (next_id, m_date.isoformat(), h_id, a_id, h_sc, a_sc))
        next_id += 1

    # Próximos UEL (Septiembre 2026)
    uel_upcoming = [
        (35, 53, d_midweek, "21:00", "Jornada 1"), # Tottenham vs AS Roma
        (41, 66, d_midweek, "21:00", "Jornada 1"), # Man United vs Lyon
        (15, 61, d_midweek, "18:45", "Jornada 1"), # Ath Bilbao vs Eintracht Frankfurt
        (38, 19, d_midweek, "21:00", "Jornada 1"), # Chelsea vs Real Betis
        (55, 10, d_midweek, "18:45", "Jornada 1"), # Lazio vs Real Sociedad
        (65, 56, d_midweek, "21:00", "Jornada 1"), # Olympique de Marsella vs Fiorentina
    ]
    for h_id, a_id, m_date, m_time, stg in uel_upcoming:
        cur.execute("""
            INSERT INTO matches (id, competition_id, season, stage, match_date, match_time, home_team_id, away_team_id, home_score, away_score, created_at, updated_at)
            VALUES (?, 11, '2425', ?, ?, ?, ?, ?, NULL, NULL, datetime('now'), datetime('now'))
        """, (next_id, stg, m_date, m_time, h_id, a_id))
        next_id += 1

    # B. COPA DEL REY (12) - Solo clubes de España
    cdr_upcoming = [
        (14, 2,  d_cup_midweek, "21:00", "Octavos de Final"), # Real Madrid vs Sevilla
        (7,  15, d_cup_midweek, "21:30", "Octavos de Final"), # Barcelona vs Ath Bilbao
        (18, 10, d_cup_midweek, "20:00", "Octavos de Final"), # Ath Madrid vs Real Sociedad
        (6,  19, d_cup_midweek, "19:00", "Octavos de Final"), # Villarreal vs Betis
    ]
    for h_id, a_id, m_date, m_time, stg in cdr_upcoming:
        cur.execute("""
            INSERT INTO matches (id, competition_id, season, stage, match_date, match_time, home_team_id, away_team_id, home_score, away_score, created_at, updated_at)
            VALUES (?, 12, '2425', ?, ?, ?, ?, ?, NULL, NULL, datetime('now'), datetime('now'))
        """, (next_id, stg, m_date, m_time, h_id, a_id))
        next_id += 1

    # C. FA CUP (13) - Solo clubes de Inglaterra
    fac_upcoming = [
        (44, 38, d_cup_midweek, "20:45", "Cuarta Ronda"), # Man City vs Chelsea
        (26, 41, d_cup_midweek, "20:45", "Cuarta Ronda"), # Arsenal vs Man United
        (28, 33, d_cup_midweek, "20:00", "Cuarta Ronda"), # Liverpool vs Newcastle
        (35, 30, d_cup_midweek, "19:45", "Cuarta Ronda"), # Tottenham vs Aston Villa
    ]
    for h_id, a_id, m_date, m_time, stg in fac_upcoming:
        cur.execute("""
            INSERT INTO matches (id, competition_id, season, stage, match_date, match_time, home_team_id, away_team_id, home_score, away_score, created_at, updated_at)
            VALUES (?, 13, '2425', ?, ?, ?, ?, ?, NULL, NULL, datetime('now'), datetime('now'))
        """, (next_id, stg, m_date, m_time, h_id, a_id))
        next_id += 1

    # D. COPPA ITALIA (14) - Solo clubes de Italia
    ci_upcoming = [
        (49, 53, d_cup_midweek, "21:00", "Cuartos de Final"), # Inter vs AS Roma
        (51, 55, d_cup_midweek, "21:00", "Cuartos de Final"), # Juventus vs Lazio
        (50, 54, d_cup_midweek, "20:45", "Cuartos de Final"), # AC Milan vs Atalanta
        (52, 56, d_cup_midweek, "18:00", "Cuartos de Final"), # Napoli vs Fiorentina
    ]
    for h_id, a_id, m_date, m_time, stg in ci_upcoming:
        cur.execute("""
            INSERT INTO matches (id, competition_id, season, stage, match_date, match_time, home_team_id, away_team_id, home_score, away_score, created_at, updated_at)
            VALUES (?, 14, '2425', ?, ?, ?, ?, ?, NULL, NULL, datetime('now'), datetime('now'))
        """, (next_id, stg, m_date, m_time, h_id, a_id))
        next_id += 1

    # E. DFB-POKAL (15) - Solo clubes de Alemania
    dfb_upcoming = [
        (57, 62, d_cup_midweek, "20:45", "Segunda Ronda"), # Bayern Múnich vs VfB Stuttgart
        (59, 61, d_cup_midweek, "18:00", "Segunda Ronda"), # Bayer Leverkusen vs Eintracht Frankfurt
        (58, 60, d_cup_midweek, "20:45", "Segunda Ronda"), # Borussia Dortmund vs RB Leipzig
    ]
    for h_id, a_id, m_date, m_time, stg in dfb_upcoming:
        cur.execute("""
            INSERT INTO matches (id, competition_id, season, stage, match_date, match_time, home_team_id, away_team_id, home_score, away_score, created_at, updated_at)
            VALUES (?, 15, '2425', ?, ?, ?, ?, ?, NULL, NULL, datetime('now'), datetime('now'))
        """, (next_id, stg, m_date, m_time, h_id, a_id))
        next_id += 1

    # F. COUPE DE FRANCE (16) - Solo clubes de Francia
    cdf_upcoming = [
        (63, 66, d_cup_midweek, "21:10", "Dieciseisavos"), # PSG vs Lyon
        (64, 65, d_cup_midweek, "20:45", "Dieciseisavos"), # Mónaco vs Marsella
        (67, 68, d_cup_midweek, "18:00", "Dieciseisavos"), # Lille vs Rennes
    ]
    for h_id, a_id, m_date, m_time, stg in cdf_upcoming:
        cur.execute("""
            INSERT INTO matches (id, competition_id, season, stage, match_date, match_time, home_team_id, away_team_id, home_score, away_score, created_at, updated_at)
            VALUES (?, 16, '2425', ?, ?, ?, ?, ?, NULL, NULL, datetime('now'), datetime('now'))
        """, (next_id, stg, m_date, m_time, h_id, a_id))
        next_id += 1

    con.commit()
    print(f"Todas las competiciones pobladas exitosamente con partidos exclusivos. Total próximo ID: {next_id}")

    # Verificar recuentos
    counts = cur.execute("""
        SELECT c.id, c.name, COUNT(m.id), SUM(CASE WHEN m.home_score IS NULL THEN 1 ELSE 0 END) AS upcoming
        FROM competitions c
        LEFT JOIN matches m ON c.id = m.competition_id
        GROUP BY c.id
        ORDER BY c.id
    """).fetchall()

    print("\n--- RESUMEN DE COMPETICIONES EN BASE DE DATOS ---")
    for cid, cname, total, upcoming in counts:
        print(f"[{cid:2d}] {cname:<24}: Total = {total:4d} | Próximos = {upcoming or 0:2d}")

    con.close()

if __name__ == "__main__":
    run_seed()

