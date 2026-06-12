from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, DateTime, func, UniqueConstraint, Index

from src.infrastructure.database.models.base import Base


class TeamStatsModel(Base):
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    is_home = Column(Boolean, nullable=False)
    goals = Column(Integer)
    xg = Column(Float)
    xga = Column(Float)
    shots_total = Column(Integer)
    shots_on_target = Column(Integer)
    shots_off_target = Column(Integer)
    shots_blocked = Column(Integer)
    corners = Column(Integer)
    fouls = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    possession = Column(Float)
    passes_total = Column(Integer)
    passes_completed = Column(Integer)
    passing_accuracy = Column(Float)
    progressive_passes = Column(Integer)
    progressive_carries = Column(Integer)
    deep_completions = Column(Integer)
    box_entries = Column(Integer)
    crosses = Column(Integer)
    crosses_accuracy = Column(Float)
    offsides = Column(Integer)
    tackles = Column(Integer)
    interceptions = Column(Integer)
    clearances = Column(Integer)
    blocks = Column(Integer)
    recoveries = Column(Integer)
    saves = Column(Integer)
    ppda = Column(Float)
    high_press_success = Column(Integer)
    territorial_possession = Column(Float)
    shot_conversion_rate = Column(Float)
    avg_shot_distance = Column(Float)
    expected_goals_on_target = Column(Float)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint("match_id", "team_id", name="uq_team_stats_match_team"),
        Index("idx_team_stats_match", "match_id"),
        Index("idx_team_stats_team", "team_id"),
    )
