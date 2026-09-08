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

    def _get_team_keys(self, row: Any) -> Tuple[Any, Any]:
        if isinstance(row, dict):
            home = row.get("team_home") or row.get("home_team") or row.get("home_team_id") or "Team_H"
            away = row.get("team_away") or row.get("away_team") or row.get("away_team_id") or "Team_A"
            return home, away
        if hasattr(row, "__getitem__"):
            try:
                home = row["team_home"] if "team_home" in row else row["home_team"] if "home_team" in row else row.get("home_team_id", "Team_H")
                away = row["team_away"] if "team_away" in row else row["away_team"] if "away_team" in row else row.get("away_team_id", "Team_A")
                return home, away
            except Exception:
                pass
        return "Team_H", "Team_A"

    def train(self, X: pd.DataFrame, y: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        X = X.copy()
        y = y.copy()

        home_goals = y["home_goals"].values if "home_goals" in y else y.iloc[:, 0].values
        away_goals = y["away_goals"].values if "away_goals" in y else y.iloc[:, 1].values

        home_col = "team_home" if "team_home" in X.columns else "home_team" if "home_team" in X.columns else "home_team_id" if "home_team_id" in X.columns else None
        away_col = "team_away" if "team_away" in X.columns else "away_team" if "away_team" in X.columns else "away_team_id" if "away_team_id" in X.columns else None

        if home_col and away_col:
            home_teams = X[home_col].values
            away_teams = X[away_col].values
        else:
            home_teams = np.array([f"Team_{i}" for i in range(len(X))])
            away_teams = np.array([f"Team_{i+1}" for i in range(len(X))])

        self.league_mean = float((home_goals.mean() + away_goals.mean()) / 2) if len(home_goals) > 0 else 1.25

        unique_teams = np.unique(np.concatenate([home_teams, away_teams]))

        for team in unique_teams:
            home_mask = (home_teams == team)
            away_mask = (away_teams == team)

            home_gf = home_goals[home_mask].mean() if home_mask.sum() > 0 else self.league_mean
            home_ga = away_goals[home_mask].mean() if home_mask.sum() > 0 else self.league_mean
            away_gf = away_goals[away_mask].mean() if away_mask.sum() > 0 else self.league_mean
            away_ga = home_goals[away_mask].mean() if away_mask.sum() > 0 else self.league_mean

            self.home_attack[team] = home_gf / self.league_mean if self.league_mean > 0 else 1.0
            self.home_defense[team] = home_ga / self.league_mean if self.league_mean > 0 else 1.0
            self.away_attack[team] = away_gf / self.league_mean if self.league_mean > 0 else 1.0
            self.away_defense[team] = away_ga / self.league_mean if self.league_mean > 0 else 1.0

        self.home_advantage = float(home_goals.mean() / self.league_mean) if self.league_mean > 0 else 1.15
        self.is_trained = True

        return {
            "league_mean": self.league_mean,
            "home_advantage": self.home_advantage,
            "n_teams": len(unique_teams),
        }

    def _expected_goals(self, home_team: Any, away_team: Any) -> Tuple[float, float]:
        home_attack = self.home_attack.get(home_team, 1.0)
        away_defense = self.away_defense.get(away_team, 1.0)
        exp_home = self.league_mean * home_attack * away_defense * self.home_advantage

        away_attack = self.away_attack.get(away_team, 1.0)
        home_defense = self.home_defense.get(home_team, 1.0)
        exp_away = self.league_mean * away_attack * home_defense

        return max(exp_home, 0.1), max(exp_away, 0.1)

    def predict(self, X: Any) -> np.ndarray:
        if not isinstance(X, pd.DataFrame):
            return np.array([[self.league_mean * self.home_advantage, self.league_mean]] * len(X))
        predictions = []
        for _, row in X.iterrows():
            h, a = self._get_team_keys(row)
            exp_home, exp_away = self._expected_goals(h, a)
            predictions.append([exp_home, exp_away])
        return np.array(predictions)

    def predict_proba(self, X: Any) -> np.ndarray:
        max_goals = 10
        results = []

        if not isinstance(X, pd.DataFrame):
            # Fallback if numpy array is passed
            exp_h = max(self.league_mean * self.home_advantage, 0.1)
            exp_a = max(self.league_mean, 0.1)
            home_probs = np.array([poisson.pmf(g, exp_h) for g in range(max_goals + 1)])
            away_probs = np.array([poisson.pmf(g, exp_a) for g in range(max_goals + 1)])
            prob_matrix = np.outer(home_probs, away_probs)
            hw = float(np.sum(np.tril(prob_matrix, k=-1)))
            dr = float(np.sum(np.diag(prob_matrix)))
            aw = float(np.sum(np.triu(prob_matrix, k=1)))
            tot = hw + dr + aw
            row_res = [hw / tot, dr / tot, aw / tot] if tot > 0 else [0.45, 0.25, 0.30]
            return np.array([row_res] * len(X))

        for _, row in X.iterrows():
            h, a = self._get_team_keys(row)
            exp_home, exp_away = self._expected_goals(h, a)

            home_probs = np.array([poisson.pmf(g, exp_home) for g in range(max_goals + 1)])
            away_probs = np.array([poisson.pmf(g, exp_away) for g in range(max_goals + 1)])
            prob_matrix = np.outer(home_probs, away_probs)

            # Row = home goals, Col = away goals
            # Row > Col => Lower triangle => Home win
            # Row == Col => Diagonal => Draw
            # Row < Col => Upper triangle => Away win
            home_win = float(np.sum(np.tril(prob_matrix, k=-1)))
            draw = float(np.sum(np.diag(prob_matrix)))
            away_win = float(np.sum(np.triu(prob_matrix, k=1)))
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
            "home_attack": float(np.mean(list(self.home_attack.values())) if self.home_attack else 1.0),
            "home_defense": float(np.mean(list(self.home_defense.values())) if self.home_defense else 1.0),
            "away_attack": float(np.mean(list(self.away_attack.values())) if self.away_attack else 1.0),
            "away_defense": float(np.mean(list(self.away_defense.values())) if self.away_defense else 1.0),
            "home_advantage": float(self.home_advantage),
            "league_mean": float(self.league_mean),
        }

    def save(self, path: str):
        import joblib
        joblib.dump({
            "home_attack": self.home_attack,
            "home_defense": self.home_defense,
            "away_attack": self.away_attack,
            "away_defense": self.away_defense,
            "home_advantage": self.home_advantage,
            "league_mean": self.league_mean,
            "model_name": self.model_name,
            "version": self.version,
            "feature_names": self.feature_names,
            "is_trained": self.is_trained,
        }, path)

    def load(self, path: str):
        import joblib
        data = joblib.load(path)
        self.home_attack = data.get("home_attack", {})
        self.home_defense = data.get("home_defense", {})
        self.away_attack = data.get("away_attack", {})
        self.away_defense = data.get("away_defense", {})
        self.home_advantage = data.get("home_advantage", 1.15)
        self.league_mean = data.get("league_mean", 1.25)
        self.model_name = data.get("model_name", "poisson")
        self.version = data.get("version", "1.0.0")
        self.feature_names = data.get("feature_names", [])
        self.is_trained = data.get("is_trained", False)
