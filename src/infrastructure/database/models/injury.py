from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func, Index

from src.infrastructure.database.models.base import Base


class InjuryModel(Base):
    __tablename__ = "injuries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    injury_type = Column(String(100))
    injury_area = Column(String(100))
    severity = Column(String(50))
    expected_return = Column(Date)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    status = Column(String(20), default="active")
    importance = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_injuries_team_status", "team_id", "status"),
    )
