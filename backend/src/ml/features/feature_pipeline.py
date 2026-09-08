import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from src.config import settings
from src.config.constants import DEFAULT_WINDOWS, COMPETITION_IMPORTANCE, STAGE_MULTIPLIER


class FeaturePipeline:
    def __init__(self):
        self.feature_names: List[str] = []
        self.seed = settings.ML_RANDOM_SEED
        np.random.seed(self.seed)

    def build_features(self, match_data: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame()

        features = self._add_basic_info(features, match_data)
        features = self._add_ranking_features(features, match_data)
        features = self._add_form_features(features, match_data)
        features = self._add_historical_features(features, match_data)
        features = self._add_contextual_features(features, match_data)
        features = self._add_advanced_features(features, match_data)
        features = self._add_h2h_features(features, match_data)
        features = self._add_interaction_features(features)

        self.feature_names = features.columns.tolist()
        return features

    def _add_basic_info(self, features: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        features["is_neutral_venue"] = data.get("is_neutral", 0)
        features["has_extra_time"] = data.get("has_extra_time", 0)
        features["competition_type"] = data.get("competition_type", "world_cup")
        return features

    def _add_ranking_features(self, features: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        for col in ["fifa_ranking_home", "fifa_ranking_away"]:
            if col in data.columns:
                features[col] = data[col].fillna(150)

        if "fifa_ranking_home" in data.columns and "fifa_ranking_away" in data.columns:
            features["ranking_diff"] = data["fifa_ranking_away"] - data["fifa_ranking_home"]
            features["ranking_diff_abs"] = features["ranking_diff"].abs()
            features["ranking_diff_squared"] = features["ranking_diff"] ** 2

        for col in ["elo_rating_home", "elo_rating_away"]:
            if col in data.columns:
                features[col] = data[col].fillna(1500)

        if "elo_rating_home" in data.columns and "elo_rating_away" in data.columns:
            features["elo_diff"] = data["elo_rating_home"] - data["elo_rating_away"]
            features["elo_diff_abs"] = features["elo_diff"].abs()

        return features

    def _add_form_features(self, features: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        for window in DEFAULT_WINDOWS:
            for team_type in ["home", "away"]:
                prefix = f"{team_type}_last_{window}"

                for stat in ["goals_scored_avg", "goals_conceded_avg", "win_rate",
                             "draw_rate", "loss_rate", "points_per_game"]:
                    col = f"{prefix}_{stat}"
                    if col in data.columns:
                        features[col] = data[col].fillna(0)

                for stat in ["corners_avg", "shots_ot_avg", "shots_total_avg",
                             "fouls_avg", "yellow_avg", "possession_avg"]:
                    col = f"{prefix}_{stat}"
                    if col in data.columns:
                        features[col] = data[col].fillna(0)

        features["home_current_streak"] = data.get("home_current_streak", 0)
        features["away_current_streak"] = data.get("away_current_streak", 0)
        features["home_unbeaten_streak"] = data.get("home_unbeaten_streak", 0)
        features["away_unbeaten_streak"] = data.get("away_unbeaten_streak", 0)
        features["home_clean_sheets_5"] = data.get("home_clean_sheets_5", 0)
        features["away_clean_sheets_5"] = data.get("away_clean_sheets_5", 0)

        return features

    def _add_historical_features(self, features: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        features["home_avg_goals_scored_total"] = data.get("home_avg_goals_scored_total", 1.0)
        features["home_avg_goals_conceded_total"] = data.get("home_avg_goals_conceded_total", 1.0)
        features["away_avg_goals_scored_total"] = data.get("away_avg_goals_scored_total", 1.0)
        features["away_avg_goals_conceded_total"] = data.get("away_avg_goals_conceded_total", 1.0)

        features["home_attack_strength"] = data.get("home_attack_strength", 1.0)
        features["home_defense_strength"] = data.get("home_defense_strength", 1.0)
        features["away_attack_strength"] = data.get("away_attack_strength", 1.0)
        features["away_defense_strength"] = data.get("away_defense_strength", 1.0)

        features["home_offensive_efficiency"] = data.get("home_offensive_efficiency", 0.0)
        features["home_defensive_efficiency"] = data.get("home_defensive_efficiency", 0.0)
        features["away_offensive_efficiency"] = data.get("away_offensive_efficiency", 0.0)
        features["away_defensive_efficiency"] = data.get("away_defensive_efficiency", 0.0)

        return features

    def _add_contextual_features(self, features: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        features["match_importance"] = data.get("match_importance", 50.0)
        features["is_knockout"] = data.get("is_knockout", 0)
        features["is_group"] = data.get("is_group", 0)
        features["is_friendly"] = data.get("is_friendly", 0)
        features["need_to_win_home"] = data.get("need_to_win_home", 0)
        features["need_to_win_away"] = data.get("need_to_win_away", 0)

        features["days_rest_home"] = data.get("days_rest_home", 7).clip(1, 30)
        features["days_rest_away"] = data.get("days_rest_away", 7).clip(1, 30)
        features["rest_diff"] = features["days_rest_home"] - features["days_rest_away"]

        features["temperature"] = data.get("temperature", 20.0)
        features["altitude"] = data.get("altitude", 0)
        features["home_altitude_advantage"] = data.get("home_altitude_advantage", 0)

        features["pressure_index"] = data.get("pressure_index", 0.5)

        return features

    def _add_advanced_features(self, features: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        for prefix in ["home", "away"]:
            for metric in ["xg_avg_5", "xga_avg_5", "xg_diff_5",
                           "ppda_avg_5", "territorial_possession_avg_5",
                           "shot_conversion_rate_5", "progressive_passes_avg_5"]:
                col = f"{prefix}_{metric}"
                if col in data.columns:
                    features[col] = data[col].fillna(0)

        features["xg_diff"] = data.get("home_xg_avg_5", 0) - data.get("away_xga_avg_5", 0)
        features["elo_momentum_home"] = data.get("elo_momentum_home", 0)
        features["elo_momentum_away"] = data.get("elo_momentum_away", 0)
        features["elo_volatility_home"] = data.get("elo_volatility_home", 0)
        features["elo_volatility_away"] = data.get("elo_volatility_away", 0)

        return features

    def _add_h2h_features(self, features: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        features["h2h_games_played"] = data.get("h2h_games_played", 0)
        features["h2h_home_win_rate"] = data.get("h2h_home_win_rate", 0.5)
        features["h2h_avg_total_goals"] = data.get("h2h_avg_total_goals", 2.5)
        features["h2h_last_home_score"] = data.get("h2h_last_home_score", 1)
        features["h2h_last_away_score"] = data.get("h2h_last_away_score", 1)
        features["h2h_home_advantage"] = data.get("h2h_home_advantage", 0.5)

        return features

    def _add_interaction_features(self, features: pd.DataFrame) -> pd.DataFrame:
        if "ranking_diff" in features.columns and "is_knockout" in features.columns:
            features["ranking_x_knockout"] = features["ranking_diff"] * features["is_knockout"]

        if "elo_diff" in features.columns and "is_friendly" in features.columns:
            features["elo_x_friendly"] = features["elo_diff"] * features["is_friendly"]

        if "home_attack_strength" in features.columns and "away_defense_strength" in features.columns:
            features["attack_vs_defense"] = (
                features["home_attack_strength"] * features["away_defense_strength"]
            )

        for col in features.select_dtypes(include=[np.number]).columns:
            features[col] = features[col].fillna(0)

        return features

    def get_feature_names(self) -> List[str]:
        return self.feature_names

    def encode_categorical(self, features: pd.DataFrame) -> pd.DataFrame:
        cat_cols = features.select_dtypes(include=["object", "category"]).columns
        for col in cat_cols:
            features[col] = pd.Categorical(features[col]).codes
        return features
