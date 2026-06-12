from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, func, UniqueConstraint, Index

from src.infrastructure.database.models.base import Base


class RankingModel(Base):
    __tablename__ = "rankings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    ranking_type = Column(String(20), nullable=False)
    rank = Column(Integer, nullable=False)
    previous_rank = Column(Integer)
    points = Column(Float)
    change_points = Column(Float)
    rank_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint("team_id", "ranking_type", "rank_date", name="uq_ranking_team_type_date"),
        Index("idx_rankings_team_date", "team_id", "rank_date"),
        Index("idx_rankings_type_date", "ranking_type", "rank_date.desc()"),
    )
