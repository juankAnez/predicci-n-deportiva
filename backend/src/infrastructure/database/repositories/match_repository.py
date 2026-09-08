from datetime import date
from typing import List, Optional

from sqlalchemy import and_

from src.domain.entities import Match
from src.infrastructure.database.models import MatchModel
from src.infrastructure.database.repositories.base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    model_class = MatchModel

    def to_domain(self, model: MatchModel) -> Match:
        return Match(
            id=model.id,
            competition_id=model.competition_id,
            season=model.season,
            stage=model.stage,
            round=model.round,
            group_name=model.group_name,
            match_date=model.match_date,
            match_time=model.match_time,
            home_team_id=model.home_team_id,
            away_team_id=model.away_team_id,
            home_score=model.home_score,
            away_score=model.away_score,
            home_goals_ht=model.home_goals_ht,
            away_goals_ht=model.away_goals_ht,
            home_xg=model.home_xg,
            away_xg=model.away_xg,
            venue=model.venue,
            city=model.city,
            country=model.country,
            stadium=model.stadium,
            attendance=model.attendance,
            temperature=model.temperature,
            humidity=model.humidity,
            altitude=model.altitude,
            weather_condition=model.weather_condition,
            referee=model.referee,
        )

    def to_model(self, domain: Match) -> MatchModel:
        return MatchModel(
            id=domain.id,
            competition_id=domain.competition_id,
            season=domain.season,
            stage=domain.stage,
            round=domain.round,
            group_name=domain.group_name,
            match_date=domain.match_date,
            match_time=domain.match_time,
            home_team_id=domain.home_team_id,
            away_team_id=domain.away_team_id,
            home_score=domain.home_score,
            away_score=domain.away_score,
            home_goals_ht=domain.home_goals_ht,
            away_goals_ht=domain.away_goals_ht,
            home_xg=domain.home_xg,
            away_xg=domain.away_xg,
            venue=domain.venue,
            city=domain.city,
            country=domain.country,
            stadium=domain.stadium,
            attendance=domain.attendance,
            temperature=domain.temperature,
            humidity=domain.humidity,
            altitude=domain.altitude,
            weather_condition=domain.weather_condition,
            referee=domain.referee,
        )

    def get_by_team(self, team_id: int, limit: int = 10) -> List[Match]:
        models = (
            self.db.query(MatchModel)
            .filter(
                and_(
                    (MatchModel.home_team_id == team_id) | (MatchModel.away_team_id == team_id),
                    MatchModel.home_score.isnot(None),
                )
            )
            .order_by(MatchModel.match_date.desc())
            .limit(limit)
            .all()
        )
        return [self.to_domain(m) for m in models]

    def get_by_competition(self, competition_id: int) -> List[Match]:
        models = (
            self.db.query(MatchModel)
            .filter(MatchModel.competition_id == competition_id)
            .order_by(MatchModel.match_date)
            .all()
        )
        return [self.to_domain(m) for m in models]

    def get_between_dates(self, start: date, end: date) -> List[Match]:
        models = (
            self.db.query(MatchModel)
            .filter(MatchModel.match_date.between(start, end))
            .order_by(MatchModel.match_date)
            .all()
        )
        return [self.to_domain(m) for m in models]

    def get_upcoming(self, limit: int = 20) -> List[Match]:
        today = date.today()
        models = (
            self.db.query(MatchModel)
            .filter(MatchModel.match_date >= today, MatchModel.home_score.is_(None))
            .order_by(MatchModel.match_date)
            .limit(limit)
            .all()
        )
        return [self.to_domain(m) for m in models]

    def get_h2h(self, team1_id: int, team2_id: int, limit: int = 10) -> List[Match]:
        models = (
            self.db.query(MatchModel)
            .filter(
                and_(
                    (
                        (MatchModel.home_team_id == team1_id) & (MatchModel.away_team_id == team2_id)
                    ) | (
                        (MatchModel.home_team_id == team2_id) & (MatchModel.away_team_id == team1_id)
                    ),
                    MatchModel.home_score.isnot(None),
                )
            )
            .order_by(MatchModel.match_date.desc())
            .limit(limit)
            .all()
        )
        return [self.to_domain(m) for m in models]

    def get_team_matches_since(self, team_id: int, since_date: date) -> List[Match]:
        models = (
            self.db.query(MatchModel)
            .filter(
                and_(
                    (MatchModel.home_team_id == team_id) | (MatchModel.away_team_id == team_id),
                    MatchModel.match_date >= since_date,
                    MatchModel.home_score.isnot(None),
                )
            )
            .order_by(MatchModel.match_date.desc())
            .all()
        )
        return [self.to_domain(m) for m in models]

    def upsert(self, match: Match) -> Match:
        existing = (
            self.db.query(MatchModel)
            .filter(
                and_(
                    MatchModel.competition_id == match.competition_id,
                    MatchModel.home_team_id == match.home_team_id,
                    MatchModel.away_team_id == match.away_team_id,
                    MatchModel.match_date == match.match_date,
                )
            )
            .first()
        )
        if existing:
            for key, value in self.to_model(match).__dict__.items():
                if key != "_sa_instance_state" and key != "id" and value is not None:
                    setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return self.to_domain(existing)
        return self.create(match)
