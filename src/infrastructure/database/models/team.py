from sqlalchemy import Column, Integer, String, Date, DateTime, func

from src.infrastructure.database.models.base import Base


class TeamModel(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    full_name = Column(String(200))
    code = Column(String(3))
    country = Column(String(100))
    confederation = Column(String(50))
    founded_year = Column(Integer)
    logo_url = Column(String(500))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
