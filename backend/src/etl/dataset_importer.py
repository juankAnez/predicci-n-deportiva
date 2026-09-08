"""Dataset importer for football data from GitHub mirrors"""

import io
import csv
import urllib.request
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from src.config import settings
from src.infrastructure.database.connection import db_session
from src.infrastructure.database.models import (
    CompetitionModel,
    TeamModel,
    MatchModel,
    TeamStatsModel,
    RankingModel,
)

BASE_GITHUB_URL = "https://raw.githubusercontent.com/datasets/football-datasets/main/datasets"

LEAGUES_CONFIG = {
    "la-liga": {
        "name": "La Liga",
        "code": "ESP_L1",
        "country": "Spain",
        "type": "league",
    },
    "premier-league": {
        "name": "Premier League",
        "code": "ENG_PL",
        "country": "England",
        "type": "league",
    },
    "serie-a": {
        "name": "Serie A",
        "code": "ITA_SA",
        "country": "Italy",
        "type": "league",
    },
    "bundesliga": {
        "name": "Bundesliga",
        "code": "GER_BL",
        "country": "Germany",
        "type": "league",
    },
    "ligue-1": {
        "name": "Ligue 1",
        "code": "FRA_L1",
        "country": "France",
        "type": "league",
    },
}

DEFAULT_SEASONS = ["2122", "2223", "2324", "2425"]


class DatasetImporter:
    def __init__(self, raw_dir: Optional[Path] = None):
        self.raw_dir = raw_dir or (Path(settings.DATA_DIR) / "raw")
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.db: Session = db_session()
        self.team_cache: Dict[str, TeamModel] = {}
        self.competition_cache: Dict[str, CompetitionModel] = {}
        self.elo_ratings: Dict[int, float] = {}

    def fetch_csv(self, league_slug: str, season: str) -> Optional[str]:
        """Download season CSV from GitHub mirror, saving a copy locally"""
        league_dir = self.raw_dir / league_slug
        league_dir.mkdir(parents=True, exist_ok=True)
        local_file = league_dir / f"season-{season}.csv"

        if local_file.exists() and local_file.stat().st_size > 500:
            return local_file.read_text(encoding="utf-8", errors="ignore")

        url = f"{BASE_GITHUB_URL}/{league_slug}/season-{season}.csv"
        print(f"  Descargando {league_slug} temporada {season} desde mirror...")
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                local_file.write_text(content, encoding="utf-8")
                return content
        except Exception as e:
            print(f"  [AVISO] No se pudo descargar {url}: {e}")
            return None

    def get_or_create_competition(self, league_slug: str, season: str = "2324") -> CompetitionModel:
        cache_key = f"{league_slug}_{season}"
        if cache_key in self.competition_cache:
            return self.competition_cache[cache_key]

        cfg = LEAGUES_CONFIG.get(league_slug, {
            "name": league_slug.replace("-", " ").title(),
            "code": league_slug[:6].upper(),
            "country": "Europe",
            "type": "league",
        })

        comp = (
            self.db.query(CompetitionModel)
            .filter(CompetitionModel.name == cfg["name"], CompetitionModel.season == season)
            .first()
        )
        if not comp:
            comp = CompetitionModel(
                name=cfg["name"],
                short_name=cfg["code"],
                type=cfg["type"],
                confederation=cfg["country"],
                season=season,
            )
            self.db.add(comp)
            self.db.commit()
            self.db.refresh(comp)

        self.competition_cache[cache_key] = comp
        return comp

    def get_or_create_team(self, team_name: str, country: str) -> TeamModel:
        clean_name = team_name.strip()
        if clean_name in self.team_cache:
            return self.team_cache[clean_name]

        team = (
            self.db.query(TeamModel)
            .filter(TeamModel.name == clean_name)
            .first()
        )
        if not team:
            code = clean_name[:3].upper()
            team = TeamModel(
                name=clean_name,
                full_name=clean_name,
                code=code,
                country=country,
            )
            self.db.add(team)
            self.db.commit()
            self.db.refresh(team)

        self.team_cache[clean_name] = team
        if team.id not in self.elo_ratings:
            self.elo_ratings[team.id] = 1500.0
        return team

    def _parse_date(self, date_str: str) -> Optional[date]:
        date_str = date_str.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y"):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                pass
        return None

    def _update_elo(self, home_id: int, away_id: int, home_score: int, away_score: int, match_date: date) -> Tuple[float, float]:
        """Calculate and update Elo ratings for both teams with home advantage"""
        k_factor = 32.0
        home_elo = self.elo_ratings.get(home_id, 1500.0)
        away_elo = self.elo_ratings.get(away_id, 1500.0)

        # Home field advantage of +65 Elo points
        expected_home = 1.0 / (1.0 + 10.0 ** ((away_elo - (home_elo + 65.0)) / 400.0))
        expected_away = 1.0 - expected_home

        if home_score > away_score:
            actual_home, actual_away = 1.0, 0.0
        elif home_score == away_score:
            actual_home, actual_away = 0.5, 0.5
        else:
            actual_home, actual_away = 0.0, 1.0

        new_home_elo = home_elo + k_factor * (actual_home - expected_home)
        new_away_elo = away_elo + k_factor * (actual_away - expected_away)

        self.elo_ratings[home_id] = new_home_elo
        self.elo_ratings[away_id] = new_away_elo

        # Record ranking snapshot in database
        for tid, elo in ((home_id, new_home_elo), (away_id, new_away_elo)):
            ranking = RankingModel(
                team_id=tid,
                ranking_type="elo",
                rank=0,
                points=round(elo, 1),
                change_points=round(k_factor * (actual_home - expected_home) if tid == home_id else k_factor * (actual_away - expected_away), 1),
                rank_date=match_date,
            )
            self.db.add(ranking)

        return new_home_elo, new_away_elo

    def import_league_season(self, league_slug: str, season: str) -> int:
        content = self.fetch_csv(league_slug, season)
        if not content:
            return 0

        comp = self.get_or_create_competition(league_slug, season)
        cfg = LEAGUES_CONFIG.get(league_slug, {"country": "Europe"})

        reader = csv.DictReader(io.StringIO(content))
        inserted_matches = 0

        # Sort matches by date to ensure chronological order for Elo
        rows = list(reader)
        valid_rows = []
        for r in rows:
            d_val = self._parse_date(r.get("Date", ""))
            if d_val and r.get("HomeTeam") and r.get("AwayTeam") and r.get("FTHG") is not None and r.get("FTHG") != "":
                valid_rows.append((d_val, r))

        valid_rows.sort(key=lambda x: x[0])

        for match_date, r in valid_rows:
            home_team_name = r["HomeTeam"]
            away_team_name = r["AwayTeam"]

            home_team = self.get_or_create_team(home_team_name, cfg["country"])
            away_team = self.get_or_create_team(away_team_name, cfg["country"])

            # Check if match already exists
            existing = (
                self.db.query(MatchModel)
                .filter(
                    MatchModel.competition_id == comp.id,
                    MatchModel.home_team_id == home_team.id,
                    MatchModel.away_team_id == away_team.id,
                    MatchModel.match_date == match_date,
                )
                .first()
            )
            if existing:
                continue

            try:
                fthg = int(r["FTHG"])
                ftag = int(r["FTAG"])
            except (ValueError, TypeError):
                continue

            hthg = int(r["HTHG"]) if r.get("HTHG") and r["HTHG"].isdigit() else None
            htag = int(r["HTAG"]) if r.get("HTAG") and r["HTAG"].isdigit() else None

            match = MatchModel(
                competition_id=comp.id,
                season=season,
                match_date=match_date,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                home_score=fthg,
                away_score=ftag,
                home_goals_ht=hthg,
                away_goals_ht=htag,
                referee=r.get("Referee"),
            )
            self.db.add(match)
            self.db.flush()

            # Record stats
            def safe_int(key):
                val = r.get(key)
                return int(val) if val and val.isdigit() else None

            home_stats = TeamStatsModel(
                match_id=match.id,
                team_id=home_team.id,
                is_home=True,
                goals=fthg,
                shots_total=safe_int("HS"),
                shots_on_target=safe_int("HST"),
                fouls=safe_int("HF"),
                corners=safe_int("HC"),
                yellow_cards=safe_int("HY"),
                red_cards=safe_int("HR"),
            )
            away_stats = TeamStatsModel(
                match_id=match.id,
                team_id=away_team.id,
                is_home=False,
                goals=ftag,
                shots_total=safe_int("AS"),
                shots_on_target=safe_int("AST"),
                fouls=safe_int("AF"),
                corners=safe_int("AC"),
                yellow_cards=safe_int("AY"),
                red_cards=safe_int("AR"),
            )
            self.db.add(home_stats)
            self.db.add(away_stats)

            # Update Elo ratings chronologically
            self._update_elo(home_team.id, away_team.id, fthg, ftag, match_date)

            inserted_matches += 1

        self.db.commit()
        return inserted_matches

    def import_all(self, leagues: Optional[List[str]] = None, seasons: Optional[List[str]] = None) -> Dict[str, int]:
        selected_leagues = leagues or list(LEAGUES_CONFIG.keys())
        selected_seasons = seasons or DEFAULT_SEASONS

        total_by_league = {}
        for league in selected_leagues:
            total_matches = 0
            for season in selected_seasons:
                count = self.import_league_season(league, season)
                total_matches += count
            total_by_league[league] = total_matches
            print(f"  [OK] {league}: {total_matches} partidos importados.")

        return total_by_league
