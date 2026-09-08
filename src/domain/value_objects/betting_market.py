"""Betting Market Value Objects and Expected Value (+EV) calculations"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class BettingOdds:
    home_win: float
    draw: float
    away_win: float
    over_25: Optional[float] = None
    under_25: Optional[float] = None
    bookmaker: str = "Consensus"

    @property
    def overround(self) -> float:
        """Calculate total bookmaker margin (e.g. 1.05 = 5% juice/vig)"""
        inv_sum = (1.0 / self.home_win) + (1.0 / self.draw) + (1.0 / self.away_win)
        return round(inv_sum, 4)

    @property
    def margin_percentage(self) -> float:
        """Bookmaker profit margin in %"""
        return round((self.overround - 1.0) * 100, 2)

    def fair_probabilities(self) -> Dict[str, float]:
        """Remove bookmaker margin to get true market consensus probabilities"""
        total = self.overround
        return {
            "H": round((1.0 / self.home_win) / total, 4),
            "D": round((1.0 / self.draw) / total, 4),
            "A": round((1.0 / self.away_win) / total, 4),
        }

    @staticmethod
    def calculate_ev(model_prob: float, odds: float) -> float:
        """
        Calculate Expected Value (EV):
        EV = (Probability * Odds) - 1
        A positive EV (> 0) means profitable in the long run.
        """
        return round((model_prob * odds) - 1.0, 4)

    @staticmethod
    def kelly_criterion(model_prob: float, odds: float, fraction: float = 0.25) -> float:
        """
        Fractional Kelly Criterion for optimal bankroll stake sizing.
        b = odds - 1 (net decimal odds)
        p = model probability
        q = 1 - p
        f* = (b*p - q) / b
        Using fractional Kelly (default 0.25 / quarter-Kelly) for risk management.
        """
        b = odds - 1.0
        if b <= 0:
            return 0.0
        p = model_prob
        q = 1.0 - p
        full_kelly = (b * p - q) / b
        if full_kelly <= 0:
            return 0.0
        # Return percentage of bankroll recommended, capped at 5% for safety
        suggested = min(full_kelly * fraction, 0.05)
        return round(suggested * 100, 2)

    def analyze_value(self, model_probs: Dict[str, float], min_ev: float = 0.02) -> Dict[str, Any]:
        """
        Compare model predicted probabilities with market odds to find +EV bets.
        """
        fair = self.fair_probabilities()
        odds_map = {"H": self.home_win, "D": self.draw, "A": self.away_win}
        names = {"H": "Local", "D": "Empate", "A": "Visitante"}

        analysis = {
            "bookmaker": self.bookmaker,
            "margin_percentage": self.margin_percentage,
            "market_fair_probabilities": fair,
            "opportunities": [],
            "best_bet": None,
        }

        best_opportunity = None
        highest_ev = -1.0

        for outcome, odds in odds_map.items():
            prob = model_probs.get(outcome, 0.0)
            ev = self.calculate_ev(prob, odds)
            ev_pct = round(ev * 100, 2)
            kelly = self.kelly_criterion(prob, odds)

            opp = {
                "outcome": outcome,
                "label": names[outcome],
                "odds": odds,
                "model_prob_pct": round(prob * 100, 1),
                "market_implied_prob_pct": round((1.0 / odds) * 100, 1),
                "fair_prob_pct": round(fair[outcome] * 100, 1),
                "ev_pct": ev_pct,
                "has_value": ev >= min_ev,
                "suggested_stake_bankroll_pct": kelly if ev >= min_ev else 0.0,
            }
            analysis["opportunities"].append(opp)

            if ev > highest_ev and ev >= min_ev:
                highest_ev = ev
                best_opportunity = opp

        analysis["best_bet"] = best_opportunity
        return analysis

