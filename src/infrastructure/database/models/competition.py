from sqlalchemy import Column, Integer, String, Date, DateTime, func, UniqueConstraint

from src.infrastructure.database.models.base import Base


class CompetitionModel(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    short_name = Column(String(50))
    type = Column(String(50))
    confederation = Column(String(50))
    season = Column(String(20))
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint("name", "season", name="uq_competition_name_season"),
    )
