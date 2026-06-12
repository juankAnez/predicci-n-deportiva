import pytest
import numpy as np
import pandas as pd

from src.domain.entities import Team, Player, Match, Competition, Prediction
from src.domain.value_objects import Ranking, TeamStats, Probability


class TestDomainEntities:
    def test_team_creation(self):
        team = Team(name="Brasil", code="BRA", confederation="CONMEBOL")
        assert team.name == "Brasil"
        assert team.code == "BRA"
        assert team.confederation == "CONMEBOL"

    def test_team_equality(self):
        t1 = Team(name="Brasil")
        t2 = Team(name="Brasil")
        assert t1 == t2

    def test_team_hash(self):
        t1 = Team(name="Brasil")
        assert hash(t1) == hash("Brasil")

    def test_match_is_finished(self):
        m = Match(home_score=2, away_score=1)
        assert m.is_finished is True

    def test_match_not_finished(self):
        m = Match()
        assert m.is_finished is False

    def test_probability_normalization(self):
        p = Probability(home_win=0.6, draw=0.2, away_win=0.2)
        assert p.is_calibrated is True

    def test_probability_unnormalized(self):
        p = Probability(home_win=0.8, draw=0.2, away_win=0.2)
        assert p.is_calibrated is False
        normalized = p.normalize()
        assert abs(normalized.home_win + normalized.draw + normalized.away_win - 1.0) < 0.01

    def test_ranking_creation(self):
        ranking = Ranking(
            team_id=1,
            ranking_type="fifa",
            rank=1,
            points=1800.0,
            rank_date="2024-01-01",
        )
        assert ranking.rank == 1

    def test_prediction_defaults(self):
        pred = Prediction()
        assert pred.home_win_probability == 0.0
        assert pred.draw_probability == 0.0
        assert pred.away_win_probability == 0.0
        assert pred.confidence_score == 0.0


class TestValueObjects:
    def test_team_stats_creation(self):
        stats = TeamStats(
            match_id=1,
            team_id=1,
            is_home=True,
            goals=2,
            possession=60.0,
            ppda=8.5,
        )
        assert stats.goals == 2
        assert stats.possession == 60.0
        assert stats.ppda == 8.5

    def test_player_defaults(self):
        player = Player(name="Neymar")
        assert player.name == "Neymar"
        assert player.goals is None  # player stats, not player itself - player has no goals field

    def test_competition_with_type(self):
        from src.config.constants import CompetitionType
        comp = Competition(name="World Cup", type=CompetitionType.WORLD_CUP)
        assert comp.type == CompetitionType.WORLD_CUP
