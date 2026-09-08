import pytest
from src.domain.value_objects.betting_market import BettingOdds


class TestBettingMarket:
    def test_overround_and_margin(self):
        # Odds of 2.0, 3.2, 3.8
        odds = BettingOdds(home_win=2.0, draw=3.2, away_win=3.8)
        # 1/2.0 + 1/3.2 + 1/3.8 = 0.5 + 0.3125 + 0.26315 = 1.0757 (7.57% vig)
        assert odds.overround > 1.0
        assert 7.0 < odds.margin_percentage < 8.0

    def test_fair_probabilities(self):
        odds = BettingOdds(home_win=2.0, draw=3.5, away_win=4.0)
        fair = odds.fair_probabilities()
        assert "H" in fair and "D" in fair and "A" in fair
        # Fair probabilities must sum to 1.0
        total = fair["H"] + fair["D"] + fair["A"]
        assert abs(total - 1.0) < 0.01

    def test_ev_calculation(self):
        # 55% model probability at 2.0 odds
        # EV = (0.55 * 2.0) - 1 = +0.10 (+10%)
        ev = BettingOdds.calculate_ev(0.55, 2.0)
        assert ev == 0.10

        # Negative EV
        ev_neg = BettingOdds.calculate_ev(0.40, 2.0)
        assert ev_neg == -0.20

    def test_kelly_criterion(self):
        # 60% win prob, 2.0 odds -> full kelly = (1 * 0.6 - 0.4) / 1 = 0.20 (20%)
        # fractional kelly (0.25) -> 5.0%
        kelly = BettingOdds.kelly_criterion(0.60, 2.0, fraction=0.25)
        assert kelly == 5.0

        # Negative EV -> 0% stake
        kelly_zero = BettingOdds.kelly_criterion(0.40, 2.0)
        assert kelly_zero == 0.0

    def test_analyze_value(self):
        odds = BettingOdds(home_win=2.50, draw=3.20, away_win=2.90)
        # Model gives 50% to Home
        # 0.50 * 2.50 = 1.25 -> EV = +25%
        model_probs = {"H": 0.50, "D": 0.25, "A": 0.25}
        analysis = odds.analyze_value(model_probs)

        assert analysis["best_bet"] is not None
        assert analysis["best_bet"]["outcome"] == "H"
        assert analysis["best_bet"]["has_value"] is True
        assert analysis["best_bet"]["ev_pct"] == 25.0

