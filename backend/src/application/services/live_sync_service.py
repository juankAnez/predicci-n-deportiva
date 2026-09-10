"""
Live Match & Result Synchronization Service.
Automatically queries official sports APIs (ESPN Soccer) to:
1. Ingest finished match scores (updating matches table and converting them to historical records).
2. Add new upcoming fixtures and schedules.
3. Automatically run on backend startup, on background intervals, or on user demand.
"""

import json
import logging
import sqlite3
import threading
import time
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "prediccion.db"


def norm(s: Any) -> str:
    if not s:
        return ""
    return unicodedata.normalize("NFKD", str(s)).encode("ASCII", "ignore").decode("utf-8").lower().strip()


# ESPN league slugs mapped to competition IDs
LEAGUE_CONFIGS = [
    {"slug": "uefa.champions", "comp_id": 10, "name": "UEFA Champions League", "default_stage": "Fase de Liga"},
    {"slug": "uefa.europa",    "comp_id": 11, "name": "UEFA Europa League",    "default_stage": "Fase de Grupos"},
    {"slug": "esp.1",          "comp_id": 3,  "name": "La Liga",                "default_stage": "Jornada Regular"},
    {"slug": "eng.1",          "comp_id": 6,  "name": "Premier League",         "default_stage": "Jornada Regular"},
    {"slug": "ita.1",          "comp_id": 7,  "name": "Serie A",                "default_stage": "Jornada Regular"},
    {"slug": "ger.1",          "comp_id": 8,  "name": "Bundesliga",             "default_stage": "Jornada Regular"},
    {"slug": "fra.1",          "comp_id": 9,  "name": "Ligue 1",                "default_stage": "Jornada Regular"},
]

# Common name translations
ESPN_NAME_MAP = {
    "real madrid": "real madrid",
    "barcelona": "barcelona",
    "ath madrid": "ath madrid",
    "atletico madrid": "ath madrid",
    "villarreal": "villarreal",
    "real betis": "betis",
    "betis": "betis",
    "manchester city": "man city",
    "man city": "man city",
    "arsenal": "arsenal",
    "liverpool": "liverpool",
    "aston villa": "aston villa",
    "manchester united": "man united",
    "man united": "man united",
    "internazionale": "inter de milan",
    "inter milan": "inter de milan",
    "inter": "inter de milan",
    "inter de milan": "inter de milan",
    "napoli": "napoli",
    "as roma": "as roma",
    "roma": "as roma",
    "bayern munich": "bayern munich",
    "bayern munchen": "bayern munich",
    "borussia dortmund": "borussia dortmund",
    "dortmund": "borussia dortmund",
    "bvb": "borussia dortmund",
    "vfb stuttgart": "vfb stuttgart",
    "stuttgart": "vfb stuttgart",
    "rb leipzig": "rb leipzig",
    "leipzig": "rb leipzig",
    "paris saint-germain": "paris saint-germain",
    "psg": "paris saint-germain",
    "lille": "lille osc",
    "lille osc": "lille osc",
    "feyenoord rotterdam": "feyenoord",
    "feyenoord": "feyenoord",
    "sporting cp": "sporting cp",
    "sporting lisbon": "sporting cp",
    "galatasaray": "galatasaray",
    "fenerbahce": "fenerbahce",
    "psv eindhoven": "psv eindhoven",
    "psv": "psv eindhoven",
    "shakhtar donetsk": "shakhtar donetsk",
    "shakhtar": "shakhtar donetsk",
    "bodo/glimt": "bodo/glimt",
    "como": "como",
    "como 1907": "como",
    "sabah fk": "sabah fk",
    "sabah": "sabah fk",
    "slavia prague": "slavia prague",
    "slavia praha": "slavia prague",
    "lens": "rc lens",
    "rc lens": "rc lens",
    "aek athens": "aek athens",
    "lask linz": "lask linz",
    "lask": "lask linz",
    "viking fk": "viking fk",
    "viking": "viking fk",
    "slovan bratislava": "slovan bratislava",
    "club brugge": "club brugge",
    "fc porto": "fc porto",
    "porto": "fc porto",
}


class LiveSyncService:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH

    def _get_team_mappings(self, cur: sqlite3.Cursor) -> Dict[str, int]:
        mapping = {}
        for row in cur.execute("SELECT id, name, full_name, code FROM teams"):
            tid = row[0]
            if row[1]:
                mapping[norm(row[1])] = tid
            if row[2]:
                mapping[norm(row[2])] = tid
            if row[3]:
                mapping[norm(row[3])] = tid
        return mapping

    def sync_all(self, days_back: int = 3, days_ahead: int = 3) -> Dict[str, Any]:
        """
        Synchronizes live match scores and schedules from ESPN API for all competitions.
        """
        print("[Auto-Sincronizador] Conectando en tiempo real con ESPN Sports API para sincronizar resultados y calendarios...")
        start_time = time.time()
        today = date.today()
        dates_to_sync = [
            (today - timedelta(days=d)).strftime("%Y%m%d")
            for d in range(days_back, 0, -1)
        ] + [
            (today + timedelta(days=d)).strftime("%Y%m%d")
            for d in range(0, days_ahead + 1)
        ]

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        team_map = self._get_team_mappings(cur)
        scores_updated = 0
        matches_created = 0
        events_processed = 0

        for league_cfg in LEAGUE_CONFIGS:
            slug = league_cfg["slug"]
            comp_id = league_cfg["comp_id"]
            default_stage = league_cfg["default_stage"]

            for d_str in dates_to_sync:
                url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard?dates={d_str}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                try:
                    with urllib.request.urlopen(req, timeout=8) as r:
                        data = json.loads(r.read().decode())
                        events = data.get("events", [])
                        for ev in events:
                            events_processed += 1
                            comp = ev.get("competitions", [{}])[0]
                            competitors = comp.get("competitors", [])
                            h_c = next((c for c in competitors if c.get("homeAway") == "home"), {})
                            a_c = next((c for c in competitors if c.get("homeAway") == "away"), {})

                            h_raw = h_c.get("team", {}).get("displayName", "")
                            a_raw = a_c.get("team", {}).get("displayName", "")

                            h_norm = ESPN_NAME_MAP.get(norm(h_raw), norm(h_raw))
                            a_norm = ESPN_NAME_MAP.get(norm(a_raw), norm(a_raw))

                            h_id = team_map.get(h_norm)
                            a_id = team_map.get(a_norm)

                            if not h_id or not a_id:
                                continue

                            # Parse date & time
                            iso_date = ev.get("date", "")
                            try:
                                dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
                                m_date = dt.strftime("%Y-%m-%d")
                                m_time = dt.strftime("%H:%M:%S")
                            except Exception:
                                m_date = f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:]}"
                                m_time = "19:00:00"

                            # Status & scores
                            status_type = ev.get("status", {}).get("type", {}).get("name", "")
                            is_completed = (
                                status_type in ("STATUS_FINAL", "STATUS_FULL_TIME")
                                or ev.get("status", {}).get("type", {}).get("completed", False)
                            )

                            h_score = int(h_c.get("score")) if is_completed and h_c.get("score") is not None else None
                            a_score = int(a_c.get("score")) if is_completed and a_c.get("score") is not None else None

                            venue = comp.get("venue", {}).get("fullName")

                            # Check if match exists in DB
                            cur.execute("""
                                SELECT id, home_score, away_score FROM matches
                                WHERE competition_id = ? AND home_team_id = ? AND away_team_id = ?
                                  AND match_date >= date(?, '-2 days') AND match_date <= date(?, '+2 days')
                            """, (comp_id, h_id, a_id, m_date, m_date))
                            existing = cur.fetchone()

                            if existing:
                                match_id, db_h_score, db_a_score = existing
                                # If it finished and we don't have score or score changed
                                if is_completed and (db_h_score != h_score or db_a_score != a_score):
                                    cur.execute("""
                                        UPDATE matches
                                        SET home_score = ?, away_score = ?, match_date = ?, match_time = ?, updated_at = datetime('now')
                                        WHERE id = ?
                                    """, (h_score, a_score, m_date, m_time, match_id))
                                    scores_updated += 1
                                    logger.info(f"Updated match {match_id}: {h_raw} {h_score}-{a_score} {a_raw}")
                            else:
                                # Insert new match
                                cur.execute("""
                                    INSERT INTO matches (
                                        competition_id, season, stage, match_date, match_time,
                                        home_team_id, away_team_id, home_score, away_score,
                                        venue, created_at, updated_at
                                    ) VALUES (?, '2425', ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                                """, (
                                    comp_id, default_stage, m_date, m_time,
                                    h_id, a_id, h_score, a_score, venue
                                ))
                                matches_created += 1
                except Exception as ex:
                    logger.debug(f"Sync skip {slug} for {d_str}: {ex}")

        conn.commit()

        # Log into scraping_logs if table exists
        duration_ms = int((time.time() - start_time) * 1000)
        try:
            cur.execute("""
                INSERT INTO scraping_logs (source, data_type, status, items_count, duration_ms, created_at)
                VALUES ('espn_live_sync', 'scores_and_fixtures', 'success', ?, ?, datetime('now'))
            """, (scores_updated + matches_created, duration_ms))
            conn.commit()
        except Exception:
            pass

        conn.close()

        result = {
            "status": "success",
            "scores_updated": scores_updated,
            "matches_created": matches_created,
            "events_processed": events_processed,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat(),
        }
        print(f"[Auto-Sincronizador] ✓ Datos al día: {scores_updated} marcadores actualizados, {matches_created} partidos registrados ({events_processed} eventos procesados).")
        logger.info(f"Live Sync Complete: {scores_updated} scores updated, {matches_created} matches created.")
        return result


_sync_thread: Optional[threading.Thread] = None


def start_background_sync(interval_seconds: int = 1800) -> None:
    """
    Runs an initial sync immediately, then periodically every `interval_seconds` in a daemon thread.
    """
    global _sync_thread
    if _sync_thread and _sync_thread.is_alive():
        return

    def _worker():
        service = LiveSyncService()
        while True:
            try:
                service.sync_all(days_back=3, days_ahead=4)
            except Exception as e:
                logger.error(f"Error in background sync: {e}")
            time.sleep(interval_seconds)

    _sync_thread = threading.Thread(target=_worker, name="ESPNLiveSyncWorker", daemon=True)
    _sync_thread.start()
    logger.info(f"Background ESPN Live Sync worker started (interval: {interval_seconds}s).")

