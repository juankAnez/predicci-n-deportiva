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

        home_ranking = self.ranking_repo.get_ranking_at_date(home_team_id, match_date)
        away_ranking = self.ranking_repo.get_ranking_at_date(away_team_id, match_date)

        data["fifa_ranking_home"] = home_ranking.rank if home_ranking else 150
        data["fifa_ranking_away"] = away_ranking.rank if away_ranking else 150
        data["elo_rating_home"] = home_ranking.points if home_ranking and home_ranking.ranking_type == "elo" else 1500
        data["elo_rating_away"] = away_ranking.points if away_ranking and away_ranking.ranking_type == "elo" else 1500

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
