from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func, Index

from src.infrastructure.database.models.base import Base


class SuspensionModel(Base):
    __tablename__ = "suspensions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"))
    reason = Column(String(200))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    matches_missed = Column(Integer)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_suspensions_team", "team_id"),
    )
