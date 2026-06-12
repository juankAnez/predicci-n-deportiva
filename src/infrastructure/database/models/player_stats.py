from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func, UniqueConstraint, Index

from src.infrastructure.database.models.base import Base


class PlayerStatsModel(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    minutes_played = Column(Integer)
    position = Column(String(30))
    rating = Column(Float)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    xg = Column(Float)
    xa = Column(Float)
    shots_total = Column(Integer, default=0)
    shots_on_target = Column(Integer, default=0)
    goals_per_shot = Column(Float)
    key_passes = Column(Integer, default=0)
    passes_total = Column(Integer, default=0)
    passes_completed = Column(Integer, default=0)
    passing_accuracy = Column(Float)
    progressive_passes = Column(Integer, default=0)
    assists_per_90 = Column(Float)
    goals_per_90 = Column(Float)
    dribbles_successful = Column(Integer, default=0)
    dribbles_attempted = Column(Integer, default=0)
    tackles = Column(Integer, default=0)
    interceptions = Column(Integer, default=0)
    clearances = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    fouls = Column(Integer, default=0)
    fouls_suffered = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    offsides = Column(Integer, default=0)
    recoveries = Column(Integer, default=0)
    aerials_won = Column(Integer, default=0)
    aerials_total = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint("match_id", "player_id", name="uq_player_stats_match_player"),
        Index("idx_player_stats_match", "match_id"),
        Index("idx_player_stats_player", "player_id"),
        Index("idx_player_stats_team", "team_id"),
    )
