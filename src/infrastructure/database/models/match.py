from sqlalchemy import (
    Column, Integer, String, Date, Time, DateTime, Float, ForeignKey, func,
    UniqueConstraint, Index
)

from src.infrastructure.database.models.base import Base


class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"))
    season = Column(String(20))
    stage = Column(String(50))
    round = Column(Integer)
    group_name = Column(String(10))
    match_date = Column(Date, nullable=False)
    match_time = Column(Time)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    home_score = Column(Integer)
    away_score = Column(Integer)
    home_goals_ht = Column(Integer)
    away_goals_ht = Column(Integer)
    home_xg = Column(Float)
    away_xg = Column(Float)
    venue = Column(String(200))
    city = Column(String(100))
    country = Column(String(100))
    stadium = Column(String(200))
    attendance = Column(Integer)
    temperature = Column(Float)
    humidity = Column(Integer)
    altitude = Column(Integer)
    weather_condition = Column(String(100))
    referee = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("competition_id", "home_team_id", "away_team_id", "match_date",
                         name="uq_match_competition_teams_date"),
        Index("idx_matches_date", "match_date"),
        Index("idx_matches_home", "home_team_id"),
        Index("idx_matches_away", "away_team_id"),
        Index("idx_matches_competition", "competition_id"),
    )
