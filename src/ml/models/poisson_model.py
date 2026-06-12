import numpy as np
import pandas as pd
from scipy.stats import poisson
from typing import Any, Dict, List, Optional, Tuple

from src.ml.models.base_model import BaseModel


class PoissonModel(BaseModel):
    def __init__(self, version: str = "1.0.0"):
        super().__init__("poisson", version)
        self.home_attack = {}
        self.home_defense = {}
        self.away_attack = {}
        self.away_defense = {}
        self.home_advantage = 0.0
        self.league_mean = 0.0

    def train(self, X: pd.DataFrame, y: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        X = X.copy()
        y = y.copy()

        home_goals = y["home_goals"].values
        away_goals = y["away_goals"].values
        teams = X["team_home"].values

        self.league_mean = (home_goals.mean() + away_goals.mean()) / 2

        unique_teams = np.unique(np.concatenate([X["team_home"].values, X["team_away"].values]))

        for team in unique_teams:
            home_mask = X["team_home"] == team
            away_mask = X["team_away"] == team

            home_gf = home_goals[home_mask].mean() if home_mask.sum() > 0 else self.league_mean
            home_ga = away_goals[home_mask].mean() if home_mask.sum() > 0 else self.league_mean
            away_gf = away_goals[away_mask].mean() if away_mask.sum() > 0 else self.league_mean
            away_ga = home_goals[away_mask].mean() if away_mask.sum() > 0 else self.league_mean

            self.home_attack[team] = home_gf / self.league_mean if self.league_mean > 0 else 1.0
            self.home_defense[team] = home_ga / self.league_mean if self.league_mean > 0 else 1.0
            self.away_attack[team] = away_gf / self.league_mean if self.league_mean > 0 else 1.0
            self.away_defense[team] = away_ga / self.league_mean if self.league_mean > 0 else 1.0

        self.home_advantage = home_goals.mean() / self.league_mean if self.league_mean > 0 else 1.0
        self.is_trained = True

        return {
            "league_mean": self.league_mean,
            "home_advantage": self.home_advantage,
            "n_teams": len(unique_teams),
        }

    def _expected_goals(self, home_team: str, away_team: str) -> Tuple[float, float]:
        home_attack = self.home_attack.get(home_team, 1.0)
        away_defense = self.away_defense.get(away_team, 1.0)
        exp_home = self.league_mean * home_attack * away_defense * self.home_advantage

        away_attack = self.away_attack.get(away_team, 1.0)
        home_defense = self.home_defense.get(home_team, 1.0)
        exp_away = self.league_mean * away_attack * home_defense

        return exp_home, exp_away

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        predictions = []
        for _, row in X.iterrows():
            exp_home, exp_away = self._expected_goals(row["team_home"], row["team_away"])
            predictions.append([exp_home, exp_away])
        return np.array(predictions)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        max_goals = 10
        results = []

        for _, row in X.iterrows():
            exp_home, exp_away = self._expected_goals(row["team_home"], row["team_away"])

            home_probs = np.array([poisson.pmf(g, exp_home) for g in range(max_goals + 1)])
            away_probs = np.array([poisson.pmf(g, exp_away) for g in range(max_goals + 1)])
            prob_matrix = np.outer(home_probs, away_probs)

            home_win = np.sum(np.triu(prob_matrix, k=1))
            draw = np.sum(np.diag(prob_matrix))
            away_win = np.sum(np.tril(prob_matrix, k=-1))
            total = home_win + draw + away_win

            if total > 0:
                home_win /= total
                draw /= total
                away_win /= total

            results.append([home_win, draw, away_win])

        return np.array(results)

    def predict_score_proba(self, home_team: str, away_team: str,
                            max_goals: int = 8) -> Dict[str, float]:
        exp_home, exp_away = self._expected_goals(home_team, away_team)
        scores = {}
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                prob = poisson.pmf(h, exp_home) * poisson.pmf(a, exp_away)
                if prob > 0.001:
                    scores[f"{h}-{a}"] = round(float(prob), 4)
        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

    def predict_over_under(self, home_team: str, away_team: str,
                           thresholds: List[int] = None) -> Dict[str, float]:
        if thresholds is None:
            thresholds = [0.5, 1.5, 2.5, 3.5, 4.5]
        exp_home, exp_away = self._expected_goals(home_team, away_team)
        results = {}
        total_goals_dist = poisson(exp_home + exp_away)
        for t in thresholds:
            over = 1.0 - total_goals_dist.cdf(t)
            results[f"over_{t:.1f}"] = round(float(over), 4)
            results[f"under_{t:.1f}"] = round(float(1.0 - over), 4)
        return results

    def get_feature_importance(self) -> Dict[str, float]:
        return {
            "home_attack": float(np.mean(list(self.home_attack.values()))),
            "home_defense": float(np.mean(list(self.home_defense.values()))),
            "away_attack": float(np.mean(list(self.away_attack.values()))),
            "away_defense": float(np.mean(list(self.away_defense.values()))),
            "home_advantage": float(self.home_advantage),
            "league_mean": float(self.league_mean),
        }
