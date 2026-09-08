import numpy as np
import pandas as pd
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.config import settings
from src.config.constants import DEFAULT_WINDOWS, COMPETITION_IMPORTANCE, STAGE_MULTIPLIER
from src.infrastructure.database.repositories import (
    TeamRepository, MatchRepository, RankingRepository, TeamStatsRepository
)
from src.ml.features.feature_pipeline import FeaturePipeline


class FeatureService:
    def __init__(self):
        self.team_repo = TeamRepository()
        self.match_repo = MatchRepository()
        self.ranking_repo = RankingRepository()
        self.stats_repo = TeamStatsRepository()
        self.feature_pipeline = FeaturePipeline()

    def generate_features_for_match(self, home_team_id: int, away_team_id: int,
                                     match_date: date, competition_id: Optional[int] = None,
                                     stage: Optional[str] = None) -> pd.DataFrame:
        data = {}

        home_matches = self.match_repo.get_team_matches_since(
            home_team_id, match_date - timedelta(days=365 * 2)
        )
        away_matches = self.match_repo.get_team_matches_since(
            away_team_id, match_date - timedelta(days=365 * 2)
        )

        for window in DEFAULT_WINDOWS:
            home_recent = home_matches[:window]
            away_recent = away_matches[:window]
            for team_type, matches in [("home", home_recent), ("away", away_recent)]:
                if matches:
                    team_id = home_team_id if team_type == "home" else away_team_id
                    data.update(self._calculate_form_features(matches, team_id, team_type, window))

        home_fifa = self.ranking_repo.get_ranking_at_date(home_team_id, match_date, ranking_type="fifa")
        away_fifa = self.ranking_repo.get_ranking_at_date(away_team_id, match_date, ranking_type="fifa")
        home_elo = self.ranking_repo.get_ranking_at_date(home_team_id, match_date, ranking_type="elo")
        away_elo = self.ranking_repo.get_ranking_at_date(away_team_id, match_date, ranking_type="elo")

        data["fifa_ranking_home"] = home_fifa.rank if home_fifa else 150
        data["fifa_ranking_away"] = away_fifa.rank if away_fifa else 150
        data["elo_rating_home"] = home_elo.points if home_elo else 1500.0
        data["elo_rating_away"] = away_elo.points if away_elo else 1500.0

        h2h = self.match_repo.get_h2h(home_team_id, away_team_id, limit=10)
        data.update(self._calculate_h2h_features(h2h, home_team_id, away_team_id))

        data["days_rest_home"] = self._calculate_rest_days(home_matches, match_date)
        data["days_rest_away"] = self._calculate_rest_days(away_matches, match_date)

        df = pd.DataFrame([data])

        return self.feature_pipeline.build_features(df)

    def generate_bulk_features(self, matches_data: List[Dict]) -> pd.DataFrame:
        feature_list = []
        for m in matches_data:
            try:
                features = self.generate_features_for_match(
                    m["home_team_id"], m["away_team_id"],
                    m["match_date"], m.get("competition_id"), m.get("stage")
                )
                feature_list.append(features.iloc[0].to_dict())
            except Exception as e:
                print(f"Error generando features para match {m}: {e}")
                continue

        return pd.DataFrame(feature_list)

    def _calculate_form_features(self, matches, team_id: int,
                                  team_type: str, window: int) -> Dict[str, float]:
        prefix = f"{team_type}_last_{window}"
        features = {}

        if not matches:
            features[f"{prefix}_goals_scored_avg"] = 0
            features[f"{prefix}_goals_conceded_avg"] = 0
            features[f"{prefix}_win_rate"] = 0
            features[f"{prefix}_draw_rate"] = 0
            features[f"{prefix}_loss_rate"] = 0
            features[f"{prefix}_points_per_game"] = 0
            return features

        goals_scored = []
        goals_conceded = []
        points = []

        for match in matches:
            if match.home_team_id == team_id:
                goals_scored.append(match.home_score or 0)
                goals_conceded.append(match.away_score or 0)
                if (match.home_score or 0) > (match.away_score or 0):
                    points.append(3)
                elif (match.home_score or 0) == (match.away_score or 0):
                    points.append(1)
                else:
                    points.append(0)
            else:
                goals_scored.append(match.away_score or 0)
                goals_conceded.append(match.home_score or 0)
                if (match.away_score or 0) > (match.home_score or 0):
                    points.append(3)
                elif (match.away_score or 0) == (match.home_score or 0):
                    points.append(1)
                else:
                    points.append(0)

        valid_matches = len(goals_scored)
        if valid_matches == 0:
            return features

        features[f"{prefix}_goals_scored_avg"] = float(np.mean(goals_scored))
        features[f"{prefix}_goals_conceded_avg"] = float(np.mean(goals_conceded))
        features[f"{prefix}_win_rate"] = sum(1 for p in points if p == 3) / valid_matches
        features[f"{prefix}_draw_rate"] = sum(1 for p in points if p == 1) / valid_matches
        features[f"{prefix}_loss_rate"] = sum(1 for p in points if p == 0) / valid_matches
        features[f"{prefix}_points_per_game"] = float(np.mean(points))

        return features

    def _calculate_h2h_features(self, matches, home_team_id: int,
                                 away_team_id: int) -> Dict[str, float]:
        features = {
            "h2h_games_played": len(matches),
            "h2h_home_win_rate": 0.5,
            "h2h_avg_total_goals": 2.5,
            "h2h_last_home_score": 1,
            "h2h_last_away_score": 1,
            "h2h_home_advantage": 0.5,
        }

        if not matches:
            return features

        home_wins = 0
        total_goals = []

        for m in matches:
            total_goals.append((m.home_score or 0) + (m.away_score or 0))
            if (m.home_team_id == home_team_id and (m.home_score or 0) > (m.away_score or 0)):
                home_wins += 1
            elif (m.away_team_id == home_team_id and (m.away_score or 0) > (m.home_score or 0)):
                home_wins += 1

        features["h2h_home_win_rate"] = home_wins / len(matches)
        features["h2h_avg_total_goals"] = float(np.mean(total_goals))

        last = matches[0]
        features["h2h_last_home_score"] = (
            last.home_score if last.home_team_id == home_team_id else last.away_score
        ) or 1
        features["h2h_last_away_score"] = (
            last.away_score if last.home_team_id == home_team_id else last.home_score
        ) or 1

        return features

    def _calculate_rest_days(self, matches, match_date: date) -> int:
        if not matches:
            return 7
        last_match = matches[0]
        delta = (match_date - last_match.match_date).days if last_match.match_date else 7
        return max(1, min(delta, 30))

    def build_training_dataframe(self, matches: List[Any]) -> pd.DataFrame:
        """
        Builds a full training dataset with chronological rolling form features and Elo ratings.
        Zero data leakage: each match only uses information available BEFORE kickoff.
        """
        # Sort matches chronologically
        sorted_matches = sorted(
            [m for m in matches if m.home_score is not None and m.match_date is not None],
            key=lambda x: x.match_date
        )

        team_history: Dict[int, List[Dict[str, Any]]] = {}
        team_elo: Dict[int, float] = {}
        rows = []

        for m in sorted_matches:
            h_id = m.home_team_id
            a_id = m.away_team_id
            m_date = m.match_date

            h_elo = team_elo.get(h_id, 1500.0)
            a_elo = team_elo.get(a_id, 1500.0)

            h_hist = team_history.get(h_id, [])
            a_hist = team_history.get(a_id, [])

            row: Dict[str, Any] = {
                "match_id": m.id,
                "match_date": m_date,
                "home_team_id": h_id,
                "away_team_id": a_id,
                "team_home": str(h_id),
                "team_away": str(a_id),
                "home_goals": m.home_score,
                "away_goals": m.away_score,
                "result": "H" if m.home_score > m.away_score else "A" if m.away_score > m.home_score else "D",
                "elo_rating_home": h_elo,
                "elo_rating_away": a_elo,
                "fifa_ranking_home": 100,
                "fifa_ranking_away": 100,
            }

            # Calculate rolling window features (e.g. last 5 games)
            for window in [5, 10]:
                for team_type, hist in [("home", h_hist), ("away", a_hist)]:
                    prefix = f"{team_type}_last_{window}"
                    recent = hist[-window:] if hist else []
                    if recent:
                        gf = [g["gf"] for g in recent]
                        ga = [g["ga"] for g in recent]
                        pts = [g["pts"] for g in recent]
                        row[f"{prefix}_goals_scored_avg"] = float(np.mean(gf))
                        row[f"{prefix}_goals_conceded_avg"] = float(np.mean(ga))
                        row[f"{prefix}_win_rate"] = sum(1 for p in pts if p == 3) / len(pts)
                        row[f"{prefix}_draw_rate"] = sum(1 for p in pts if p == 1) / len(pts)
                        row[f"{prefix}_loss_rate"] = sum(1 for p in pts if p == 0) / len(pts)
                        row[f"{prefix}_points_per_game"] = float(np.mean(pts))
                        row[f"{prefix}_shots_ot_avg"] = float(np.mean([g["sot"] for g in recent]))
                        row[f"{prefix}_corners_avg"] = float(np.mean([g["corners"] for g in recent]))
                    else:
                        row[f"{prefix}_goals_scored_avg"] = 1.2
                        row[f"{prefix}_goals_conceded_avg"] = 1.2
                        row[f"{prefix}_win_rate"] = 0.33
                        row[f"{prefix}_draw_rate"] = 0.33
                        row[f"{prefix}_loss_rate"] = 0.33
                        row[f"{prefix}_points_per_game"] = 1.0
                        row[f"{prefix}_shots_ot_avg"] = 4.0
                        row[f"{prefix}_corners_avg"] = 5.0

            # Rest days
            row["days_rest_home"] = (m_date - h_hist[-1]["date"]).days if h_hist and "date" in h_hist[-1] else 7
            row["days_rest_away"] = (m_date - a_hist[-1]["date"]).days if a_hist and "date" in a_hist[-1] else 7

            # Historical attack/defense ratios
            h_scored_total = [g["gf"] for g in h_hist]
            a_conceded_total = [g["ga"] for g in a_hist]
            row["home_attack_strength"] = (float(np.mean(h_scored_total)) / 1.3) if h_scored_total else 1.0
            row["away_defense_strength"] = (float(np.mean(a_conceded_total)) / 1.3) if a_conceded_total else 1.0

            rows.append(row)

            # Update history and Elo ratings AFTER recording match features
            h_pts = 3 if m.home_score > m.away_score else 1 if m.home_score == m.away_score else 0
            a_pts = 3 if m.away_score > m.home_score else 1 if m.home_score == m.away_score else 0

            if h_id not in team_history:
                team_history[h_id] = []
            if a_id not in team_history:
                team_history[a_id] = []

            team_history[h_id].append({
                "date": m_date,
                "gf": m.home_score,
                "ga": m.away_score,
                "pts": h_pts,
                "sot": 4.5,
                "corners": 5.0,
            })
            team_history[a_id].append({
                "date": m_date,
                "gf": m.away_score,
                "ga": m.home_score,
                "pts": a_pts,
                "sot": 4.0,
                "corners": 4.5,
            })

            # Update Elo
            exp_h = 1.0 / (1.0 + 10.0 ** ((a_elo - (h_elo + 65.0)) / 400.0))
            exp_a = 1.0 - exp_h
            act_h = 1.0 if h_pts == 3 else 0.5 if h_pts == 1 else 0.0
            act_a = 1.0 if a_pts == 3 else 0.5 if a_pts == 1 else 0.0
            team_elo[h_id] = h_elo + 32.0 * (act_h - exp_h)
            team_elo[a_id] = a_elo + 32.0 * (act_a - exp_a)

        return pd.DataFrame(rows)
